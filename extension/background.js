/**
 * Cognitive Shield TN - Background Service Worker
 * Proxies API calls for content scripts (which can't make cross-origin requests in MV3).
 */

const DEFAULT_API = "http://localhost:8000";
const DEFAULT_KEY = "changeme-cognitive-shield-key";

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "analyze") {
    handleAnalyze(msg.text).then(sendResponse).catch(e => sendResponse({ error: e.message }));
    return true; // keep channel open for async
  }
  if (msg.type === "logDecision") {
    handleLog(msg.payload).then(sendResponse).catch(e => sendResponse({ error: e.message }));
    return true;
  }
});

async function getSettings() {
  return new Promise(resolve => {
    chrome.storage.local.get(["backendUrl", "apiKey"], d => {
      resolve({
        api: d.backendUrl || DEFAULT_API,
        key: d.apiKey || DEFAULT_KEY
      });
    });
  });
}

async function handleAnalyze(text) {
  const { api, key } = await getSettings();
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 8000);
  try {
    const resp = await fetch(`${api}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text.substring(0, 15000) }),
      signal: controller.signal
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const result = await resp.json();
    // Store result for popup
    chrome.storage.local.set({
      csLastResult: result,
      csLastScore: result.risk_score,
      csLastUpdate: Date.now()
    });
    return result;
  } catch (e) {
    return { error: e.message };
  } finally {
    clearTimeout(timeout);
  }
}

async function handleLog(payload) {
  const { api, key } = await getSettings();
  try {
    await fetch(`${api}/log`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    return { ok: true };
  } catch (e) {
    return { error: e.message };
  }
}
