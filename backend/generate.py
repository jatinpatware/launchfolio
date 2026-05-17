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

  heroBadges: {hero_badges_js},

  summary: {js_str(data.get("summary", ""))},

  focus: {focus_js},

  skills: {skills_js},

  experience: {experience_js},

  certifications: {certs_js},

  projects: {projects_js},

  education: {education_js},

  achievements: {achievements_js},
}};
"""


def build_zip(data: dict) -> bytes:
    """Build a ZIP of the full portfolio from template + generated data.js."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # Copy all template files
        for path in TEMPLATE_DIR.rglob("*"):
            if path.is_file():
                arcname = path.relative_to(TEMPLATE_DIR)
                zf.write(path, arcname)

        # Overwrite data.js with generated content
        zf.writestr("data.js", _render_data_js(data))

    return buf.getvalue()


# ── Flask server ──────────────────────────────────────────────────────────────

def create_app():
    from flask import Flask, request, send_file
    from flask_cors import CORS

    app = Flask(__name__)
    CORS(app)

    @app.post("/api/generate")
    def generate():
        from parse_resume import parse
        from enrich import merge

        overrides = {k: request.form.get(k, "") for k in
                     ["name", "title", "email", "location", "linkedin", "github",
                      "tagline1", "tagline2", "summary"]}
        hero_badges_raw = request.form.get("hero_badges", "")
        overrides["heroBadges"] = [b.strip() for b in hero_badges_raw.split(",") if b.strip()]

        resume_file = request.files.get("resume")
        enrichment  = request.form.get("enrichment", "").strip()

        tmp_path = None
        try:
            # 1. Parse resume if provided, otherwise start with empty base
            if resume_file and resume_file.filename:
                tmp_path = f"/tmp/launchfolio_resume_{os.getpid()}.pdf"
                resume_file.save(tmp_path)
                base_data = parse(tmp_path)
            else:
                base_data = {}

            # 2. Merge enrichment text on top of base, then apply explicit overrides
            data = merge(base_data, enrichment, overrides)

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
    parser.add_argument("--resume", required=True, help="Path to PDF resume")
    parser.add_argument("--output", default="./my-portfolio", help="Output directory")
    parser.add_argument("--serve", action="store_true", help="Start Flask dev server instead")
    args = parser.parse_args()

    if args.serve:
        app = create_app()
        print("LaunchFolio dev server running at http://localhost:5000")
        app.run(debug=True, port=5000)
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
