/**
 * Cognitive Shield TN - Popup Script
 * Reads real-time results from widget.js via chrome.storage.local.
 * The widget (content script) does all the scanning and API calls.
 * This popup just displays the latest result.
 */

const DEFAULT_API_BASE = "http://localhost:8000";
const DEFAULT_API_KEY = "changeme-cognitive-shield-key";

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

let currentResult = null;
let pollInterval = null;

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

  // Start polling storage for widget results
  startPolling();
})();

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

// --- Poll storage for widget results ---
function startPolling() {
  liveLabel.textContent = "Connecting to monitor...";
  liveStatus.classList.add("active");
  readResult();
  pollInterval = setInterval(readResult, 1000);
}

function readResult() {
  if (typeof chrome === "undefined" || !chrome.storage) return;
  chrome.storage.local.get(["csLastResult", "csLastUpdate"], (data) => {
    if (!data.csLastResult) {
      liveLabel.textContent = "Waiting for first scan...";
      return;
    }

    const age = Date.now() - (data.csLastUpdate || 0);
    const result = data.csLastResult;

    // Only update if we have a result
    currentResult = result;
    displayResults(result);

    loadingSection.classList.add("hidden");
    resultsSection.classList.remove("hidden");
    errorSection.classList.add("hidden");

    if (age < 5000) {
      liveLabel.textContent = "Live monitor active";
    } else {
      liveLabel.textContent = `Last scan ${Math.round(age / 1000)}s ago`;
    }
  });
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
        input_text: "viewport-text",
        ai_decision: currentResult,
        user_decision: decision,
      }),
    });
  } catch (err) {
    console.warn("Could not log decision:", err);
  }

  loggedSection.classList.remove("hidden");
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
