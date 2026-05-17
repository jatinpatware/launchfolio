"""
LLM abstraction layer — supports Anthropic and OpenAI.

Usage:
    from llm import call_llm, is_ai_enabled

    if is_ai_enabled(config):
        result = call_llm(prompt, config)
    else:
        # fall back to regex path
"""

import json


def is_ai_enabled(config: dict) -> bool:
    provider = config.get("provider", "").lower()
    if provider == "ollama":
        return bool(config.get("model"))
    return bool(config.get("api_key") and config.get("model"))


def call_llm(prompt: str, config: dict) -> str:
    """
    Send prompt to the configured provider and return the raw response text.
    Raises ValueError for unknown providers.
    """
    provider = config.get("provider", "anthropic").lower()
    model    = config["model"]
    api_key  = config.get("api_key", "")

    if provider == "anthropic":
        return _call_anthropic(prompt, model, api_key)
    elif provider == "openai":
        return _call_openai_compat(prompt, model, api_key, "https://api.openai.com/v1")
    elif provider == "google":
        return _call_google(prompt, model, api_key)
    elif provider == "deepseek":
        return _call_openai_compat(prompt, model, api_key, "https://api.deepseek.com")
    elif provider == "groq":
        return _call_openai_compat(prompt, model, api_key, "https://api.groq.com/openai/v1")
    elif provider == "ollama":
        return _call_openai_compat(prompt, model, api_key or "ollama", "http://localhost:11434/v1")
    else:
        raise ValueError(
            f"Unknown provider '{provider}'. "
            f"Supported: anthropic, openai, google, deepseek, groq, ollama"
        )


def _call_anthropic(prompt: str, model: str, api_key: str) -> str:
    try:
        import anthropic
    except ImportError:
        raise ImportError("Run: pip install anthropic")

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def _call_openai_compat(prompt: str, model: str, api_key: str, base_url: str) -> str:
    """OpenAI-compatible chat completions endpoint (OpenAI, DeepSeek, Groq, Ollama)."""
    try:
        import openai
    except ImportError:
        raise ImportError("Run: pip install openai")

    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    kwargs = dict(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
    )
    if "11434" in base_url:
        # Force JSON output and tune for better consistency with local models
        kwargs["response_format"] = {"type": "json_object"}
        kwargs["temperature"] = 0.1
        kwargs["extra_body"] = {"num_ctx": 8192}
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


def _call_google(prompt: str, model: str, api_key: str) -> str:
    try:
        import google.generativeai as genai
    except ImportError:
        raise ImportError("Run: pip install google-generativeai")

    genai.configure(api_key=api_key)
    m = genai.GenerativeModel(model)
    response = m.generate_content(prompt)
    return response.text


def extract_json(text: str) -> dict:
    """Extract JSON object from LLM response (handles markdown fences and preamble)."""
    original = text
    text = text.strip()

    # Strip ```json ... ``` or ``` ... ``` fences
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            candidate = part.lstrip("json").strip()
            if candidate.startswith("{"):
                text = candidate
                break

    # Find the first { and last } in case the model added preamble/postamble
    start = text.find("{")
    end   = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]

    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        preview = original[:300].replace("\n", " ")
        raise ValueError(
            f"LLM did not return valid JSON. Parse error: {e}. "
            f"Raw response (first 300 chars): {preview!r}"
        ) from e
