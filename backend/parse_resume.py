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


def _find_phone(text: str) -> str:
    m = re.search(r'(?:\+?\d[\d\s\-().]{7,}\d)', text)
    candidate = m.group(0).strip() if m else ""
    # filter out things that look like years
    if candidate and len(re.sub(r'\D', '', candidate)) >= 7:
        return candidate
    return ""

def _find_twitter(text: str) -> str:
    m = re.search(r'(?:twitter\.com|x\.com)/[\w]+', text, re.IGNORECASE)
    return f"https://{m.group(0)}" if m else ""

def _find_portfolio(text: str) -> str:
    m = re.search(r'https?://(?!linkedin|github|twitter|x\.com|credly|certmetrics)[\w.-]+\.(?:io|com|dev|me|net)/[\w/.-]*', text)
    return m.group(0) if m else ""


def _split_sections(text: str) -> dict[str, str]:
    """
    Split resume text into named sections using common uppercase headings.
    Returns dict: {section_name: section_text}
    """
    section_re = re.compile(
        r"^(SUMMARY|PROFESSIONAL SUMMARY|EXPERIENCE|WORK EXPERIENCE|PROFESSIONAL EXPERIENCE|WORK HISTORY|"
        r"SKILLS|TECHNICAL SKILLS|CORE COMPETENCIES|"
        r"EDUCATION|ACADEMIC BACKGROUND|"
        r"CERTIFICATIONS?|LICENSES? & CERTIFICATIONS?|LICENSES? AND CERTIFICATIONS?|"
        r"PROJECTS?|ACHIEVEMENTS?|ACCOMPLISHMENTS?|"
        r"AWARDS?(?:\s*&\s*(?:RECOGNITION|HONORS?))?|HONORS?|REWARDS?|"
        r"SOFT SKILLS?|INTERPERSONAL SKILLS?|"
        r"LANGUAGES?|PUBLICATIONS?|VOLUNTEERING?|"
        r"TOP SKILLS|CONTACT)\s*:?\s*$",
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
    # Strip LinkedIn's "Contact" prefix if present
    name = ""
    for line in lines[:8]:
        cleaned = re.sub(r'^contact\s+', '', line.strip(), flags=re.IGNORECASE)
        if not re.search(r"[@/.]", cleaned) and 1 < len(cleaned.split()) <= 5:
            name = cleaned
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
        "github":    overrides.get("github") or _find_github(text),
        "phone":     overrides.get("phone") or _find_phone(text),
        "twitter":   overrides.get("twitter") or _find_twitter(text),
        "leetcode":  overrides.get("leetcode") or "",
        "hackerrank": overrides.get("hackerrank") or "",
        "portfolio": overrides.get("portfolio") or _find_portfolio(text),
        "credly":    "",
        "tagline1": "",
        "tagline2": "",
        "sub":      "",
        "heroBadges": [],
        "summary":  sections.get("SUMMARY", ""),
        "focus":    _parse_focus(text, sections.get("SUMMARY", "")),
        "skills":   _parse_skills(sections.get("SKILLS", sections.get("TECHNICAL SKILLS", ""))),
        "experience": _parse_experience(sections.get("EXPERIENCE", sections.get("WORK EXPERIENCE", sections.get("PROFESSIONAL EXPERIENCE", sections.get("WORK HISTORY", ""))))),
        "certifications": _parse_certifications(
            sections.get("CERTIFICATIONS", sections.get("LICENSES & CERTIFICATIONS", ""))
        ),
        "projects": _parse_projects(sections.get("PROJECTS", "")),
        "education": _parse_education(sections.get("EDUCATION", "")),
        "achievements": [],
        "extras": _parse_extras(sections),
    }

    return data


_EXTRAS_MAP = {
    # section heading (uppercase) → (display title, type)
    "ACCOMPLISHMENTS":           ("Accomplishments",        "list"),
    "ACHIEVEMENTS":              ("Achievements",           "list"),
    "AWARDS":                    ("Awards & Recognition",   "list"),
    "AWARDS & RECOGNITION":      ("Awards & Recognition",   "list"),
    "AWARDS & HONORS":           ("Awards & Honors",        "list"),
    "HONORS":                    ("Honors",                 "list"),
    "REWARDS":                   ("Rewards & Recognition",  "list"),
    "SOFT SKILLS":               ("Soft Skills",            "tags"),
    "INTERPERSONAL SKILLS":      ("Interpersonal Skills",   "tags"),
    "LANGUAGES":                 ("Languages",              "tags"),
    "LANGUAGE":                  ("Languages",              "tags"),
    "PUBLICATIONS":              ("Publications",           "list"),
    "PUBLICATION":               ("Publications",           "list"),
    "VOLUNTEERING":              ("Volunteering",           "list"),
}

