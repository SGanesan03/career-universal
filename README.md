# 🔒 CareerOS Vault — Single-Repo AES-256 Encrypted SaaS

Everything lives in **one single GitHub repository**! All user resumes, contact info, and application histories are encrypted in the browser using **AES-256** (`CryptoJS`) with each user's personal PIN before saving to `data/users/<user_id>.json`.

## Setup (3 Simple Steps)

### 1. Upload to Your Existing GitHub Repo
Replace the files in your repository (`sganesan03/careeros-universal`) with `index.html`, `scraper_worker.py`, `requirements.txt`, `data/users/.gitkeep`, and `.github/workflows/discover_jobs.yml`.

### 2. Verify 3 Secrets in Repo Settings -> Secrets and variables -> Actions
- `GEMINI_API_KEY` = Your `AIzaSy...` key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
- `TELEGRAM_BOT_TOKEN` = Token from `@BotFather`
- `WEB_APP_URL` = `https://sganesan03.github.io/careeros-universal/`

### 3. Generate Your Zero-Config Magic Link
1. Open `https://sganesan03.github.io/careeros-universal/`.
2. Click **⚙️ Admin One-Time Magic Link Setup (Owner Only)** at the bottom.
3. Enter your GitHub Username, Repo Name (`careeros-universal`), Fine-Grained Token, and `AIzaSy...` Gemini Key -> click **🔗 Generate Zero-Config End-User Link**.
4. Share that Magic Link with anyone—they just enter their **Name/Email + 4-digit PIN** to unlock their encrypted workspace!
