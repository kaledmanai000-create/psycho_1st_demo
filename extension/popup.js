/**
 * Cognitive Shield TN - Popup Script (Real-Time Monitor)
 * Automatically scans viewport text every second.
 * When content changes, re-analyzes and updates the display live.
 */

const DEFAULT_API_BASE = "http://localhost:8000";
const DEFAULT_API_KEY = "changeme-cognitive-shield-key";
const SCAN_INTERVAL_MS = 1000; // 1 second
const MIN_TEXT_LENGTH = 10;

// Offline fallback patterns
const OFFLINE_PATTERNS = {
  phishing: [
    /click\s+here\s+to\s+verify/i,
    /your\s+account\s+(has\s+been|was)\s+(compromised|suspended|locked)/i,
    /enter\s+your\s+(password|bank|credit\s+card|cin)/i,
    /urgent.*verify\s+your\s+(identity|account)/i,
    /update\s+your\s+(payment|billing)\s+information/i,
    /congratulations.*you\s+(won|have\s+won)/i,
  ],
  manipulation: [
    /act\s+now\s+or/i,
    /share\s+(this|before)\s+(before|it\s+gets\s+deleted)/i,
    /you\s+should\s+be\s+ashamed/i,
    /everyone\s+(is|knows)/i,
    /if\s+you\s+(don'?t|really)\s+(care|love)/i,
  ],
  disinformation: [
    /they\s+don'?t\s+want\s+you\s+to\s+know/i,
    /mainstream\s+media\s+is\s+hiding/i,
    /miracle\s+cure/i,
    /government\s+is\s+secretly/i,
    /doctors?\s+(hate|don'?t\s+want)/i,
    /before\s+(they|it\s+gets?)\s+delete/i,
  ],
};

let apiBase = DEFAULT_API_BASE;
let apiKey = DEFAULT_API_KEY;

// DOM Elements
const liveStatus = document.getElementById("live-status");
const liveLabel = document.getElementById("live-label");
const loadingSection = document.getElementById("loading-section");
const resultsSection = document.getElementById("results-section");
const errorSection = document.getElementById("error-section");
const loggedSection = document.getElementById("logged-section");
const settingsBtn = document.getElementById("settings-btn");

const riskCard = document.getElementById("risk-card");
const riskScore = document.getElementById("risk-score");
const riskLabel = document.getElementById("risk-label");
const riskBar = document.getElementById("risk-bar");
const threatType = document.getElementById("threat-type");
const confidenceEl = document.getElementById("confidence");
const explanationList = document.getElementById("explanation-list");
const errorMessage = document.getElementById("error-message");

// State
let currentResult = null;
let currentText = "";
let lastTextHash = "";
let scanInterval = null;
let isAnalyzing = false;
let scanCount = 0;

// --- Init ---
(async function init() {
  await loadSettings();

  if (settingsBtn) {
    settingsBtn.addEventListener("click", () => {
      window.location.href = "settings.html";
    });
  }

  document.querySelectorAll(".btn-action").forEach((btn) => {
    btn.addEventListener("click", () => handleDecision(btn.dataset.decision));
  });

  // Start real-time monitoring
  startMonitoring();
})();

// --- Settings ---
function loadSettings() {
  return new Promise((resolve) => {
    if (typeof chrome !== "undefined" && chrome.storage) {
      chrome.storage.local.get(["backendUrl", "apiKey"], (data) => {
        apiBase = data.backendUrl || DEFAULT_API_BASE;
        apiKey = data.apiKey || DEFAULT_API_KEY;
        resolve();
      });
    } else {
      resolve();
    }
  });
}

// --- Real-Time Monitoring ---
function startMonitoring() {
  liveLabel.textContent = "Live monitor active";
  liveStatus.classList.add("active");

  // Run first scan immediately
  performScan();

  // Then scan every second
  scanInterval = setInterval(performScan, SCAN_INTERVAL_MS);
}

async function performScan() {
  if (isAnalyzing) return; // Skip if previous analysis still running

  try {
    const text = await extractViewportText();
    const hash = simpleHash(text);

    // Only re-analyze if content actually changed
    if (hash === lastTextHash) {
      scanCount++;
      liveLabel.textContent = `Monitoring... (${scanCount}s)`;
      return;
    }

    lastTextHash = hash;
    currentText = text;
    scanCount = 0;

    if (!text || text.length < MIN_TEXT_LENGTH) {
      liveLabel.textContent = "Waiting for content...";
      return;
    }

    // Analyze the new content
    isAnalyzing = true;
    liveLabel.textContent = "Analyzing new content...";

    let result;
    try {
      result = await analyzeText(text);
    } catch (apiErr) {
      result = offlineAnalyze(text);
    }

    currentResult = result;
    displayResults(result);

    // Show results, hide loading
    loadingSection.classList.add("hidden");
    resultsSection.classList.remove("hidden");
    errorSection.classList.add("hidden");

    // Re-enable action buttons for new content
    resetActionButtons();
    loggedSection.classList.add("hidden");

    liveLabel.textContent = "Live monitor active";
    isAnalyzing = false;
  } catch (err) {
    isAnalyzing = false;
    liveLabel.textContent = "Monitor active (page access limited)";
  }
}

// --- Text Extraction ---
function extractViewportText() {
  return new Promise((resolve, reject) => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (!tabs[0]) {
        reject(new Error("No active tab"));
        return;
      }

      chrome.tabs.sendMessage(tabs[0].id, { action: "extractViewportText" }, (response) => {
        if (chrome.runtime.lastError) {
          // Inject content script and retry
          chrome.scripting.executeScript(
            { target: { tabId: tabs[0].id }, files: ["content.js"] },
            () => {
              setTimeout(() => {
                chrome.tabs.sendMessage(tabs[0].id, { action: "extractViewportText" }, (resp) => {
                  resolve(resp?.text || "");
                });
              }, 300);
            }
          );
          return;
        }
        resolve(response?.text || "");
      });
    });
  });
}

