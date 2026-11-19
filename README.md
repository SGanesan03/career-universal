# 🚀 CareerOS Zero-Config — End-User Ready AI Job & Outreach SaaS

End-users **never** need a GitHub account, GitHub token, or API key! They simply open your website link, enter their Name/Email, upload their PDF resume, and start applying. Meanwhile, all user resumes stay 100% encrypted & isolated inside your **Private GitHub Data Repo**.

## One-Time Admin Setup (5 Minutes in Chrome)

### Step 1: Create 2 GitHub Repositories
1. **Public App Repo (`careeros-app`)**: Host the frontend (`index.html`, `scraper_worker.py`, `requirements.txt`, `.github/workflows/discover_jobs.yml`). Enable **Settings -> Pages -> Branch: `main` (`/root`) -> Save** to get your public Website URL.
2. **Private Data Repo (`careeros-private-data`)**: Create a **Private** repository with a single empty file `data/users/.gitkeep`. All users' resumes and job histories are stored safely here!

### Step 2: Deploy the Free Google Apps Script Bridge
1. Open [script.google.com](https://script.google.com) -> **New project**.
2. Paste the entire code from `Code.gs` into the editor and save.
3. Click **Project Settings (Gear icon left sidebar) -> Script Properties -> Add script property** and add:
   - `GEMINI_API_KEY` = Your `AIzaSy...` key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
   - `GH_OWNER` = Your GitHub username (e.g., `sganesan03`)
   - `GH_REPO` = `careeros-private-data`
   - `GH_TOKEN` = Fine-grained GitHub token with **Contents (Read/Write)** on `careeros-private-data` and **Actions (Read/Write)** on `careeros-app`
4. Click **Deploy -> New deployment -> Web app**:
   - Execute as: **Me**
   - Who has access: **Anyone**
   - Click **Deploy** and copy the **Web app URL** (`https://script.google.com/macros/s/.../exec`).

### Step 3: Paste Bridge URL into `index.html`
1. Edit `index.html` in `careeros-app` and replace `PASTE_YOUR_GOOGLE_APPS_SCRIPT_WEB_APP_URL_HERE` with your Apps Script Web App URL.

### Step 4: Add Secrets to `careeros-app` (For 8 AM – 8 PM Auto-Scan)
Go to `careeros-app` **Settings -> Secrets and variables -> Actions** and add:
- `GEMINI_API_KEY` = Your `AIzaSy...` key
- `TELEGRAM_BOT_TOKEN` = Token from `@BotFather`
- `WEB_APP_URL` = Your GitHub Pages URL
- `DATA_REPO_FULL_NAME` = `sganesan03/careeros-private-data`
- `GH_DATA_TOKEN` = Same Fine-Grained GitHub token
