# LaunchFolio

> Your personal professional presence repo. One place to maintain everything.

Fork this repo, fill in your details once — your portfolio site, resume, and README stay in sync automatically from that point forward.

No separate resume file. No outdated portfolio. No manual syncing. One source of truth, forever.

---

## The problem

Maintaining a professional presence across multiple formats is tedious:

- Update experience on LinkedIn → forget to update the resume
- Update the resume → forget to update the portfolio
- Update the portfolio → README is still the old version
- PDF resume is six months stale

Every format drifts. You end up with four different versions of your own career.

## How LaunchFolio solves it

Everything lives in a single config file — `data.js`. When you change it:

- The **portfolio site** re-renders automatically on next page load
- A **GitHub Action** regenerates `README.md` and commits it
- The **resume HTML** is driven by the same file — regenerate a PDF in one command
- Every format stays in sync, always

You maintain one thing. Everything else follows.

---

## Getting started

### 1. Fork or use this template

```
GitHub → Use this template → Create a new repository
Name it: <yourusername>.github.io
```

### 2. Bootstrap your config

Three ways to populate your initial `data.js`:

**a) Upload a resume PDF** (recommended for first-timers)
```bash
cd backend
pip install -r requirements.txt
python generate.py --resume your_resume.pdf --output ../
# Overwrites data.js with your parsed content
```

**b) Use the web form** (fill in details manually or paste raw content)
```bash
python generate.py --serve
# Open http://localhost:5000
```

**c) Edit `data.js` directly** (if you're comfortable with a text file)
```bash
# Open data.js and fill in your details — comments guide you through each field
```

### 3. Enable GitHub Pages

```bash
git add data.js
git commit -m "Add my details"
git push
# GitHub repo → Settings → Pages → Source: main → Save
```

Your portfolio is live at `https://<yourusername>.github.io` in ~60 seconds.

---

## Day-to-day updates

Changed jobs? Got a new cert? Updated a project?

**Edit `data.js` only.** That's the rule.

```
Edit data.js → git commit → git push
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
            Portfolio site          GitHub Action runs
            re-renders              → regenerates README.md
            on next load            → commits automatically
```

To regenerate the PDF resume after updating:
```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu \
  --print-to-pdf="resume/Resume.pdf" \
  "file://$(pwd)/resume/resume_print.html"
git add resume/Resume.pdf && git commit -m "Update resume PDF"
```

---

## Architecture

```
data.js                          ← Single source of truth — edit this only
│
├── index.html + js/main.js      → Portfolio site (rendered dynamically)
├── resume/resume_print.html     → Print-to-PDF resume template
├── scripts/generate_readme.js   → Generates README.md from data.js
└── .github/workflows/
    ├── deploy.yml               → Auto-deploys site to GitHub Pages on push
    └── generate-readme.yml      → Auto-regenerates README on data.js change
```

```
bootstrap/                       ← One-time setup tools (not deployed)
├── app/                         Web form UI — upload PDF or paste raw content
└── backend/
    ├── parse_resume.py          Extracts structured data from PDF
    ├── generate.py              Populates data.js from parsed data (CLI + Flask)
    └── models.py                Data schema matching data.js structure
```

---

## What the portfolio includes

- Hero section with name, title, taglines, skill badges, and CTAs
- Experience timeline with role cards, stack tags, and bullet points
- Skills grid grouped by category
- Projects section (professional + open source)
- Education and certifications (with verification links)
- Contact section
- Auto-generated README matching all of the above

All sections driven by `data.js`. Add a field once, it appears everywhere.

---

## Roadmap

- [x] Portfolio template (single source of truth, CI/CD)
- [x] Resume HTML template (renders from data.js)
- [x] Auto README generation via GitHub Action
- [ ] Resume PDF parser (pdfplumber — in progress)
- [ ] Web form UI (upload PDF or paste raw content)
- [ ] data.js generator from parsed resume
- [ ] DOCX resume output
- [ ] Multi-template support (light theme, minimal layout)

---

## AI assistant friendly

This repo ships with `HOWTO.md` explaining the architecture. Any AI coding assistant (Claude, GitHub Copilot, Cursor, etc.) that reads it will know to edit only `data.js` and let CI/CD handle the rest.

---

## Contributing

PRs welcome. The most valuable contributions:

- Better resume parsing (resumes vary wildly in format)
- Additional portfolio templates
- DOCX output from data.js

---

## License

MIT — fork it, use it, make it yours.
