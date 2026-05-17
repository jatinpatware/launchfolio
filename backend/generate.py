"""
Generator — takes a ResumeData dict and produces a ready-to-deploy portfolio ZIP.

Usage (CLI):
    python generate.py --resume path/to/resume.pdf --output ./my-portfolio

Usage (from Flask server):
    from generate import build_zip
    zip_bytes = build_zip(resume_data_dict)
"""

import argparse
import io
import json
import os
import shutil
import zipfile
from pathlib import Path

from parse_resume import parse


TEMPLATE_DIR = Path(__file__).parent.parent / "template"

THEMES = {
    "ocean": {   # default
        "--bg": "#0d1b2a", "--bg2": "#112233", "--bg3": "#152840",
        "--teal": "#00b4d8", "--teal-dim": "#0096b4",
        "--white": "#f0f4f8", "--muted": "#8899aa",
        "--card-bg": "#132035", "--border": "#1e3a55",
    },
    "midnight": {
        "--bg": "#09090f", "--bg2": "#111122", "--bg3": "#1a1a2e",
        "--teal": "#818cf8", "--teal-dim": "#6366f1",
        "--white": "#f1f0ff", "--muted": "#8888bb",
        "--card-bg": "#111128", "--border": "#2a2a4a",
    },
    "forest": {
        "--bg": "#091510", "--bg2": "#0f2018", "--bg3": "#142b1e",
        "--teal": "#34d399", "--teal-dim": "#10b981",
        "--white": "#f0faf4", "--muted": "#7aaa8a",
        "--card-bg": "#0e1f16", "--border": "#1a3f2a",
    },
    "ember": {
        "--bg": "#130e09", "--bg2": "#1e1610", "--bg3": "#2b1e14",
        "--teal": "#fb923c", "--teal-dim": "#f97316",
        "--white": "#fef3ea", "--muted": "#aa9070",
        "--card-bg": "#1a1208", "--border": "#3a2510",
    },
    "rose": {
        "--bg": "#120a0e", "--bg2": "#1e1018", "--bg3": "#2a1420",
        "--teal": "#fb7185", "--teal-dim": "#f43f5e",
        "--white": "#fff0f3", "--muted": "#aa8090",
        "--card-bg": "#1a0d14", "--border": "#3a1a26",
    },
}


def _render_theme_css(theme_name: str) -> str:
    theme = THEMES.get(theme_name, THEMES["ocean"])
    vars_block = "\n".join(f"  {k}: {v};" for k, v in theme.items())
    return f":root {{\n{vars_block}\n}}\n"


def _render_data_js(data: dict) -> str:
    """Render data.js from parsed resume dict."""
    def js_str(v):
        return json.dumps(v, ensure_ascii=False)

    def js_list(lst):
        return json.dumps(lst, ensure_ascii=False, indent=4)

    skills_js = json.dumps(data.get("skills", []), ensure_ascii=False, indent=4)
    experience_js = json.dumps(data.get("experience", []), ensure_ascii=False, indent=4)
    certs_js = json.dumps(data.get("certifications", []), ensure_ascii=False, indent=4)
    projects_js = json.dumps(data.get("projects", []), ensure_ascii=False, indent=4)
    education_js = json.dumps(data.get("education", []), ensure_ascii=False, indent=4)
    achievements_js = json.dumps(data.get("achievements", []), ensure_ascii=False, indent=4)
    extras_js = json.dumps(data.get("extras", []), ensure_ascii=False, indent=4)
    hero_badges_js = json.dumps(data.get("heroBadges", []), ensure_ascii=False)
    focus_js = json.dumps(data.get("focus", []), ensure_ascii=False, indent=4)

    return f"""// ============================================================
// SINGLE SOURCE OF TRUTH — update here, everything else syncs
// ============================================================
const resumeData = {{

  name:      {js_str(data.get("name", ""))},
  title:     {js_str(data.get("title", ""))},
  tagline1:  {js_str(data.get("tagline1", ""))},
  tagline2:  {js_str(data.get("tagline2", ""))},
  sub:       {js_str(data.get("sub", ""))},
  location:  {js_str(data.get("location", ""))},
  email:     {js_str(data.get("email", ""))},
  linkedin:  {js_str(data.get("linkedin", ""))},
  github:    {js_str(data.get("github", ""))},
  portfolio: {js_str(data.get("portfolio", ""))},
  credly:    {js_str(data.get("credly", ""))},
  phone:     {js_str(data.get("phone", ""))},
  twitter:   {js_str(data.get("twitter", ""))},
  leetcode:  {js_str(data.get("leetcode", ""))},
  hackerrank: {js_str(data.get("hackerrank", ""))},

  heroBadges: {hero_badges_js},

  summary: {js_str(data.get("summary", ""))},

  focus: {focus_js},

  skills: {skills_js},

  experience: {experience_js},

  certifications: {certs_js},

  projects: {projects_js},

  education: {education_js},

  achievements: {achievements_js},

  extras: {extras_js},
}};
"""


