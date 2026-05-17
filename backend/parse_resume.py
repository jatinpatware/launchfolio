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
        r"^(SUMMARY|PROFESSIONAL SUMMARY|EXPERIENCE|WORK EXPERIENCE|PROFESSIONAL EXPERIENCE|WORK HISTORY|"
        r"SKILLS|TECHNICAL SKILLS|CORE COMPETENCIES|"
        r"EDUCATION|ACADEMIC BACKGROUND|"
        r"CERTIFICATIONS?|LICENSES? & CERTIFICATIONS?|"
        r"PROJECTS|ACHIEVEMENTS?|ACCOMPLISHMENTS?)\s*$",
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
        "experience": _parse_experience(sections.get("EXPERIENCE", sections.get("WORK EXPERIENCE", sections.get("PROFESSIONAL EXPERIENCE", sections.get("WORK HISTORY", ""))))),
        "certifications": _parse_certifications(sections.get("CERTIFICATIONS", "")),
        "projects": [],
        "education": _parse_education(sections.get("EDUCATION", "")),
        "achievements": [],
    }

    return data


def _parse_experience(text: str) -> list[dict]:
    """
    Heuristic experience parser. Handles common resume formats:
    - Company on one line with dates, title on next line
    - Title | Company | Dates
    - Bullets starting with - or •
    """
    if not text.strip():
        return []

    date_re = re.compile(
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|'
        r'June|July|August|September|October|November|December)\s+\d{4}'
        r'|\d{4}\s*[-–—]\s*(\d{4}|Present|Current|Now)',
        re.IGNORECASE
    )
    bullet_re = re.compile(r'^[-•*·]\s+(.+)')

    lines = [l.rstrip() for l in text.splitlines()]
    entries = []
    current_company = None
    current_roles = []
    current_role = None

    def flush_role():
        nonlocal current_role
        if current_role and current_company is not None:
            current_roles.append(current_role)
            current_role = None

    def flush_company():
        nonlocal current_company, current_roles
        if current_company is not None and current_roles:
            entries.append({
                "company": current_company,
                "companyDesc": "",
                "period": current_roles[0].get("period", ""),
                "roles": current_roles,
            })
        current_company = None
        current_roles = []

    for line in lines:
        if not line.strip():
            continue

        bullet_m = bullet_re.match(line.strip())
        has_date = bool(date_re.search(line))

        if bullet_m:
            if current_role:
                current_role["bullets"].append(bullet_m.group(1).strip())
            continue

        # Line with a date — likely a role/company line
        if has_date:
            # Extract date range
            period_m = re.search(
                r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}|'
                r'\d{4})\s*[-–—]\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}|'
                r'\d{4}|Present|Current|Now)',
                line, re.IGNORECASE
            )
            period = period_m.group(0).strip() if period_m else ""
            title_part = date_re.sub('', line).strip().strip('|-').strip()

            if current_company is None:
                # First date line — this is company + date or title + date
                flush_role()
                current_company = title_part or "Unknown Company"
                current_role = {"title": "", "period": period, "stack": "", "bullets": []}
            else:
                # Subsequent date line — new role at same or new company
                flush_role()
                if title_part and title_part.lower() not in current_company.lower():
                    # Looks like a new company
                    if len(entries) > 0 or current_roles:
                        flush_company()
                        current_company = title_part
                current_role = {"title": title_part, "period": period, "stack": "", "bullets": []}
        elif line.strip().lower().startswith("stack:") or line.strip().lower().startswith("tech:"):
            if current_role:
                current_role["stack"] = re.sub(r'^(stack|tech)\s*:\s*', '', line.strip(), flags=re.IGNORECASE)
        else:
            # No date, no bullet — could be title or company name
            if current_role is not None and not current_role["title"]:
                current_role["title"] = line.strip()
            elif current_role is not None and current_role["bullets"]:
                # After bullets, a plain line might be a new role title
                flush_role()
                current_role = {"title": line.strip(), "period": "", "stack": "", "bullets": []}
            elif current_company is None:
                current_company = line.strip()

    flush_role()
    flush_company()

    # Clean up: if role title is empty and company isn't, use company as title
    for entry in entries:
        for role in entry["roles"]:
            if not role["title"]:
                role["title"] = entry["company"]

    return entries


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
