# LaunchFolio — How to Use

---

## Quickest start

**Mac / Linux** — one command does everything:
```bash
bash setup.sh
```

**Windows** — double-click `setup.bat`

Both scripts check for Python, install dependencies, and start the server.  
Then open **http://localhost:5000** in your browser.

> Keep the Terminal/Command Prompt window open while using the app — closing it stops the server.

---

## Manual setup (step by step)

### Step 0 — Install Python 3

Check if you already have it:
```bash
python3 --version
```

If you see `Python 3.x.x`, skip to Step 1. If not:

**Mac:** Download from https://www.python.org/downloads/ and run the `.pkg` installer.

**Windows:** Download from https://www.python.org/downloads/ — tick **"Add Python to PATH"** during install, then open a new Command Prompt.

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install python3 python3-pip
```

---

### Step 1 — Get LaunchFolio

**With Git:**
```bash
git clone https://github.com/<your-username>/launchfolio.git
cd launchfolio
```

**Without Git:**
1. Download the ZIP from GitHub → **Code → Download ZIP**
2. Unzip it and open a Terminal inside the folder  
   (Mac: drag folder onto Terminal; Windows: Shift+right-click → "Open PowerShell here")

---

### Step 2 — Install dependencies

```bash
cd backend
pip3 install -r requirements.txt
```

If `pip3` isn't found, try `pip`:
```bash
pip install -r requirements.txt
```

If you get an SSL error on Mac:
```bash
pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

**AI parsing (optional)** — only needed if you want AI-powered parsing:
```bash
pip3 install anthropic    # for Anthropic / Claude
pip3 install openai       # for OpenAI / GPT-4o
```

---

### Step 3 — Start the server

From the `backend/` folder:
```bash
python3 generate.py --serve
```

Or from the project root:
```bash
python3 backend/generate.py --serve
```

You should see:
```
LaunchFolio running at http://localhost:5000
```

Open **http://localhost:5000** in your browser.

---

## Step 4 — Generate your portfolio

Fill in the form:

**Upload your resume PDF** (optional but recommended)  
The parser reads it and auto-fills the form fields. For best results, export directly from LinkedIn:  
`LinkedIn → Me → View Profile → More → Save to PDF`

**Enrichment text** (optional, recommended for non-AI mode)  
Paste anything your resume doesn't fully cover: new roles, new projects, certifications with links, or custom sections like accomplishments and awards. Plain English is fine.

Example enrichment text:
```
Tagline: Building scalable data pipelines at petabyte scale
Focus: Data Architecture, Apache Spark, AWS, LLM Integration

Accomplishments:
- AIR-1518 in GATE 2016 (Computer Science)
- Led a hackathon project adopted into production within 3 months

Soft Skills: Mentorship, System Thinking, Technical Communication

CGPA is 8.55 for M.Tech, CGPA is 7.8 for B.E.
```

**Review and correct fields**  
Name, title, email, LinkedIn URL, GitHub, taglines, and contact links. These always override what the PDF parse finds.

**Optional contact fields**  
Phone, Twitter/X, LeetCode, HackerRank, Credly, and Portfolio URL — fill in whichever apply.

**Hero badges**  
Short skill keywords shown in the hero section, comma-separated. Example: `Apache Spark, AWS, Python, Kafka`

**Colour theme**  
Pick one of five themes: Ocean (dark blue), Midnight (indigo), Forest (green), Ember (orange), Rose (red-pink).

**AI parsing (optional)**  
Toggle on, select your provider (Anthropic or OpenAI), and paste your API key. AI mode gives a much more accurate parse — especially for complex or non-standard resume layouts. Leave off to use the built-in rule-based parser.

Click **Generate Portfolio**, then **Download ZIP**.

---

## Step 5 — Deploy to GitHub Pages (free)

### 5a — Create a GitHub account
Go to https://github.com and sign up for free if you don't have one.

### 5b — Create a repository
1. Click **+** → **New repository**
2. Name it exactly: `<your-username>.github.io`  
   Example: for username `johndoe`, name it `johndoe.github.io`
3. Set visibility to **Public**
4. Leave "Initialize with README" **unticked**
5. Click **Create repository**

### 5c — Unzip and push

**Mac / Linux:**
```bash
unzip launchfolio-portfolio.zip -d my-portfolio
cd my-portfolio
git init
git add .
git commit -m "Initial portfolio"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-username>.github.io.git
git push -u origin main
```

**Windows (Command Prompt):**
```cmd
tar -xf launchfolio-portfolio.zip -C my-portfolio
cd my-portfolio
git init
git add .
git commit -m "Initial portfolio"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-username>.github.io.git
git push -u origin main
```

Replace `<your-username>` with your actual GitHub username.

### 5d — Enable GitHub Pages
1. Go to your repo on GitHub → **Settings → Pages**
2. Under "Source", select **Deploy from a branch**
3. Branch: `main`, folder: `/ (root)`
4. Click **Save**

Your portfolio is live at **https://\<your-username\>.github.io** within ~60 seconds.

---

## Updating your portfolio later

All your data lives in `data.js` inside your portfolio repo. Edit only that file.

```bash
# Edit data.js with any text editor, then:
git add data.js
git commit -m "Update portfolio"
git push
```

GitHub Pages redeploys automatically. Your README is also regenerated by a GitHub Action.

### Adding custom sections (Accomplishments, Awards, Soft Skills, etc.)

Open `data.js` and edit the `extras` array:

```js
extras: [
  {
    title: "Accomplishments",
    type: "list",        // renders as bullet points
    items: [
      "AIR-1518 in GATE 2016 (top 0.1% nationally)",
      "Led hackathon project adopted into production"
    ]
  },
  {
    title: "Soft Skills",
    type: "tags",        // renders as pill chips
    items: ["Mentorship", "System Thinking", "Technical Communication"]
  },
  {
    title: "Languages",
    type: "tags",
    items: ["English (Fluent)", "Hindi (Native)"]
  }
]
```

These appear as a "Highlights" section on the portfolio site and as additional sections in the resume print view.

### Regenerate the PDF resume

After editing `data.js`, regenerate your PDF resume using Chrome:

**Mac:**
```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu \
  --print-to-pdf="resume/Resume.pdf" \
  "file://$(pwd)/resume/resume_print.html"
git add resume/Resume.pdf && git commit -m "Update resume PDF"
```

**Windows (PowerShell):**
```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --headless --disable-gpu `
  --print-to-pdf="resume\Resume.pdf" `
  "file:///$((Get-Location).Path.Replace('\','/'))/resume/resume_print.html"
git add resume\Resume.pdf && git commit -m "Update resume PDF"
```

---

## Stopping the server

Go back to the Terminal and press `Ctrl + C`.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python3: command not found` | Install Python from python.org — see Step 0 |
| `pip3: command not found` | Try `pip` instead, or run `python3 -m pip install -r requirements.txt` |
| SSL error during pip install | Add `--trusted-host pypi.org --trusted-host files.pythonhosted.org` |
| Port 5000 already in use | Close the other app using port 5000, or restart your computer and try again |
| Browser says "can't be reached" | The server stopped — run the start command again |
| Portfolio shows wrong data | Form fields always override the PDF parse — check what you typed in the form |
| Experience section is empty | Switch to AI parsing mode for better accuracy on complex resume layouts |
| Git push asks for a password | Use a Personal Access Token — see https://docs.github.com/en/authentication |
| Windows: `bash` not found | Use `setup.bat` instead of `setup.sh`, or install Git Bash |
