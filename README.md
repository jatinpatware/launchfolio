# LaunchFolio

> Upload your resume. Get a deployed developer portfolio in minutes.

LaunchFolio is an open-source tool that turns a resume PDF into a complete, self-hosted portfolio — with a generated data config, multiple resume formats (PDF, DOCX, HTML), and a GitHub Pages-ready site with CI/CD baked in.

No templates to fight. No hosting fees. One upload.

---

## How it works

```
Upload resume (PDF)
        │
        ▼
  ┌─────────────┐
  │   Parser    │  Extracts name, title, experience, skills,
  │  (Python)   │  education, certifications from your resume
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │  Generator  │  Produces:
  │             │  • data.js  (single source of truth)
  │             │  • portfolio site (HTML/CSS/JS)
  │             │  • resume PDF + HTML
  │             │  • README.md (auto-synced)
  │             │  • GitHub Actions CI/CD workflows
  └──────┬──────┘
         │
         ▼
  Download ZIP  →  Push to GitHub  →  Enable Pages  →  Live in 60 seconds
```

---

## Features

- **Resume parser** — extracts structured data from uploaded PDF
- **Single source of truth** — all content in `data.js`; update once, syncs everywhere
- **Portfolio site** — dark-themed, responsive, sections for experience, skills, projects, certs
- **Resume formats** — print-ready HTML (Chrome PDF), structured for ATS
- **Auto README** — GitHub Action regenerates `README.md` from `data.js` on every push
- **GitHub Pages deploy** — workflow included, enable Pages and you're live
- **AI-assistant friendly** — ships with `HOWTO.md` and project docs so any AI assistant can help maintain it

---

## Quick Start

### 1. Use the web UI (recommended)

```
Open app/index.html in your browser
→ Upload your resume PDF
→ Fill in any missing details
→ Click "Generate Portfolio"
→ Download the ZIP
```

### 2. CLI

```bash
pip install -r backend/requirements.txt
python backend/generate.py --resume your_resume.pdf --output ./my-portfolio
```

### 3. Deploy

```bash
cd my-portfolio
git init
git remote add origin https://github.com/<username>/<username>.github.io.git
git add . && git commit -m "Initial portfolio"
git push -u origin main
# Then: GitHub repo → Settings → Pages → Source: main → Save
```

Your portfolio is live at `https://<username>.github.io` in ~60 seconds.

---

## Project Structure

```
launchfolio/
├── app/                    # Web UI for resume upload
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── backend/                # Resume parsing and generation
│   ├── parse_resume.py     # Extracts structured data from PDF
│   ├── generate.py         # Generates portfolio files from data
│   ├── models.py           # Data models / schema
│   └── requirements.txt
├── template/               # Portfolio template (what gets generated)
│   ├── index.html
│   ├── data.js             # Generated from resume — edit this to update everything
│   ├── css/styles.css
│   ├── js/main.js
│   ├── resume/
│   │   └── resume_print.html
│   ├── scripts/
│   │   └── generate_readme.js
│   └── .github/workflows/
│       ├── deploy.yml
│       └── generate-readme.yml
├── HOWTO.md                # Step-by-step for first-time users
└── README.md
```

---

## Roadmap

- [x] Portfolio template (single source of truth, CI/CD)
- [ ] Resume PDF parser (PyMuPDF / pdfplumber)
- [ ] Web UI for upload + manual editing
- [ ] data.js generator from parsed resume
- [ ] ZIP download with ready-to-deploy repo
- [ ] DOCX resume output
- [ ] Multi-template support

---

## Contributing

PRs welcome. The parser (`backend/parse_resume.py`) is the hardest part — resumes vary wildly in format. If you have a working parser for a specific layout, that's a great contribution.

---

## License

MIT
