/**
 * Cognitive Shield TN - In-Page Widget
 * Injects a floating monitor in the bottom-right of every page.
 * Shows a center-screen alert when risk > 50.
 * Scans viewport text every 1 second.
 */

(() => {
  // Prevent double injection
  if (document.getElementById("cs-widget")) return;

  const DEFAULT_API_BASE = "http://localhost:8000";
  const DEFAULT_API_KEY = "changeme-cognitive-shield-key";
  const SCAN_INTERVAL = 1000;
  const HIGH_RISK_THRESHOLD = 50;

  let apiBase = DEFAULT_API_BASE;
  let apiKey = DEFAULT_API_KEY;
  let lastTextHash = "";
  let isAnalyzing = false;
  let currentResult = null;
  let currentText = "";
  let alertDismissedForHash = "";

  // ---- Build the DOM ----
  function buildWidget() {
    // Bottom-right widget
    const widget = document.createElement("div");
    widget.id = "cs-widget";
    widget.innerHTML = `
      <div class="cs-pill" id="cs-pill">
        <div class="cs-dot safe" id="cs-dot"></div>
        <span class="cs-pill-label" id="cs-pill-label">Scanning...</span>
        <span class="cs-pill-score" id="cs-pill-score">--</span>
      </div>
      <div class="cs-card" id="cs-card">
        <div class="cs-card-header">
          <span class="cs-title">&#128737; Cognitive Shield TN</span>
          <button class="cs-close" id="cs-close">&times;</button>
        </div>
        <div class="cs-risk" id="cs-risk-section">
          <div class="cs-risk-score" id="cs-risk-score">0</div>
          <div class="cs-risk-label" id="cs-risk-label">Scanning...</div>
          <div class="cs-risk-bar"><div class="cs-risk-bar-fill" id="cs-risk-bar-fill" style="width:0%"></div></div>
        </div>
        <div class="cs-meta">
          <span id="cs-threat-type">--</span>
          <span id="cs-confidence">--</span>
        </div>
        <div class="cs-explanations" id="cs-explanations">
          <ul id="cs-explanation-list"></ul>
        </div>
        <div class="cs-actions" id="cs-actions">
          <button class="cs-act-ignore" data-decision="ignore">&#10004; Ignore</button>
          <button class="cs-act-investigate" data-decision="investigate">&#128270; Investigate</button>
          <button class="cs-act-threat" data-decision="mark_as_threat">&#9888; Threat</button>
        </div>
        <div class="cs-logged" id="cs-logged">&#9989; Decision logged</div>
      </div>
    `;
    document.body.appendChild(widget);

    // Center-screen alert overlay
    const overlay = document.createElement("div");
    overlay.id = "cs-alert-overlay";
    overlay.innerHTML = `
      <div id="cs-alert-box">
        <div class="cs-alert-icon">&#9888;</div>
        <div class="cs-alert-title">HIGH RISK DETECTED</div>
        <div class="cs-alert-subtitle">This page may contain dangerous content</div>
        <div class="cs-alert-score" id="cs-alert-score">0</div>
        <div class="cs-alert-type" id="cs-alert-type">--</div>
        <button class="cs-alert-dismiss" id="cs-alert-dismiss">I Understand</button>
      </div>
    `;
    document.body.appendChild(overlay);

    // Event listeners
    document.getElementById("cs-pill").addEventListener("click", () => {
      widget.classList.add("expanded");
    });
    document.getElementById("cs-close").addEventListener("click", (e) => {
      e.stopPropagation();
      widget.classList.remove("expanded");
    });
    document.getElementById("cs-alert-dismiss").addEventListener("click", () => {
      overlay.classList.remove("visible");
      alertDismissedForHash = lastTextHash;
    });

    // Decision buttons
    document.querySelectorAll("#cs-actions button").forEach((btn) => {
      btn.addEventListener("click", () => handleDecision(btn.dataset.decision));
    });
  }

  // ---- Viewport text extraction ----
  function extractViewportText() {
    const vh = window.innerHeight;
    const vw = window.innerWidth;
    const texts = [];
    const seen = new Set();

    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode: (node) => {
        const p = node.parentElement;
        if (!p) return NodeFilter.FILTER_REJECT;
        const tag = p.tagName.toLowerCase();
        if (["script","style","noscript","iframe","svg","meta","link"].includes(tag)) return NodeFilter.FILTER_REJECT;
        // Skip our own widget
        if (p.closest("#cs-widget") || p.closest("#cs-alert-overlay")) return NodeFilter.FILTER_REJECT;
        const t = node.textContent.trim();
        if (!t || t.length < 2) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      },
    });

    let n;
    while ((n = walker.nextNode())) {
      const p = n.parentElement;
      if (!p) continue;
      const r = p.getBoundingClientRect();
      if (r.bottom > 0 && r.top < vh && r.right > 0 && r.left < vw && r.width > 0 && r.height > 0) {
        const style = window.getComputedStyle(p);
        if (style.display === "none" || style.visibility === "hidden" || style.opacity === "0") continue;
        const t = n.textContent.trim();
        if (t.length >= 2 && !seen.has(t)) {
          seen.add(t);
          texts.push(t);
        }
      }
    }

    return texts.join(" ").replace(/\s+/g, " ").trim().substring(0, 15000);
  }

  // ---- Simple hash ----
  function simpleHash(str) {
    if (!str) return "";
    let h = 0;
    for (let i = 0; i < str.length; i++) {
      h = ((h << 5) - h) + str.charCodeAt(i);
      h |= 0;
    }
    return String(h);
  }

  // ---- Risk level helper ----
  function riskLevel(score) {
    if (score <= 25) return "safe";
    if (score <= 50) return "medium";
    if (score <= 75) return "high";
    return "critical";
  }

  // ---- API call ----
  async function analyzeText(text) {
    const ctrl = new AbortController();
    const timeout = setTimeout(() => ctrl.abort(), 8000);
    try {
      const resp = await fetch(`${apiBase}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-API-Key": apiKey },
        body: JSON.stringify({ text: text.substring(0, 15000) }),
        signal: ctrl.signal,
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      return await resp.json();
    } finally {
      clearTimeout(timeout);
    }
  }

  // ---- Offline fallback ----
  function offlineAnalyze(text) {
    const patterns = {
      phishing: [/click\s+here\s+to\s+verify/i, /your\s+account\s+(has\s+been|was)\s+(compromised|suspended)/i, /enter\s+your\s+(password|bank|credit)/i, /urgent.*verify/i],
      manipulation: [/act\s+now\s+or/i, /share\s+(this|before)/i, /you\s+should\s+be\s+ashamed/i],
      disinformation: [/they\s+don'?t\s+want\s+you\s+to\s+know/i, /mainstream\s+media\s+is\s+hiding/i, /miracle\s+cure/i, /government\s+is\s+secretly/i],
    };
    let maxScore = 0, detectedType = "safe";
    const explanations = [];
    for (const [cat, pats] of Object.entries(patterns)) {
      let m = 0;
      for (const p of pats) if (p.test(text)) m++;
      if (m > 0) {
        const s = Math.min(m * 25, 80);
        explanations.push(`${m} ${cat} pattern(s) detected`);
        if (s > maxScore) { maxScore = s; detectedType = cat; }
      }
    }
    return { risk_score: maxScore, threat_type: detectedType, explanation: explanations, confidence: maxScore > 0 ? 0.4 : 0.2 };
  }

  // ---- Decision logging ----
  async function handleDecision(decision) {
    if (!currentResult) return;
    const btns = document.querySelectorAll("#cs-actions button");
    btns.forEach((b) => { b.disabled = true; });
    try {
      await fetch(`${apiBase}/log`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-API-Key": apiKey },
        body: JSON.stringify({ input_text: currentText.substring(0, 5000), ai_decision: currentResult, user_decision: decision }),
      });
    } catch (e) { /* silent */ }
    document.getElementById("cs-logged").style.display = "block";
  }

  // ---- Update UI ----
  function updateWidget(result) {
    const score = result.risk_score;
    const level = riskLevel(score);

    // Pill
    const dot = document.getElementById("cs-dot");
    dot.className = `cs-dot ${level}`;
    document.getElementById("cs-pill-label").textContent =
      level === "safe" ? "Safe" : level === "medium" ? "Medium" : level === "high" ? "High Risk" : "DANGER";
    document.getElementById("cs-pill-score").textContent = score;
    document.getElementById("cs-pill-score").className = `cs-pill-score cs-color-${level}`;

    // Card
    document.getElementById("cs-risk-score").textContent = score;
    document.getElementById("cs-risk-score").className = `cs-risk-score cs-color-${level}`;
    document.getElementById("cs-risk-label").textContent =
      level === "safe" ? "Low Risk" : level === "medium" ? "Medium Risk" : level === "high" ? "High Risk" : "Critical Risk";
    document.getElementById("cs-risk-label").className = `cs-risk-label cs-color-${level}`;

    const barFill = document.getElementById("cs-risk-bar-fill");
    barFill.style.width = `${score}%`;
    barFill.className = `cs-risk-bar-fill cs-fill-${level}`;

    document.getElementById("cs-threat-type").textContent = result.threat_type;
    document.getElementById("cs-confidence").textContent = `${Math.round(result.confidence * 100)}% conf.`;

    // Explanations
    const list = document.getElementById("cs-explanation-list");
    list.innerHTML = "";
    if (result.explanation && result.explanation.length > 0) {
      result.explanation.forEach((e) => {
        const li = document.createElement("li");
        li.textContent = e;
        list.appendChild(li);
      });
    } else {
      const li = document.createElement("li");
      li.textContent = "No specific threats identified.";
      list.appendChild(li);
    }

    // Reset action buttons
    document.querySelectorAll("#cs-actions button").forEach((b) => { b.disabled = false; });
    document.getElementById("cs-logged").style.display = "none";

    // Center alert for high risk
    if (score > HIGH_RISK_THRESHOLD && alertDismissedForHash !== lastTextHash) {
      const overlay = document.getElementById("cs-alert-overlay");
      document.getElementById("cs-alert-score").textContent = score;
      document.getElementById("cs-alert-type").textContent = result.threat_type;
      overlay.classList.add("visible");
    }
  }

  // ---- Main scan loop ----
  async function scan() {
    if (isAnalyzing) return;

    const text = extractViewportText();
    const hash = simpleHash(text);

    if (hash === lastTextHash) return;
    if (!text || text.length < 10) return;

    lastTextHash = hash;
    currentText = text;
    isAnalyzing = true;

    try {
      let result;
      try {
        result = await analyzeText(text);
      } catch (e) {
        result = offlineAnalyze(text);
      }
      currentResult = result;
      updateWidget(result);
    } catch (e) {
      // silent
    }

    isAnalyzing = false;
  }

  // ---- Load settings and start ----
  function loadSettingsAndStart() {
    if (typeof chrome !== "undefined" && chrome.storage) {
      chrome.storage.local.get(["backendUrl", "apiKey"], (data) => {
        apiBase = data.backendUrl || DEFAULT_API_BASE;
        apiKey = data.apiKey || DEFAULT_API_KEY;
        start();
      });
    } else {
      start();
    }
  }

  function start() {
    buildWidget();
    scan();
    setInterval(scan, SCAN_INTERVAL);
  }

  // Go
  loadSettingsAndStart();
})();
