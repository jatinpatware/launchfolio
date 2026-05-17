"""
AI-powered parser — uses an LLM to extract and merge structured resume data.

Takes raw resume text + enrichment notes in one shot.
The LLM understands context, writes polished bullets, and merges intelligently.
Enrichment text always takes precedence over the resume for overlapping fields.
"""

import re
from llm import call_llm, extract_json

SCHEMA_DESCRIPTION = """
{
  "name": "string",
  "title": "string — current job title",
  "email": "string",
  "location": "string",
  "linkedin":   "string — full URL",
  "github":     "string — full URL",
  "twitter":    "string — full URL or empty string",
  "leetcode":   "string — full URL or empty string",
  "hackerrank": "string — full URL or empty string",
  "credly":     "string — full URL or empty string",
  "portfolio":  "string — full URL or empty string",
  "phone":      "string or empty string",
  "tagline1": "string — bold punchy statement about their professional identity",
  "tagline2": "string — italic supporting line, e.g. 'Designing systems that scale.'",
  "sub": "string — one-liner stat summary, e.g. '8+ Years · Petabyte Scale · Real-Time Pipelines'",
  "heroBadges": ["array of 8-12 key technologies/skills for hero section"],
  "summary": "string — 3-4 sentence professional summary",
  "focus": ["array of 4-6 bullet strings describing what this person focuses on"],
  "skills": [
    { "category": "string", "items": ["array of skill strings"] }
  ],
  "experience": [
    {
      "company": "string — full legal/official company name",
      "companyDesc": "string — one-line company description",
      "period": "string — e.g. 'Jan 2022 – Present'",
      "roles": [
        {
          "title": "string",
          "period": "string",
          "stack": "string — technologies separated by · ",
          "bullets": ["array of achievement bullet strings, use <strong> tags for numbers/impact"]
        }
      ]
    }
  ],
  "certifications": [
    { "name": "string", "icon": "string — one emoji", "featured": false, "link": "string or null" }
  ],
  "projects": [
    { "name": "string", "desc": "string", "stack": ["strings"], "status": "coming-soon or live", "github": "string or null" }
  ],
  "education": [
    { "degree": "string", "school": "string", "period": "string", "cgpa": "string", "notes": ["strings"] }
  ],
  "achievements": ["array of strings"],
  "extras": [
    { "title": "string — e.g. Accomplishments, Soft Skills, Languages", "type": "list or tags", "items": ["strings"] }
  ]
}
"""


_MD_BOLD_RE = re.compile(r'\*{1,2}(.*?)\*{1,2}')
_STRING_FIELDS = {
    "name", "title", "email", "location", "linkedin", "github", "twitter",
    "leetcode", "hackerrank", "credly", "portfolio", "phone",
    "tagline1", "tagline2", "sub", "summary",
}

def _clean_strings(data: dict) -> dict:
    """Strip markdown bold/italic asterisks from top-level string fields."""
    for key in _STRING_FIELDS:
        if isinstance(data.get(key), str):
            data[key] = _MD_BOLD_RE.sub(r'\1', data[key]).strip()
    return data


def score_response(data: dict) -> tuple[int, list[str]]:
    """
    Score 0-100 based on how complete the parsed data is.
    Returns (score, list_of_issues).
    """
    score = 100
    issues = []

    for field in ["name", "title", "tagline1", "summary"]:
        if not data.get(field, "").strip():
            issues.append(f"missing {field}")
            score -= 15

    exp = data.get("experience", [])
    if not exp:
        issues.append("no experience entries")
        score -= 25
    else:
        total_bullets = sum(
            len(r.get("bullets", []))
            for e in exp
            for r in e.get("roles", [])
        )
        if total_bullets == 0:
            issues.append("experience has no bullets")
            score -= 15

    if not data.get("skills", []):
        issues.append("no skills section")
        score -= 10

    if len(data.get("heroBadges", [])) < 4:
        issues.append("too few hero badges")
        score -= 5

    if not data.get("education", []):
        issues.append("no education")
        score -= 5

    return max(0, score), issues


def parse_with_ai(resume_text: str, enrichment_text: str, config: dict) -> dict:
    """
    Use an LLM to extract and merge structured data from resume + enrichment.
    Returns a dict matching the data.js schema.
    """
    sections = []

    if resume_text.strip():
        sections.append(f"## RESUME\n{resume_text.strip()}")

    if enrichment_text.strip():
        sections.append(
            f"## ENRICHMENT (recent updates — takes precedence over resume)\n"
            f"{enrichment_text.strip()}"
        )

    if not sections:
        return {"data": {}, "score": 0, "issues": ["no content provided"]}

    prompt = f"""You are helping a software engineer build their professional portfolio.

Extract structured data from the content below and return a single JSON object matching the schema exactly.

Rules:
- Enrichment content takes precedence over resume for any overlapping fields
- Write polished, specific bullet points — keep numbers and impact metrics where present
- Use <strong>metric</strong> HTML tags around numbers and key achievements in bullets
- For tagline1: bold, punchy professional identity statement (plain text only — no asterisks or markdown)
- For tagline2: short supporting line (plain text only — no asterisks or markdown)
- For heroBadges: pick 8-12 most relevant technologies the person actually uses
- For skills: group logically (Core, Cloud & Infra, Streaming, AI/LLM, etc.)
- If a field cannot be determined from the content, use an empty string or empty array
- Return ONLY valid JSON — no explanation, no markdown fences

Schema:
{SCHEMA_DESCRIPTION}

Content:
{chr(10).join(sections)}

Return the JSON object now:"""

    raw = call_llm(prompt, config)
    data = extract_json(raw)
    data = _clean_strings(data)
    score, issues = score_response(data)
    return {"data": data, "score": score, "issues": issues}