def _parse_extras(sections: dict) -> list[dict]:
    """Build extras list from any recognised extra sections present in the resume."""
    extras = []
    for raw_key, text in sections.items():
        mapping = _EXTRAS_MAP.get(raw_key.upper())
        if not mapping or not text.strip():
            continue
        display_title, kind = mapping
        items = []
        for line in text.splitlines():
            line = line.strip().lstrip("-•·→✦►▶*").strip()
            if line and len(line) > 2:
                items.append(line)
        if items:
            extras.append({"title": display_title, "items": items, "type": kind})
    return extras


def _parse_focus(full_text: str, summary: str) -> list[str]:
    """Extract focus points — lines starting with →, ✦, or similar bullet styles."""
    focus_items = []
    arrow_re = re.compile(r'^[→✦►▶•]\s*(.+)', re.UNICODE)
    for line in full_text.splitlines():
        m = arrow_re.match(line.strip())
        if m:
            item = m.group(1).strip()
            if 10 < len(item) < 120:
                focus_items.append(item)
    return focus_items[:6]  # cap at 6 items


def _parse_experience_piped(text: str) -> list[dict]:
    """
    Parse 'Title | Company | Date' format — common in modern resume templates.
    Lines starting with whitespace or explicit bullet chars are bullets.
    Unwrapped continuation lines are merged into the previous bullet.
    """
    pipe_re = re.compile(r'^(.+?)\s*\|\s*(.+?)\s*\|\s*(.+)$')
    bullet_char_re = re.compile(r'^[•\-*→✦►▶]\s*(.+)')

    raw_lines = text.splitlines()
    entries = []
    current = None

    for raw in raw_lines:
        stripped = raw.strip()
        if not stripped:
            continue

        m = pipe_re.match(stripped)
        if m:
            if current:
                entries.append(current)
            period = m.group(3).strip()
            current = {
                "company": m.group(2).strip(),
                "companyDesc": "",
                "period": period,
                "roles": [{"title": m.group(1).strip(), "period": period, "stack": "", "bullets": []}],
            }
            continue

        if current is None:
            continue

        role = current["roles"][-1]
        bm = bullet_char_re.match(stripped)
        leading_space = raw and raw[0] in (' ', '\t')

        if bm:
            role["bullets"].append(bm.group(1).strip())
        elif leading_space:
            # Leading whitespace = new bullet in this format
            role["bullets"].append(stripped)
        elif role["bullets"]:
            # No leading space, no bullet char = continuation of last bullet
            role["bullets"][-1] = role["bullets"][-1].rstrip() + ' ' + stripped
        else:
            # First text after header, no bullets yet — treat as first bullet
            role["bullets"].append(stripped)

    if current:
        entries.append(current)

    return entries


def _parse_projects(text: str) -> list[dict]:
    """
    Best-effort project parser. Handles formats like:
      Project Name | Tech, Stack | optional-link
      Project Name
      Description / bullets
    """
    if not text.strip():
        return []

    pipe_re = re.compile(r'^(.+?)\s*\|\s*(.+?)(?:\s*\|\s*(.+))?$')
    bullet_re = re.compile(r'^[•\-*→✦►▶]\s*(.+)')
    url_re = re.compile(r'https?://\S+')

    raw_lines = text.splitlines()
    projects = []
    current = None

    def flush():
        if current and current.get("name"):
            projects.append(current)

    # Matches "Technologies: ..." / "Tech Stack: ..." / "Stack: ..." / "Tools: ..."
    tech_prefix_re = re.compile(
        r'^(?:Technologies|Tech(?:nology)?(?:\s+Stack)?|Stack|Tools?)\s*:\s*(.+)',
        re.IGNORECASE,
    )

    for raw in raw_lines:
        line = raw.strip()
        if not line:
            continue

        # "Technologies: X, Y, Z" — attach to current project as stack
        tech_m = tech_prefix_re.match(line)
        if tech_m:
            if current is not None and not current["stack"]:
                stack_str = tech_m.group(1).strip()
                current["stack"] = [s.strip() for s in re.split(r'[,·]', stack_str) if s.strip()]
            continue

        m = pipe_re.match(line)
        if m:
            flush()
            stack_str = m.group(2).strip() if m.group(2) else ""
            link = m.group(3).strip() if m.group(3) else ""
            if url_re.search(stack_str):
                link = url_re.search(stack_str).group(0)
                stack_str = url_re.sub("", stack_str).strip(" |,")
            current = {
                "name": m.group(1).strip(),
                "desc": "",
                "stack": [s.strip() for s in re.split(r'[,·]', stack_str) if s.strip()],
                "github": link or "",
                "status": "done",
                "academic": False,
            }
            continue

        bm = bullet_re.match(line)
        if bm:
            if current is None:
                continue
            if not current["desc"]:
                current["desc"] = bm.group(1).strip()
            continue

        # Short non-bullet line with no lowercase-heavy content = project name
        if len(line) < 80 and not re.search(r'^[a-z]', line) and not url_re.search(line):
            flush()
            current = {"name": line, "desc": "", "stack": [], "github": "", "status": "done", "academic": False}
        elif current:
            if not current["desc"]:
                current["desc"] = line
            elif url_re.search(line):
                current["github"] = url_re.search(line).group(0)

    flush()
    return projects


