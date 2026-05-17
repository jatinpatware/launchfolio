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
    return bool(config.get("api_key") and config.get("model"))


def call_llm(prompt: str, config: dict) -> str:
    """
    Send prompt to the configured provider and return the raw response text.
    Raises ValueError for unknown providers.
    """
    provider = config.get("provider", "anthropic").lower()
    model    = config["model"]
    api_key  = config["api_key"]

    if provider == "anthropic":
        return _call_anthropic(prompt, model, api_key)
    elif provider == "openai":
        return _call_openai(prompt, model, api_key)
    else:
        raise ValueError(f"Unknown provider '{provider}'. Supported: anthropic, openai")


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


def _call_openai(prompt: str, model: str, api_key: str) -> str:
    try:
        import openai
    except ImportError:
        raise ImportError("Run: pip install openai")

    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
    )
    return response.choices[0].message.content


def extract_json(text: str) -> dict:
    """Extract JSON object from LLM response (handles markdown code fences)."""
    # Strip ```json ... ``` fences if present
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip().rstrip("`").strip()
    return json.loads(text)
