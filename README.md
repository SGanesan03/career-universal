# 🚀 CareerOS Pure-GitHub SaaS (No script.google.com Needed!)

100% hosted on **GitHub Pages** + **GitHub Actions** + **Private GitHub Data Repo**. No external script platforms required!

## Setup Guide (3 Simple Steps)

### Step 1: Create 2 Repos on GitHub
1. **Public App Repo (`careeros-app`)**: Upload `index.html`, `scraper_worker.py`, `requirements.txt`, and `.github/workflows/discover_jobs.yml`. Enable **Settings -> Pages -> Branch: `main` (`/root`) -> Save**.
2. **Private Data Repo (`careeros-private-data`)**: Create a **Private** repo with `data/users/.gitkeep`. All users' resumes and job histories stay private here.

### Step 2: Add Secrets to `careeros-app`
Go to `careeros-app` **Settings -> Secrets and variables -> Actions** and add:
- `GEMINI_API_KEY` = Your `AIzaSy...` key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
- `TELEGRAM_BOT_TOKEN` = Token from `@BotFather`
- `WEB_APP_URL` = Your GitHub Pages URL
- `DATA_REPO_FULL_NAME` = `sganesan03/careeros-private-data`
- `GH_DATA_TOKEN` = Fine-grained GitHub token (**Contents: Read/Write** on `careeros-private-data` + **Actions: Read/Write** on `careeros-app`)

### Step 3: Generate Your Zero-Config Magic Link
1. Open your GitHub Pages URL in Chrome.
2. At the bottom of the Login box, click **⚙️ Admin One-Time Link Generator (Owner Only)**.
3. Enter your details once and click **🔗 Generate Zero-Config End-User Link**.
4. Share that Magic Link with anyone—when they open it, they simply enter their **Name / Email** and upload their PDF resume with **0 configuration**!
