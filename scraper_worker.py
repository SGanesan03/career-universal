import os
import re
import glob
import json
import hashlib
import urllib.parse
from datetime import datetime

import requests
import feedparser
from bs4 import BeautifulSoup
from google import genai
from google.genai import types

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
TG_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
WEB_APP_URL = os.environ.get("WEB_APP_URL", "").strip()

gemini = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
MODEL_ID = "gemini-2.5-flash"


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def send_telegram_alert(chat_id, text):
    if not TG_BOT_TOKEN or not chat_id:
        return
    payload = {
        "chat_id": str(chat_id).strip(),
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    if WEB_APP_URL:
        payload["reply_markup"] = json.dumps({
            "inline_keyboard": [[{"text": "🔓 Unlock CareerOS Vault", "url": WEB_APP_URL}]]
        })
    try:
        requests.post(f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage", json=payload, timeout=15)
    except Exception:
        pass


def make_hash(title, company, url):
    raw = f"{title.lower().strip()}|{company.lower().strip()}|{url.strip()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def fetch_linkedin_public_jobs(roles, locations):
    results = []
    loc = locations[0] if locations else "India"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    for role in roles[:3]:
        q = urllib.parse.quote(role)
        l = urllib.parse.quote(loc)
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={q}&location={l}&f_TPR=r86400&start=0"
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            for card in soup.select("li")[:8]:
                title_el = card.select_one("h3.base-search-card__title")
                comp_el = card.select_one("h4.base-search-card__subtitle")
                loc_el = card.select_one("span.job-search-card__location")
                link_el = card.select_one("a.base-card__full-link")
                if title_el and link_el:
                    title = title_el.get_text(strip=True)
                    company = comp_el.get_text(strip=True) if comp_el else "Company"
                    job_url = link_el["href"].split("?")[0]
                    results.append({
                        "hash": make_hash(title, company, job_url),
                        "title": title,
                        "company": company,
                        "location": loc_el.get_text(strip=True) if loc_el else loc,
                        "source": "LinkedIn_Public",
                        "apply_url": job_url,
                        "description": f"{title} opening at {company} ({loc}). Public LinkedIn job listing."
                    })
        except Exception:
            continue
    return results


def fetch_remote_feeds(roles):
    results = []
    try:
        r = requests.get("https://remoteok.com/api", headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        if r.status_code == 200:
            for item in r.json()[1:40]:
                title = item.get("position", "")
                if any(role.lower() in title.lower() for role in roles):
                    url = item.get("apply_url") or item.get("url")
                    comp = item.get("company", "Company")
                    desc = BeautifulSoup(item.get("description", ""), "html.parser").get_text(" ")
                    results.append({
                        "hash": make_hash(title, comp, url),
                        "title": title,
                        "company": comp,
                        "location": item.get("location", "Remote"),
                        "source": "RemoteOK",
                        "apply_url": url,
                        "description": desc
                    })
    except Exception:
        pass

    for rss in ["https://weworkremotely.com/categories/remote-programming-jobs.rss", "https://jobicy.com/feed/newjobs"]:
        try:
            feed = feedparser.parse(rss)
            for entry in feed.entries[:25]:
                title = entry.get("title", "")
                if any(role.lower() in title.lower() for role in roles):
                    link = entry.get("link", "")
                    comp = title.split(":")[0] if ":" in title else "Hiring Team"
                    desc = BeautifulSoup(entry.get("summary", ""), "html.parser").get_text(" ")
                    results.append({
                        "hash": make_hash(title, comp, link),
                        "title": title,
                        "company": comp,
                        "location": "Remote",
                        "source": "RSS_Feed",
                        "apply_url": link,
                        "description": desc
                    })
        except Exception:
            continue
    return results


def evaluate_job_with_gemini(skills, job):
    emails_found = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", job["description"])
    prompt = f"""
    Match this job against the candidate's skills and classify into ONE category:
    - "A": Direct apply link with no recruiter email and no screening questions.
    - "B": Mentions mandatory screening questions (notice period, expected CTC, years in skill).
    - "C": Contains a recruiter email address asking candidates to email their resume.
    - "D": Social hiring post asking candidates to comment.

    Candidate Skills: {skills}
    Job: {job["title"]} at {job["company"]}
    Detected Emails: {emails_found}
    Description: {job["description"][:4000]}

    Return strictly valid JSON:
    {{
      "match_score": 0,
      "matched_skills": ["skill1", "skill2"],
      "category": "A",
      "recruiter_email": null,
      "mandatory_questions": [],
      "jd_summary": "Crisp 2-line role summary"
    }}
    """
    resp = gemini.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    data = json.loads(resp.text)
    if emails_found and not data.get("recruiter_email"):
        data["recruiter_email"] = emails_found[0]
        data["category"] = "C"
    return data


def process_encrypted_vault(user_path):
    vault = load_json(user_path, None)
    if not vault or not gemini:
        return

    uid = vault.get("user_id", os.path.basename(user_path))
    idx = vault.get("match_index", {})
    skills = idx.get("skills", [])
    if not skills:
        return

    roles = idx.get("target_roles") or ["Developer"]
    locations = idx.get("locations") or ["Remote"]
    blacklist = [b.lower() for b in idx.get("blacklist", [])]
    seen = set(idx.get("seen_hashes", []))
    pending = vault.setdefault("pending_jobs", {})
    seen.update(pending.keys())

    candidates = fetch_linkedin_public_jobs(roles, locations) + fetch_remote_feeds(roles)
    newly_matched = []

    for job in candidates:
        if len(newly_matched) >= 6:
            break
        h = job["hash"]
        if h in seen:
            continue
        blob = f"{job['title']} {job['description']}".lower()
        if any(bad in blob for bad in blacklist):
            continue

        analysis = evaluate_job_with_gemini(skills, job)
        if analysis.get("match_score", 0) < 55:
            continue

        job.update(analysis)
        pending[h] = job
        seen.add(h)
        newly_matched.append(f"• *{job['title']}* @ {job['company']} ({job['match_score']}% | Cat {job['category']})")

    save_json(user_path, vault)

    tg_chat_id = idx.get("telegram_chat_id", "")
    if newly_matched and tg_chat_id:
        send_telegram_alert(
            tg_chat_id,
            f"🎯 *{len(newly_matched)} New Matched Jobs for {uid}!*

"
            + "
".join(newly_matched)
            + "

Open *CareerOS Vault* with your PIN to Tailor Resume or Smart Apply."
        )


if __name__ == "__main__":
    user_files = glob.glob("data/users/*.json")
    print(f"Scanning {len(user_files)} encrypted user vaults.")
    for path in user_files:
        if os.path.basename(path) == ".gitkeep":
            continue
        try:
            process_encrypted_vault(path)
        except Exception as e:
            print(f"Error processing {path}: {e}")
