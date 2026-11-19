# 🚀 CareerOS Universal — Multi-User AI Job & Outreach Platform

A 100% free, generic, multi-user career automation SaaS hosted on **GitHub Pages**, powered by **Google Gemini AI**, with isolated per-user JSON workspaces (`data/users/<user_id>.json`) and personal **Telegram Push Notifications**.

## Complete Setup Guide (100% Chrome Browser)

### Step 1: Create Private GitHub Repo & Upload Files
1. Open [github.com](https://github.com) -> click **+** -> **New repository**.
2. Name it `careeros-universal`, select **Private** (protects all users' resume data), and click **Create repository**.
3. Upload the entire `careeros-universal` folder contents (`index.html`, `scraper_worker.py`, `requirements.txt`, `data/users/.gitkeep`, and `.github/workflows/discover_jobs.yml`).

### Step 2: Host Free on GitHub Pages
1. Go to Repo **Settings -> Pages**.
2. Under **Source**, select **Deploy from a branch** -> Branch: `main` (`/root`) -> **Save**.
3. Copy your live Web App URL (`https://<username>.github.io/careeros-universal/`).

### Step 3: Add GitHub Actions Secrets & Permissions
1. Go to Repo **Settings -> Secrets and variables -> Actions -> New repository secret**:
   - `GEMINI_API_KEY` = Your free key from [aistudio.google.com](https://aistudio.google.com)
   - `TELEGRAM_BOT_TOKEN` = Your bot token from `@BotFather`
   - `WEB_APP_URL` = Your GitHub Pages URL from Step 2
2. Go to **Settings -> Actions -> General -> Workflow permissions** -> select **Read and write permissions** -> **Save**.

### Step 4: How Any User Can Register & Use It
1. Generate a GitHub Fine-Grained Token (**Profile Settings -> Developer settings -> Personal access tokens -> Fine-grained tokens**) with **Contents: Read & Write** and **Actions: Read & Write** for this repo.
2. Open your GitHub Pages Web App URL in Chrome -> go to **👤 User Account & API Setup**:
   - Enter any **Unique User Handle** (e.g., `selvaraj_98`, `arun_dev`, `priya_ui`). Each handle automatically creates its own isolated database file (`data/users/<handle>.json`).
   - Enter the Repo Owner, Repo Name, Token, and Gemini API Key -> click **Connect My Personal Workspace**.
3. Go to **🧠 AI Resume & Career Audit**:
   - Upload your PDF resume, set your target roles, blacklist keywords, and your personal **Telegram Chat ID** (from `@userinfobot`), then click **Save My Profile & Preferences** and **⚡ Trigger Live Scan**!
