/**
 * Cognitive Shield TN - Popup Script
 * Handles UI interactions, API calls, and human-in-the-loop decision logging.
 */

const API_BASE = "http://localhost:8000";

// DOM Elements
const analyzeSection = document.getElementById("analyze-section");
const loadingSection = document.getElementById("loading-section");
const resultsSection = document.getElementById("results-section");
const errorSection = document.getElementById("error-section");
const loggedSection = document.getElementById("logged-section");

const analyzeBtn = document.getElementById("analyze-btn");
const retryBtn = document.getElementById("retry-btn");
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

// --- Event Listeners ---

analyzeBtn.addEventListener("click", handleAnalyze);
retryBtn.addEventListener("click", handleAnalyze);

document.querySelectorAll(".btn-action").forEach((btn) => {
  btn.addEventListener("click", () => handleDecision(btn.dataset.decision));
});

// --- Main Functions ---

async function handleAnalyze() {
  showSection("loading");

  try {
    // Extract text from current page via content script
    const text = await extractPageText();
    currentText = text;

    if (!text || text.length < 10) {
      showError("Not enough text content found on this page to analyze.");
      return;
    }

    // Call backend API
    const result = await analyzeText(text);
    currentResult = result;

    // Display results
    displayResults(result);
    showSection("results");
  } catch (err) {
    console.error("Analysis error:", err);
    showError(err.message || "Could not connect to the analysis server. Make sure the backend is running.");
  }
}

async function extractPageText() {
  return new Promise((resolve, reject) => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (!tabs[0]) {
        reject(new Error("No active tab found"));
        return;
      }

      chrome.tabs.sendMessage(tabs[0].id, { action: "extractText" }, (response) => {
        if (chrome.runtime.lastError) {
          // Fallback: try to inject content script and retry
          chrome.scripting.executeScript(
            { target: { tabId: tabs[0].id }, files: ["content.js"] },
            () => {
              setTimeout(() => {
                chrome.tabs.sendMessage(tabs[0].id, { action: "extractText" }, (resp) => {
                  if (resp && resp.text) {
                    resolve(resp.text);
                  } else {
                    reject(new Error("Could not extract text from this page."));
                  }
                });
              }, 200);
            }
          );
          return;
        }
        resolve(response?.text || "");
      });
    });
  });
}

async function analyzeText(text) {
  const response = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: text.substring(0, 15000) }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || `Server error (${response.status})`);
  }

  return response.json();
}

async function handleDecision(decision) {
  if (!currentResult) return;

  // Disable action buttons
  document.querySelectorAll(".btn-action").forEach((btn) => {
    btn.disabled = true;
    btn.style.opacity = "0.5";
  });

  try {
    await fetch(`${API_BASE}/log`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        input_text: currentText.substring(0, 5000),
        ai_decision: currentResult,
        user_decision: decision,
      }),
    });
  } catch (err) {
    console.warn("Could not log decision:", err);
  }

  // Show confirmation
  loggedSection.classList.remove("hidden");
}

// --- UI Functions ---

function displayResults(result) {
  const score = result.risk_score;

  // Risk score animation
  riskScore.textContent = score;
  riskBar.style.width = `${score}%`;

  // Risk level classification
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

  // Threat type
  threatType.textContent = result.threat_type;

  // Confidence
  confidenceEl.textContent = `Confidence: ${Math.round(result.confidence * 100)}%`;

  // Explanations
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

function showSection(section) {
  analyzeSection.classList.add("hidden");
  loadingSection.classList.add("hidden");
  resultsSection.classList.add("hidden");
  errorSection.classList.add("hidden");
  loggedSection.classList.add("hidden");

  switch (section) {
    case "analyze":
      analyzeSection.classList.remove("hidden");
      break;
    case "loading":
      loadingSection.classList.remove("hidden");
      break;
    case "results":
      resultsSection.classList.remove("hidden");
      break;
    case "error":
      errorSection.classList.remove("hidden");
      break;
  }
}

function showError(message) {
  errorMessage.textContent = message;
  showSection("error");
}
