# How to Use LaunchFolio

## Option A — Web UI (no code needed)

### 1. Start the server
```bash
cd backend
pip install -r requirements.txt
python generate.py --serve
```
Open `http://localhost:5000` in your browser (or open `app/index.html` directly).

### 2. Upload and generate
1. Upload your resume PDF
2. Correct any fields the parser got wrong
3. Click **Generate Portfolio**
4. Download the ZIP

### 3. Deploy
```bash
unzip launchfolio-portfolio.zip -d my-portfolio
cd my-portfolio
git init
git remote add origin https://github.com/<username>/<username>.github.io.git
git add .
git commit -m "Initial portfolio"
git push -u origin main
```
Then: GitHub repo → Settings → Pages → Source: `main` → Save.

Your portfolio is live at `https://<username>.github.io` in ~60 seconds.

---

## Option B — CLI

```bash
cd backend
pip install -r requirements.txt
python generate.py --resume /path/to/resume.pdf --output ./my-portfolio
```
Then follow Step 3 above.

---

## Updating your portfolio later

Everything lives in `data.js` inside your generated portfolio repo.

1. Edit `data.js` only — never edit `index.html`, `README.md`, or `resume/resume_print.html` directly
2. Commit and push
3. The GitHub Action auto-regenerates `README.md`
4. GitHub Pages redeploys automatically

To regenerate the PDF resume:
```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu \
  --print-to-pdf="resume/YourName_Resume.pdf" \
  "file://$(pwd)/resume/resume_print.html"
```

---

## File map (generated portfolio)

```
data.js                          ← Edit this only
index.html                       ← Portfolio site shell
js/main.js                       ← Renders everything from data.js
css/styles.css                   ← Styles
resume/resume_print.html         ← Print-to-PDF template
scripts/generate_readme.js       ← Generates README.md
README.md                        ← Auto-generated — do not edit
.github/workflows/deploy.yml     ← Auto-deploys to GitHub Pages
.github/workflows/generate-readme.yml  ← Auto-regenerates README
```