def _parse_experience(text: str) -> list[dict]:
    """
    Parse experience — handles three formats:
    1. Pipe: "Title | Company | Date" (modern resume templates)
    2. LinkedIn PDF: Company → Title → Date (Duration) → Location → Bullets
    3. Traditional: Company + Date on same line, Title below, bullets
    """
    if not text.strip():
        return []

    # Detect pipe format and delegate
    if re.search(r'^.+\|.+\|.+', text, re.MULTILINE):
        return _parse_experience_piped(text)

    date_re = re.compile(
        r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|'
        r'Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
        r'\s+\d{4}|\b\d{4}\s*[-–—]\s*(?:\d{4}|Present|Current|Now)'
        r'|\b\d{1,2}/\d{2,4}\s*[-–—]\s*(?:\d{1,2}/\d{2,4}|Present|Current|Now)'
        r'|\b\d{1,2}/\d{2,4}',
        re.IGNORECASE
    )
    period_re = re.compile(
        r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}|\d{4})'
        r'\s*[-–—]\s*'
        r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}|\d{4}|Present|Current|Now)',
        re.IGNORECASE
    )
    bullet_re = re.compile(r'^[-•*·→✦►]\s*(.+)')
    duration_re = re.compile(r'^\(?\s*\d+\s+(?:year|month|yr|mo)', re.IGNORECASE)
    # Patterns that indicate a location line (short, no role keywords)
    role_keywords = re.compile(r'\b(engineer|developer|analyst|manager|lead|architect|designer|'
                               r'scientist|director|head|vp|consultant|intern|associate|senior|junior|'
                               r'staff|principal|data|software|product)\b', re.IGNORECASE)

    def has_date(line):
        return bool(date_re.search(line))

    def extract_period(line):
        m = period_re.search(line)
        if m:
            period = m.group(0)
            # strip trailing duration like "(1 year 3 months)"
            period = re.sub(r'\s*\([\d\s\wyears months]+\)\s*$', '', period, flags=re.IGNORECASE).strip()
            return period
        return ""

    def is_location(line):
        """Heuristic: short line, no role keywords, looks like a city/country."""
        if len(line.split()) > 5:
            return False
        if role_keywords.search(line):
            return False
        if re.search(r',\s*[A-Z]', line):  # "City, Country" pattern
            return True
        return False

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    entries = []
    current_company = None
    current_roles = []
    current_role = None

    def flush_role():
        nonlocal current_role
        if current_role and (current_role.get("title") or current_role.get("bullets")):
            current_roles.append(current_role)
        current_role = None

    def flush_company():
        nonlocal current_company, current_roles
        flush_role()
        if current_company and current_roles:
            # Clean up: filter roles that look like location/duration artifacts
            valid_roles = [r for r in current_roles
                           if r.get("bullets") or (r.get("title") and role_keywords.search(r.get("title", "")))]
            if not valid_roles:
                valid_roles = current_roles[:1]  # keep at least the first
            entries.append({
                "company": current_company,
                "companyDesc": "",
                "period": valid_roles[0].get("period", "") if valid_roles else "",
                "roles": valid_roles,
            })
        current_company = None
        current_roles = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Skip pure duration lines like "(1 year 3 months)"
        if duration_re.match(line):
            i += 1
            continue

        # Bullet line
        bullet_m = bullet_re.match(line)
        if bullet_m:
            if current_role is None and current_company:
                current_role = {"title": "", "period": "", "stack": "", "bullets": []}
            if current_role is not None:
                current_role["bullets"].append(bullet_m.group(1).strip())
            i += 1
            continue

        # Stack/tech line
        if re.match(r'^(stack|tech(?:nologies)?|tools?)\s*:', line, re.IGNORECASE):
            if current_role:
                current_role["stack"] = re.sub(r'^[^:]+:\s*', '', line).strip()
            i += 1
            continue

        # Line with date
        if has_date(line):
            period = extract_period(line)
            if current_role is not None and not current_role.get("period"):
                current_role["period"] = period
            elif current_role is not None and current_role.get("period"):
                # Another date line → new role
                flush_role()
                current_role = {"title": "", "period": period, "stack": "", "bullets": []}
            elif current_company is not None:
                # Date after company line (LinkedIn: company → title → date)
                if current_role is None:
                    current_role = {"title": "", "period": period, "stack": "", "bullets": []}
                else:
                    current_role["period"] = period
            else:
                current_company = "Unknown"
                current_role = {"title": "", "period": period, "stack": "", "bullets": []}
            i += 1
            continue

        # Location line — skip
        if is_location(line):
            i += 1
            continue

        # Plain text — company name, job title, or description
        if current_role is not None and current_role.get("bullets"):
            # Currently in bullets, plain line = new company starts
            flush_company()
            current_company = line
        elif current_role is not None and not current_role.get("title") and role_keywords.search(line):
            # Role exists but no title — this is the title
            current_role["title"] = line
        elif current_role is not None and current_role.get("title"):
            # Has title already — could be new company or description text
            if role_keywords.search(line):
                # Looks like a new role title at same company
                flush_role()
                current_role = {"title": line, "period": "", "stack": "", "bullets": []}
            else:
                flush_company()
                current_company = line
        elif current_company is not None and current_role is None:
            # Have company, no role — this is the title
            current_role = {"title": line, "period": "", "stack": "", "bullets": []}
        else:
            # No company yet, or ambiguous
            if current_company is None:
                current_company = line
            else:
                flush_company()
                current_company = line

        i += 1

    flush_company()

    # Post-process: remove entries where company is a duration or single word artifact
    entries = [e for e in entries
               if e["company"] and not duration_re.match(e["company"])
               and not re.match(r'^[\d\s\-–—()]+$', e["company"])]

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
        if not line:
            continue
        # Single line with multiple certs separated by · or | (common in generated PDFs)
        if ('·' in line or ' | ' in line) and 'http' not in line:
            parts = re.split(r'\s*[·|]\s*', line)
        elif ';' in line and 'http' not in line:
            parts = re.split(r'\s*;\s*', line)
        else:
            parts = [line]
        for p in parts:
            p = p.strip().lstrip("-•·").strip()
            if p:
                certs.append({"name": p, "icon": "📜", "featured": False, "link": None})
    return certs