// --- API Analysis ---
async function analyzeText(text) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 8000);

  try {
    const response = await fetch(`${apiBase}/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": apiKey,
      },
      body: JSON.stringify({ text: text.substring(0, 15000) }),
      signal: controller.signal,
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `Server error (${response.status})`);
    }

    return response.json();
  } finally {
    clearTimeout(timeout);
  }
}

function offlineAnalyze(text) {
  const explanations = ["Offline mode: limited analysis (backend unreachable)"];
  let maxScore = 0;
  let detectedType = "safe";

  for (const [category, patterns] of Object.entries(OFFLINE_PATTERNS)) {
    let matchCount = 0;
    for (const pattern of patterns) {
      if (pattern.test(text)) matchCount++;
    }
    if (matchCount > 0) {
      const score = Math.min(matchCount * 25, 80);
      explanations.push(`Detected ${matchCount} ${category} pattern(s)`);
      if (score > maxScore) {
        maxScore = score;
        detectedType = category;
      }
    }
  }

  return {
    risk_score: maxScore,
    threat_type: detectedType,
    explanation: explanations,
    confidence: maxScore > 0 ? 0.4 : 0.2,
    offline: true,
  };
}

// --- Decision Logging ---
async function handleDecision(decision) {
  if (!currentResult) return;

  document.querySelectorAll(".btn-action").forEach((btn) => {
    btn.disabled = true;
    btn.style.opacity = "0.5";
  });

  try {
    await fetch(`${apiBase}/log`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": apiKey,
      },
      body: JSON.stringify({
        input_text: currentText.substring(0, 5000),
        ai_decision: currentResult,
        user_decision: decision,
      }),
    });
  } catch (err) {
    console.warn("Could not log decision:", err);
  }

  loggedSection.classList.remove("hidden");
  // Buttons will re-enable on next content change
}

function resetActionButtons() {
  document.querySelectorAll(".btn-action").forEach((btn) => {
    btn.disabled = false;
    btn.style.opacity = "1";
  });
}

// --- UI Display ---
function displayResults(result) {
  const score = result.risk_score;

  riskScore.textContent = score;
  riskBar.style.width = `${score}%`;

  let level, labelText;
  if (score <= 25) {
    level = "low";
    labelText = "Low Risk";
  } else if (score <= 50) {
    level = "medium";
    labelText = "Medium Risk";
  } else if (score <= 75) {
    level = "high";
    labelText = "High Risk";
  } else {
    level = "critical";
    labelText = "Critical Risk";
  }

  if (result.offline) labelText += " (Offline)";

  riskCard.className = `card risk-${level}`;
  riskLabel.textContent = labelText;
  threatType.textContent = result.threat_type;
  confidenceEl.textContent = `Confidence: ${Math.round(result.confidence * 100)}%`;

  explanationList.innerHTML = "";
  if (result.explanation && result.explanation.length > 0) {
    result.explanation.forEach((exp) => {
      const li = document.createElement("li");
      li.textContent = exp;
      explanationList.appendChild(li);
    });
  } else {
    const li = document.createElement("li");
    li.textContent = "No specific threats identified.";
    explanationList.appendChild(li);
  }
}

// --- Helpers ---
function simpleHash(str) {
  if (!str) return "";
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const chr = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + chr;
    hash |= 0;
  }
  return String(hash);
}