def build_zip(data: dict) -> bytes:
    """Build a ZIP of the full portfolio from template + generated data.js."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # Copy all template files except data.js (always use generated version)
        for path in TEMPLATE_DIR.rglob("*"):
            if path.is_file():
                arcname = path.relative_to(TEMPLATE_DIR)
                if str(arcname) in ("data.js", "theme.css"):
                    continue
                zf.write(path, arcname)

        # Write generated data.js
        zf.writestr("data.js", _render_data_js(data))
        zf.writestr("theme.css", _render_theme_css(data.get("_theme", "ocean")))

    return buf.getvalue()


# ── Flask server ──────────────────────────────────────────────────────────────

def create_app():
    from flask import Flask, request, send_file, send_from_directory
    from flask_cors import CORS

    app_dir = Path(__file__).parent.parent / "app"
    app = Flask(__name__, static_folder=str(app_dir), static_url_path="")
    CORS(app)

    @app.get("/")
    def index():
        return send_from_directory(app_dir, "index.html")

    @app.post("/api/parse")
    def parse_resume_endpoint():
        """Parse a resume PDF and return structured JSON for form auto-fill."""
        from parse_resume import parse, _extract_text

        resume_file = request.files.get("resume")
        if not resume_file or not resume_file.filename:
            return {"error": "No file provided"}, 400

        tmp_path = f"/tmp/launchfolio_parse_{os.getpid()}.pdf"
        try:
            resume_file.save(tmp_path)
            data = parse(tmp_path)
            return data
        except Exception as e:
            return {"error": str(e)}, 500
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    @app.post("/api/generate")
    def generate():
        from parse_resume import parse, _extract_text
        from enrich import merge
        from llm import is_ai_enabled
        from parse_ai import parse_with_ai

        overrides = {k: request.form.get(k, "") for k in
                     ["name", "title", "email", "location", "linkedin", "github",
                      "tagline1", "tagline2", "summary",
                      "phone", "twitter", "leetcode", "hackerrank", "portfolio", "credly"]}
        hero_badges_raw = request.form.get("hero_badges", "")
        overrides["heroBadges"] = [b.strip() for b in hero_badges_raw.split(",") if b.strip()]

        resume_file = request.files.get("resume")
        enrichment  = request.form.get("enrichment", "").strip()

        # AI config — optional, from form fields
        ai_config = {
            "provider": request.form.get("ai_provider", "anthropic").lower(),
            "model":    request.form.get("ai_model", "").strip(),
            "api_key":  request.form.get("ai_api_key", "").strip(),
        }

        tmp_path = None
        try:
            if resume_file and resume_file.filename:
                tmp_path = f"/tmp/launchfolio_resume_{os.getpid()}.pdf"
                resume_file.save(tmp_path)

            if is_ai_enabled(ai_config):
                # ── AI path: one LLM call handles parse + merge ──────────
                resume_text = _extract_text(tmp_path) if tmp_path else ""
                data = parse_with_ai(resume_text, enrichment, ai_config)
                # Still apply explicit form overrides on top
                from enrich import _apply_overrides
                data = _apply_overrides(data, overrides)
            else:
                # ── Non-AI path: regex parse + rule-based merge ──────────
                base_data = parse(tmp_path) if tmp_path else {}
                data = merge(base_data, enrichment, overrides)

            data["_theme"] = request.form.get("theme", "ocean")
            zip_bytes = build_zip(data)
            return send_file(
                io.BytesIO(zip_bytes),
                mimetype="application/zip",
                as_attachment=True,
                download_name="launchfolio-portfolio.zip",
            )
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

    return app


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LaunchFolio CLI generator")
    parser.add_argument("--resume", help="Path to PDF resume (CLI mode)")
    parser.add_argument("--output", default="./my-portfolio", help="Output directory")
    parser.add_argument("--serve", action="store_true", help="Start Flask dev server")
    args = parser.parse_args()

    if args.serve:
        app = create_app()
        print("LaunchFolio running at http://localhost:5000")
        app.run(debug=True, port=5000)
    elif not args.resume:
        parser.error("--resume is required when not using --serve")
    else:
        data = parse(args.resume)
        zip_bytes = build_zip(data)
        out = Path(args.output)
        out.mkdir(parents=True, exist_ok=True)
        import zipfile
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            zf.extractall(out)
        print(f"Portfolio generated at: {out.resolve()}")
        print("Next: push to GitHub and enable Pages.")