def _parse_education(text: str) -> list[dict]:
    entries = []
    degree_re = re.compile(
        r'(?:^|\s)(B\.?Tech|M\.?Tech|B\.?E\b\.?|M\.?E\b\.?|'
        r'B\.?Sc\b\.?|M\.?Sc\b\.?|M\.?S\b\.?|B\.?S\b\.?|'
        r'B\.?A\b\.?|M\.?A\b\.?|B\.?Com\b|MBA\b|LLB\b|B\.?Des\b|'
        r'Ph\.?D\.?|Bachelors?|Masters?)',
        re.IGNORECASE
    )
    cgpa_re = re.compile(r'(?:CGPA|GPA)\s*[:\-·]?\s*([0-9]+(?:\.[0-9]+)?)', re.IGNORECASE)
    period_re = re.compile(r'\b(\d{4})\s*[-–—]\s*(\d{4}|Present)\b', re.IGNORECASE)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    i = 0
    while i < len(lines):
        line = lines[i]
        if degree_re.search(line):
            # Degree line may include the period inline (e.g. "M.Tech — CSE 2016 – 2018")
            period_m = period_re.search(line)
            period = period_m.group(0) if period_m else ""
            degree = re.sub(r'\s*\d{4}\s*[-–—]\s*(?:\d{4}|Present)', '', line).strip()

            # Next line(s): school, CGPA, notes
            school = ""
            cgpa = ""
            notes = []
            j = i + 1
            while j < len(lines) and not degree_re.search(lines[j]):
                l = lines[j]
                cgpa_m = cgpa_re.search(l)
                if cgpa_m and not cgpa:
                    cgpa = cgpa_m.group(1)
                    school = school or re.sub(r'\s*·?\s*CGPA.*$', '', l, flags=re.IGNORECASE).strip()
                elif not school and not degree_re.search(l):
                    school = l
                elif school and l and not cgpa_m:
                    notes.append(l)
                j += 1

            entries.append({
                "degree": degree,
                "school": school,
                "period": period,
                "cgpa":   cgpa,
                "notes":  notes[:2],
            })
            i = j
        else:
            i += 1
    return entries
