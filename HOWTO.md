# How to Use LaunchFolio

---

## Step 0 — Prerequisites

You need Python 3 and pip installed. Follow the steps for your operating system.

### Check if Python is already installed

Open **Terminal** (Mac/Linux) or **Command Prompt** (Windows) and run:

```bash
python3 --version
```

If you see something like `Python 3.11.4`, skip to **Step 0b**. If you get "command not found", install Python first.

### Step 0a — Install Python (if not installed)

**Mac:**
1. Go to https://www.python.org/downloads/
2. Click **Download Python 3.x.x**
3. Open the downloaded `.pkg` file and follow the installer
4. After install, run `python3 --version` to confirm it worked

**Windows:**
1. Go to https://www.python.org/downloads/
2. Click **Download Python 3.x.x**
3. Run the installer — **tick "Add Python to PATH"** before clicking Install
4. After install, open a new Command Prompt and run `python --version`

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### Step 0b — Check pip is available

```bash
pip3 --version
```

If you see a version number, you're ready. If not:

**Mac/Linux:**
```bash
python3 -m ensurepip --upgrade
```

**Windows:**
```bash
python -m ensurepip --upgrade
```

---

## Step 1 — Download LaunchFolio

**Option A — with Git:**
```bash
git clone https://github.com/jatinpatware/launchfolio.git
cd launchfolio
```

**Option B — without Git:**
1. Go to https://github.com/jatinpatware/launchfolio
2. Click **Code → Download ZIP**
3. Unzip it — you'll get a folder called `launchfolio-main`
4. Open Terminal in that folder (Mac: drag folder onto Terminal icon; Windows: Shift+right-click → "Open PowerShell window here")

---

## Step 2 — Install dependencies

```bash
cd backend
pip3 install -r requirements.txt
```

If you get an SSL error on Mac:
```bash
pip3 install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

If the command `pip3` isn't found, try `pip` instead:
```bash
pip install -r requirements.txt
```

---

## Step 3 — Start the server

```bash
python3 generate.py --serve
```

You should see:
```
LaunchFolio running at http://localhost:5000
```

Now open your browser and go to: **http://localhost:5000**

> Keep this Terminal window open while you use the app — closing it stops the server.

---

## Step 4 — Generate your portfolio

In the browser form:

1. **Upload your resume PDF** (optional but recommended — the parser reads it to pre-fill fields)
2. **Paste any enrichment text** — things your old resume doesn't cover: new roles, new projects, new skills, certifications with links. Plain text is fine.
3. **Review and correct fields** — name, title, email, LinkedIn, etc. These override the PDF parse.
4. **AI parsing (optional)** — toggle on, pick Anthropic or OpenAI, paste your API key. Leave off to use the built-in rule-based parser.
5. Click **Generate Portfolio**
6. **Download the ZIP**

---

## Step 5 — Deploy to GitHub Pages

### 5a — Create a GitHub account (if you don't have one)
Go to https://github.com and sign up for free.

### 5b — Create a repository
1. Click **+** → **New repository**
2. Name it exactly: `<your-username>.github.io`  
   Example: if your username is `johndoe`, name it `johndoe.github.io`
3. Set it to **Public**
4. Leave "Initialize with README" **unticked**
5. Click **Create repository**

### 5c — Unzip and push

**Mac/Linux:**
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

> Replace `<your-username>` with your actual GitHub username in the remote URL above.

### 5d — Enable GitHub Pages
1. Go to your repo on GitHub
2. Click **Settings** → **Pages**
3. Under "Source", select **Deploy from a branch**
4. Choose branch: `main`, folder: `/ (root)`
5. Click **Save**

Your portfolio will be live at **https://\<your-username\>.github.io** within about 60 seconds.

---

## Updating your portfolio later

All your data lives in `data.js` inside your portfolio repo.

1. Edit `data.js` — change any field you want
2. Save, commit, and push:

```bash
git add data.js
git commit -m "Update portfolio"
git push
```

3. GitHub automatically redeploys the site and regenerates `README.md`

> Never edit `index.html`, `README.md`, or `resume/resume_print.html` directly — they are auto-generated.

### Regenerate the PDF resume (optional)

After updating `data.js`, regenerate your PDF resume with Chrome:

**Mac:**
```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu \
  --print-to-pdf="resume/YourName_Resume.pdf" \
  "file://$(pwd)/resume/resume_print.html"
```

**Windows (PowerShell):**
```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --headless --disable-gpu `
  --print-to-pdf="resume\YourName_Resume.pdf" `
  "file:///$((Get-Location).Path.Replace('\','/'))/resume/resume_print.html"
```

---

## Stopping the server

Go back to the Terminal where the server is running and press `Ctrl + C`.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python3: command not found` | Install Python from python.org (see Step 0a) |
| `pip3: command not found` | Try `pip` instead of `pip3`, or run `python3 -m pip` |
| SSL error during pip install | Add `--trusted-host pypi.org --trusted-host files.pythonhosted.org` |
| Port 5000 already in use | Another app is using that port — run `python3 generate.py --serve` again after a restart |
| Browser says "This site can't be reached" | Make sure the server is still running in Terminal |
| Generated portfolio shows wrong data | Check the form fields in Step 4 — the form overrides always win over the PDF parse |
| Git push asks for username/password | Use a Personal Access Token instead of your password — see https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token |
