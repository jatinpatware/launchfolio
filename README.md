# LaunchFolio

**Upload your resume → get a deployable portfolio in 60 seconds.**

LaunchFolio reads your PDF resume, auto-fills a form, and generates a ready-to-deploy ZIP containing your portfolio site, resume page, and README — all driven by a single config file (`data.js`). Update that one file and everything stays in sync.

---

## Quick start

**Mac / Linux**
```bash
git clone https://github.com/<your-username>/launchfolio.git
cd launchfolio
bash setup.sh
# → opens at http://localhost:5000
```

**Windows**
```
Double-click setup.bat
# → opens at http://localhost:5000
```

Open the browser form, upload your resume PDF, fill in any extras, pick a colour theme, and click **Generate Portfolio**. Download the ZIP, push it to GitHub, enable Pages — done.

---

## What you get

The generated portfolio includes:

| Section | What it shows |
|---------|--------------|
| Hero | Name, title, taglines, skill badges |
| About | Summary + what you focus on |
| Experience | Timeline with role cards, stack tags, bullet points |
| Skills | Category-grouped skill chips |
| Projects | Cards for professional and open-source work |
| Education & Certifications | Degree cards with CGPA, cert list with verification links |
| Highlights | Custom extras — accomplishments, awards, soft skills, languages, etc. |
| Contact | Links to email, LinkedIn, GitHub, Twitter, LeetCode, HackerRank, Credly |

Five colour themes: Ocean (default), Midnight, Forest, Ember, Rose.

---

## How it works

Everything lives in `data.js`:

```
data.js  ← single source of truth — edit only this file after setup
│
├── index.html + js/main.js       → portfolio site (renders from data.js)
├── resume/resume_print.html      → printable resume (renders from data.js)
├── scripts/generate_readme.js    → auto-generates README.md
└── .github/workflows/
    ├── deploy.yml                → deploys site to GitHub Pages on push
    └── generate-readme.yml       → regenerates README when data.js changes
```

---

## After setup — updating your portfolio

Edit `data.js` only. That's the rule.

```bash
# Change any field in data.js, then:
git add data.js
git commit -m "Update portfolio"
git push
# GitHub Pages redeploys automatically
```

To regenerate the PDF resume after updating:

**Mac:**
```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu \
  --print-to-pdf="resume/Resume.pdf" \
  "file://$(pwd)/resume/resume_print.html"
```

**Windows (PowerShell):**
```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --headless --disable-gpu `
  --print-to-pdf="resume\Resume.pdf" `
  "file:///$((Get-Location).Path.Replace('\','/'))/resume/resume_print.html"
```

---

## Custom sections (Accomplishments, Awards, Soft Skills, etc.)

Add any custom section to `data.js` under `extras`:

```js
extras: [
  { title: "Accomplishments", type: "list", items: [
      "AIR-1518 in GATE 2016",
      "Led hackathon project adopted into production"
  ]},
  { title: "Soft Skills", type: "tags", items: [
      "Mentorship", "System Thinking", "Technical Communication"
  ]},
]
```

`type: "list"` renders as bullet points. `type: "tags"` renders as pill chips.  
These appear automatically in the portfolio and the resume print view.

---

## AI parsing (optional)

Toggle **Use AI parsing** in the form and enter your API key for a much more accurate parse — especially useful for non-standard resume layouts.

Supported providers:
- **Anthropic** — `claude-sonnet-4-6` or `claude-opus-4-7`  
  Get a key at https://console.anthropic.com
- **OpenAI** — `gpt-4o` or `gpt-4o-mini`  
  Get a key at https://platform.openai.com

Install the matching package before using:
```bash
pip3 install anthropic   # for Anthropic
pip3 install openai      # for OpenAI
```

---

## Architecture

```
launchfolio/
├── setup.sh / setup.bat     ← run this first (installs deps + starts server)
├── backend/
│   ├── generate.py          Flask server + ZIP builder + CLI
│   ├── parse_resume.py      PDF → structured data (rule-based)
│   ├── parse_ai.py          PDF → structured data (LLM-powered)
│   ├── enrich.py            Merges enrichment text + form overrides
│   └── requirements.txt     Python dependencies
├── app/
│   ├── index.html           Web form UI
│   ├── app.js               Form logic, validation, theme picker
│   └── styles.css           Form styles
└── template/                Generated into every portfolio ZIP
    ├── data.js              Blank config — populated by the generator
    ├── index.html           Portfolio site shell
    ├── css/styles.css       Portfolio styles
    ├── js/main.js           Portfolio renderer (reads data.js)
    ├── theme.css            Generated colour theme overrides
    └── resume/
        └── resume_print.html  Printable resume (reads data.js)
```

---

## Contributing

PRs welcome. Highest-value contributions:
- Better resume parsing (resumes vary wildly in format)
- Additional portfolio templates / themes
- DOCX resume output

---

## License

MIT — fork it, use it, make it yours.
