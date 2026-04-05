/**
 * Cognitive Shield TN - Dashboard Application
 */

const API_BASE = window.location.hostname === "localhost"
  ? "http://localhost:8000"
  : `${window.location.protocol}//${window.location.hostname}:8000`;

const API_KEY = "changeme-cognitive-shield-key";

const headers = {
  "Content-Type": "application/json",
  "X-API-Key": API_KEY,
};

// --- Init ---
document.addEventListener("DOMContentLoaded", () => {
  loadAnalytics();
  loadHistory();

  document.getElementById("export-btn").addEventListener("click", handleExport);
  document.getElementById("retrain-btn").addEventListener("click", handleRetrain);
  document.getElementById("refresh-btn").addEventListener("click", () => {
    loadAnalytics();
    loadHistory();
  });
  document.getElementById("history-limit").addEventListener("change", loadHistory);
  document.getElementById("history-filter").addEventListener("input", filterHistory);
});

// --- Analytics ---
async function loadAnalytics() {
  try {
    const resp = await fetch(`${API_BASE}/analytics`, { headers });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();

    document.getElementById("total-analyses").textContent = data.total_analyses;
    document.getElementById("avg-risk").textContent = data.avg_risk_score;
    document.getElementById("avg-confidence").textContent = `${Math.round(data.avg_confidence * 100)}%`;

    // Count non-safe threats
    const threats = Object.entries(data.threat_distribution)
      .filter(([k]) => k !== "safe")
      .reduce((sum, [, v]) => sum + v, 0);
    document.getElementById("threats-count").textContent = threats;

    renderBarChart("threat-chart", data.threat_distribution, {
      safe: "#22c55e", phishing: "#ef4444", manipulation: "#f59e0b", disinformation: "#8b5cf6",
    });
    renderBarChart("decision-chart", data.decision_breakdown, {
      ignore: "#22c55e", investigate: "#f59e0b", mark_as_threat: "#ef4444",
    });
    renderBarChart("risk-chart", data.risk_distribution, {
      low: "#22c55e", medium: "#f59e0b", high: "#f97316", critical: "#ef4444",
    });
    renderTimeline("timeline-chart", data.timeline);
  } catch (err) {
    console.error("Failed to load analytics:", err);
    showStatus("Failed to load analytics. Is the backend running?", "error");
  }
}

// --- History ---
let allLogs = [];

async function loadHistory() {
  const limit = document.getElementById("history-limit").value;
  try {
    const resp = await fetch(`${API_BASE}/log/history?limit=${limit}`, { headers });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    allLogs = data.logs || [];
    renderHistory(allLogs);
  } catch (err) {
    console.error("Failed to load history:", err);
    document.getElementById("history-body").innerHTML =
      '<tr><td colspan="7" class="empty-msg">Failed to load history.</td></tr>';
  }
}

function filterHistory() {
  const query = document.getElementById("history-filter").value.toLowerCase();
  const filtered = allLogs.filter(
    (log) => log.threat_type.toLowerCase().includes(query) || log.user_decision.toLowerCase().includes(query)
  );
  renderHistory(filtered);
}

function renderHistory(logs) {
  const tbody = document.getElementById("history-body");
  if (!logs.length) {
    tbody.innerHTML = '<tr><td colspan="7" class="empty-msg">No records found.</td></tr>';
    return;
  }

  tbody.innerHTML = logs
    .map(
      (log) => `
    <tr>
      <td>${log.id}</td>
      <td class="text-preview" title="${escapeHtml(log.input_text)}">${escapeHtml(log.input_text)}</td>
      <td><span class="risk-badge risk-${getRiskLevel(log.risk_score)}">${log.risk_score}</span></td>
      <td><span class="threat-badge threat-${log.threat_type}">${log.threat_type}</span></td>
      <td>${Math.round(log.confidence * 100)}%</td>
      <td><span class="decision-badge decision-${log.user_decision}">${log.user_decision}</span></td>
      <td>${new Date(log.timestamp).toLocaleString()}</td>
    </tr>`
    )
    .join("");
}

// --- Actions ---
async function handleExport() {
  try {
    const resp = await fetch(`${API_BASE}/log/export`, { headers });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "cognitive_shield_logs.csv";
    a.click();
    URL.revokeObjectURL(url);
    showStatus("CSV exported successfully!", "success");
  } catch (err) {
    showStatus("Export failed: " + err.message, "error");
  }
}

async function handleRetrain() {
  const btn = document.getElementById("retrain-btn");
  btn.disabled = true;
  btn.textContent = "Retraining...";
  try {
    const resp = await fetch(`${API_BASE}/model/retrain`, { method: "POST", headers });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.detail || "Retrain failed");
    showStatus(
      `Model retrained! Added ${data.new_samples_added} new samples (total: ${data.total_training_samples}).`,
      "success"
    );
  } catch (err) {
    showStatus("Retrain failed: " + err.message, "error");
  } finally {
    btn.disabled = false;
    btn.textContent = "Retrain Model";
  }
}

// --- Chart Rendering (Pure CSS bars) ---
function renderBarChart(containerId, data, colorMap) {
  const container = document.getElementById(containerId);
  if (!data || !Object.keys(data).length) {
    container.innerHTML = '<p class="empty-chart">No data yet</p>';
    return;
  }

  const maxVal = Math.max(...Object.values(data), 1);
  container.innerHTML = Object.entries(data)
    .map(
      ([label, value]) => `
    <div class="bar-row">
      <span class="bar-label">${label}</span>
      <div class="bar-track">
        <div class="bar-fill" style="width: ${(value / maxVal) * 100}%; background: ${colorMap[label] || '#6366f1'}"></div>
      </div>
      <span class="bar-value">${value}</span>
    </div>`
    )
    .join("");
}

function renderTimeline(containerId, timeline) {
  const container = document.getElementById(containerId);
  if (!timeline || !timeline.length) {
    container.innerHTML = '<p class="empty-chart">No data in the last 30 days</p>';
    return;
  }

  const maxVal = Math.max(...timeline.map((t) => t.count), 1);
  container.innerHTML = `<div class="timeline-bars">${timeline
    .map(
      (t) => `
    <div class="timeline-bar-wrapper" title="${t.date}: ${t.count} analyses">
      <div class="timeline-bar" style="height: ${(t.count / maxVal) * 100}%"></div>
      <span class="timeline-date">${t.date.slice(5)}</span>
    </div>`
    )
    .join("")}</div>`;
}

// --- Helpers ---
function getRiskLevel(score) {
  if (score <= 25) return "low";
  if (score <= 50) return "medium";
  if (score <= 75) return "high";
  return "critical";
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str || "";
  return div.innerHTML;
}

function showStatus(message, type) {
  const el = document.getElementById("action-status");
  el.textContent = message;
  el.className = `action-status ${type}`;
  el.classList.remove("hidden");
  setTimeout(() => el.classList.add("hidden"), 5000);
}
