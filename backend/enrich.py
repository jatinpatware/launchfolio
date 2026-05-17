"""
Enrichment merger — takes base data (from PDF parse) and raw enrichment text
(recent updates the user typed in) and merges them.

Strategy:
  - Scalar fields (name, title, email, etc.): enrichment wins if non-empty
  - List fields (heroBadges, skills items): union — enrichment adds to, not replaces
  - Experience: if enrichment mentions a new role/company, prepend it
  - Certifications: new ones found in enrichment are appended
  - Summary: enrichment wins if provided (it's usually more current)
"""

import re


def merge(base: dict, enrichment_text: str, overrides: dict) -> dict:
    """
    Merge base (parsed PDF data), enrichment_text (user's raw notes), and
    explicit form overrides into a single data dict.

    Priority: overrides > enrichment > base (PDF)
    """
    if not enrichment_text.strip():
        return _apply_overrides(base, overrides)

    enriched = _parse_enrichment(enrichment_text, base)
    merged = _deep_merge(base, enriched)
    return _apply_overrides(merged, overrides)


def _apply_overrides(data: dict, overrides: dict) -> dict:
    """Explicit form fields always win."""
    result = dict(data)
    for key, val in overrides.items():
        if val:  # only override if the user actually typed something
            if key == "heroBadges" and isinstance(val, list):
                # Merge badge lists rather than replacing
                existing = set(result.get("heroBadges", []))
                result["heroBadges"] = list(existing | set(val))
            else:
                result[key] = val
    return result


def _deep_merge(base: dict, enriched: dict) -> dict:
    result = dict(base)
    for key, val in enriched.items():
        if not val:
            continue
        if isinstance(val, list) and isinstance(result.get(key), list):
            # Merge lists — enriched items go first (more recent)
            result[key] = _merge_lists(key, enriched[key], base.get(key, []))
        elif val:
            result[key] = val
    return result


def _merge_lists(key: str, enriched: list, base: list) -> list:
    """For most lists: prepend enriched items that aren't already present."""
    if key == "experience":
        # Prepend new companies/roles from enrichment
        base_companies = {e.get("company", "").lower() for e in base}
        new = [e for e in enriched if e.get("company", "").lower() not in base_companies]
        return new + base
    elif key == "certifications":
        base_names = {c.get("name", "").lower() for c in base}
        new = [c for c in enriched if c.get("name", "").lower() not in base_names]
        return base + new  # new certs at the end
    elif key == "heroBadges":
        # Union, preserve order
        seen = set()
        result = []
        for item in enriched + base:
            if item.lower() not in seen:
                seen.add(item.lower())
                result.append(item)
        return result
    elif key == "skills":
        # Merge by category
        base_by_cat = {sg.get("category", "").lower(): sg for sg in base}
        result = list(base)
        for sg in enriched:
            cat = sg.get("category", "").lower()
            if cat in base_by_cat:
                # Add new items to existing category
                existing_items = set(i.lower() for i in base_by_cat[cat].get("items", []))
                new_items = [i for i in sg.get("items", []) if i.lower() not in existing_items]
                base_by_cat[cat]["items"] = base_by_cat[cat]["items"] + new_items
            else:
                result.append(sg)
        return result
    else:
        # Default: union with enriched first
        seen = set()
        out = []
        for item in enriched + base:
            key_val = str(item).lower()
            if key_val not in seen:
                seen.add(key_val)
                out.append(item)
        return out


def _parse_enrichment(text: str, base: dict) -> dict:
    """
    Best-effort extraction from free-form enrichment text.
    Looks for: new roles, new certs (credly URLs), new skills, summary updates.
    """
    result: dict = {}
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    # Certifications: lines with credly/certmetrics URLs
    new_certs = []
    for line in lines:
        cert_url = _extract_cert_url(line)
        if cert_url:
            cert_name = _clean_cert_name(re.sub(r'https?://\S+', '', line))
            if cert_name:
                new_certs.append({"name": cert_name, "icon": "📜", "link": cert_url, "featured": False})
    if new_certs:
        result["certifications"] = new_certs

    # New skills: lines that look like skill mentions (comma-separated tech names)
    skill_tokens = _extract_skills(text)
    if skill_tokens:
        result["heroBadges"] = skill_tokens[:6]  # top 6 for badges
        result["skills"] = [{"category": "Additional Skills", "items": skill_tokens}]

    # New role: lines mentioning job title + company + date
    new_role = _extract_new_role(lines)
    if new_role:
        result["experience"] = [new_role]

    # Summary override: if enrichment is one coherent paragraph, use as summary
    full_text = " ".join(lines)
    if len(lines) == 1 and len(full_text) > 80:
        result["summary"] = full_text

    # CGPA / GPA mentions — update education entries
    cgpa_re = re.compile(r'(?:cgpa|gpa)\s*(?:is|was|:|=)?\s*([0-9]+(?:\.[0-9]+)?)', re.IGNORECASE)
    cgpa_matches = cgpa_re.findall(text)
    if cgpa_matches and base.get("education"):
        edu = list(base["education"])
        # Assign CGPAs in order they appear (first match → first edu entry, etc.)
        for i, cgpa_val in enumerate(cgpa_matches):
            if i < len(edu):
                edu[i] = dict(edu[i])
                edu[i]["cgpa"] = cgpa_val
        result["education"] = edu

    return result


def _extract_cert_url(line: str) -> str:
    m = re.search(r'https?://(credly\.com|cp\.certmetrics\.com|learn\.microsoft\.com)\S+', line)
    return m.group(0) if m else ""


def _clean_cert_name(text: str) -> str:
    return re.sub(r'^[-–—•·\s]+', '', text).strip()


def _extract_skills(text: str) -> list[str]:
    """Extract technology names from enrichment text."""
    # Known tech patterns — extend as needed
    tech_pattern = re.compile(
        r'\b(Terraform|Kubernetes|Docker|Kafka|Spark|Airflow|dbt|Snowflake|Redshift|'
        r'Databricks|Flink|Iceberg|Delta Lake|Python|Scala|Java|Go|Rust|TypeScript|'
        r'React|FastAPI|Flask|AWS|GCP|Azure|MCP|Claude|LLM|RAG|Bedrock|OpenAI|'
        r'Glean|Trino|Presto|Hive|BigQuery|Looker|dbt|Dagster|Prefect|MLflow)\b',
        re.IGNORECASE
    )
    found = tech_pattern.findall(text)
    # Deduplicate preserving order
    seen = set()
    result = []
    for t in found:
        if t.lower() not in seen:
            seen.add(t.lower())
            result.append(t)
    return result


def _extract_new_role(lines: list[str]) -> dict | None:
    """Look for 'title at Company' or 'started as X at Y' patterns."""
    role_pattern = re.compile(
        r'(?:started as|joined as|now|currently)?\s*'
        r'(?P<title>[\w\s]+?)\s+(?:at|@)\s+(?P<company>[\w\s,\.]+?)'
        r'(?:\s+(?:in|from|since)\s+(?P<period>[\w\s]+?))?'
        r'(?:[,.]|$)',
        re.IGNORECASE
    )
    for line in lines[:5]:  # usually mentioned early in enrichment text
        m = role_pattern.search(line)
        if m:
            return {
                "company": m.group("company").strip(),
                "companyDesc": "",
                "period": m.group("period").strip() if m.group("period") else "Present",
                "roles": [{
                    "title": m.group("title").strip(),
                    "period": m.group("period").strip() if m.group("period") else "Present",
                    "stack": "",
                    "bullets": [line.strip()],
                }]
            }
    return None
