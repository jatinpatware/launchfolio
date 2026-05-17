"""
Resume parser — extracts structured data from a PDF resume using pdfplumber.

Best-effort: resumes vary wildly. The output is a dict matching the ResumeData
schema. Fields that can't be confidently extracted are left empty for the user
to fill in via the web UI or by editing data.js directly.
"""

import re
import pdfplumber
from models import ResumeData, Company, Role, Education, Certification, SkillGroup


# ── Helpers ──────────────────────────────────────────────────────────────────

def _extract_text(pdf_path: str) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


def _find_email(text: str) -> str:
    m = re.search(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", text)
    return m.group(0) if m else ""


def _find_linkedin(text: str) -> str:
    m = re.search(r"linkedin\.com/in/[\w-]+", text, re.IGNORECASE)
    return f"https://{m.group(0)}" if m else ""


def _find_github(text: str) -> str:
    m = re.search(r"github\.com/[\w-]+", text, re.IGNORECASE)
    return f"https://{m.group(0)}" if m else ""


def _split_sections(text: str) -> dict[str, str]:
    """
    Split resume text into named sections using common uppercase headings.
    Returns dict: {section_name: section_text}
    """
    section_re = re.compile(
        r"^(SUMMARY|EXPERIENCE|WORK EXPERIENCE|SKILLS|TECHNICAL SKILLS|"
        r"EDUCATION|CERTIFICATIONS|PROJECTS|ACHIEVEMENTS?)\s*$",
        re.MULTILINE | re.IGNORECASE,
    )
    matches = list(section_re.finditer(text))
    sections: dict[str, str] = {}
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections[m.group(1).upper()] = text[start:end].strip()
    return sections


# ── Public API ────────────────────────────────────────────────────────────────

def parse_raw(raw_text: str, overrides: dict | None = None) -> dict:
    """Parse from pasted raw text instead of a PDF file."""
    return _build_data(raw_text, overrides)


def parse(pdf_path: str, overrides: dict | None = None) -> dict:
    """Parse a PDF resume."""
    text = _extract_text(pdf_path)
    return _build_data(text, overrides)


def _build_data(text: str, overrides: dict | None = None) -> dict:
    """Shared logic for both PDF and raw-text paths."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    sections = _split_sections(text)
    overrides = overrides or {}

    # Name: first non-empty line that isn't an email/URL
    name = ""
    for line in lines[:5]:
        if not re.search(r"[@/.]", line) and len(line.split()) <= 5:
            name = line
            break

    # Title: line after name that looks like a job title
    title = ""
    if name and name in text:
        idx = lines.index(name) if name in lines else -1
        if idx >= 0 and idx + 1 < len(lines):
            title = lines[idx + 1]

    data = {
        "name":     overrides.get("name") or name,
        "title":    overrides.get("title") or title,
        "email":    overrides.get("email") or _find_email(text),
        "location": overrides.get("location") or "",
        "linkedin": overrides.get("linkedin") or _find_linkedin(text),
        "github":   overrides.get("github") or _find_github(text),
        "portfolio": "",
        "credly":   "",
        "tagline1": "",
        "tagline2": "",
        "sub":      "",
        "heroBadges": [],
        "summary":  sections.get("SUMMARY", ""),
        "focus":    [],
        "skills":   _parse_skills(sections.get("SKILLS", sections.get("TECHNICAL SKILLS", ""))),
        "experience": [],   # TODO: structured experience parsing
        "certifications": _parse_certifications(sections.get("CERTIFICATIONS", "")),
        "projects": [],
        "education": _parse_education(sections.get("EDUCATION", "")),
        "achievements": [],
    }

    return data


def _parse_skills(text: str) -> list[dict]:
    """
    Parse skill lines like 'Category: skill1, skill2, skill3'
    """
    groups = []
    for line in text.splitlines():
        if ":" in line:
            cat, _, items_str = line.partition(":")
            items = [i.strip() for i in re.split(r"[,·]", items_str) if i.strip()]
            if items:
                groups.append({"category": cat.strip(), "items": items})
    return groups


def _parse_certifications(text: str) -> list[dict]:
    certs = []
    for line in text.splitlines():
        line = line.strip().lstrip("-•·").strip()
        if line:
            certs.append({"name": line, "icon": "📜", "featured": False, "link": None})
    return certs


def _parse_education(text: str) -> list[dict]:
    entries = []
    # Look for degree lines — heuristic: lines containing common degree keywords
    degree_re = re.compile(r"(B\.?[A-Z]\.?|M\.?[A-Z]\.?|Ph\.?D|Bachelor|Master|MBA)", re.IGNORECASE)
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if degree_re.search(lines[i]):
            entries.append({
                "degree": lines[i].strip(),
                "school": lines[i + 1].strip() if i + 1 < len(lines) else "",
                "period": "",
                "cgpa":   "",
                "notes":  [],
            })
        i += 1
    return entries
