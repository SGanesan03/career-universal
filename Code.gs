// ============================================================================
// CareerOS Zero-Config Bridge (Google Apps Script - 100% Free)
// Paste this entire code into script.google.com -> Deploy as Web App
// ============================================================================

const PROPS = PropertiesService.getScriptProperties();

function doPost(e) {
  try {
    const req = JSON.parse(e.postData.contents);
    const action = req.action;

    if (action === "gemini") {
      return jsonOut(callGeminiProxy(req.prompt, req.expectJson));
    } else if (action === "getUser") {
      return jsonOut(getUserFromGitHub(req.userId));
    } else if (action === "saveUser") {
      return jsonOut(saveUserToGitHub(req.userId, req.userData, req.message));
    } else if (action === "triggerScan") {
      return jsonOut(triggerGitHubScan());
    }
    return jsonOut({ ok: false, error: "Unknown action" });
  } catch (err) {
    return jsonOut({ ok: false, error: err.toString() });
  }
}

function jsonOut(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function callGeminiProxy(prompt, expectJson) {
  const apiKey = PROPS.getProperty("GEMINI_API_KEY");
  if (!apiKey) return { ok: false, error: "Admin GEMINI_API_KEY not configured in Apps Script." };

  const models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"];
  let lastErr = "";

  for (let i = 0; i < models.length; i++) {
    const url = "https://generativelanguage.googleapis.com/v1beta/models/" + models[i] + ":generateContent?key=" + apiKey;
    const payload = { contents: [{ parts: [{ text: prompt }] }] };
    if (expectJson) {
      payload.generationConfig = { responseMimeType: "application/json" };
    }

    const res = UrlFetchApp.fetch(url, {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    });

    const data = JSON.parse(res.getContentText());
    if (res.getResponseCode() === 200 && data.candidates && data.candidates[0]) {
      let raw = data.candidates[0].content.parts[0].text.trim();
      if (expectJson) {
        raw = raw.replace(/^```json\s*/i, "").replace(/```\s*$/i, "");
        return { ok: true, data: JSON.parse(raw) };
      }
      return { ok: true, data: raw };
    }
    lastErr = (data.error && data.error.message) ? data.error.message : ("HTTP " + res.getResponseCode());
  }
  return { ok: false, error: lastErr };
}

function getUserFromGitHub(userId) {
  const owner = PROPS.getProperty("GH_OWNER");
  const repo = PROPS.getProperty("GH_REPO");
  const token = PROPS.getProperty("GH_TOKEN");
  const safeId = userId.toLowerCase().replace(/[^a-z0-9_-]/g, "_");
  const path = "data/users/" + safeId + ".json";

  const url = "https://api.github.com/repos/" + owner + "/" + repo + "/contents/" + path + "?t=" + Date.now();
  const res = UrlFetchApp.fetch(url, {
    headers: { Authorization: "Bearer " + token, Accept: "application/vnd.github.v3+json" },
    muteHttpExceptions: true
  });

  if (res.getResponseCode() === 200) {
    const json = JSON.parse(res.getContentText());
    const decoded = Utilities.newBlob(Utilities.base64Decode(json.content.replace(/\n/g, ""))).getDataAsString("UTF-8");
    return { ok: true, exists: true, userData: JSON.parse(decoded) };
  }
  return { ok: true, exists: false };
}

function saveUserToGitHub(userId, userData, commitMsg) {
  const owner = PROPS.getProperty("GH_OWNER");
  const repo = PROPS.getProperty("GH_REPO");
  const token = PROPS.getProperty("GH_TOKEN");
  const safeId = userId.toLowerCase().replace(/[^a-z0-9_-]/g, "_");
  const path = "data/users/" + safeId + ".json";
  const apiUrl = "https://api.github.com/repos/" + owner + "/" + repo + "/contents/" + path;

  // Fetch latest SHA first to avoid conflict
  let sha = null;
  const check = UrlFetchApp.fetch(apiUrl + "?t=" + Date.now(), {
    headers: { Authorization: "Bearer " + token, Accept: "application/vnd.github.v3+json" },
    muteHttpExceptions: true
  });
  if (check.getResponseCode() === 200) {
    sha = JSON.parse(check.getContentText()).sha;
  }

  const encoded = Utilities.base64Encode(Utilities.newBlob(JSON.stringify(userData, null, 2)).getBytes());
  const body = { message: commitMsg || ("update user: " + safeId), content: encoded };
  if (sha) body.sha = sha;

  const putRes = UrlFetchApp.fetch(apiUrl, {
    method: "put",
    contentType: "application/json",
    headers: { Authorization: "Bearer " + token, Accept: "application/vnd.github.v3+json" },
    payload: JSON.stringify(body),
    muteHttpExceptions: true
  });

  return { ok: putRes.getResponseCode() === 200 || putRes.getResponseCode() === 201 };
}

function triggerGitHubScan() {
  const owner = PROPS.getProperty("GH_OWNER");
  const repo = PROPS.getProperty("GH_REPO");
  const token = PROPS.getProperty("GH_TOKEN");
  const url = "https://api.github.com/repos/" + owner + "/" + repo + "/actions/workflows/discover_jobs.yml/dispatches";

  const res = UrlFetchApp.fetch(url, {
    method: "post",
    contentType: "application/json",
    headers: { Authorization: "Bearer " + token, Accept: "application/vnd.github.v3+json" },
    payload: JSON.stringify({ ref: "main" }),
    muteHttpExceptions: true
  });

  return { ok: res.getResponseCode() === 204 };
}
