/**
 * Cognitive Shield TN - In-Page Widget v2
 * 3 modes based on risk score:
 *   < 30  → Small circle with % in bottom-right
 *   30-50 → Expanded text explanation card in bottom-right
 *   > 50  → Big center-screen alert popup
 */
(() => {
  if (document.getElementById("cs-widget")) return;

  const DEFAULT_API = "http://localhost:8000";
  const DEFAULT_KEY = "changeme-cognitive-shield-key";
  const SCAN_MS = 1000;

  let lastHash = "";
  let busy = false;
  let currentResult = null;
  let currentText = "";
  let alertDismissedHash = "";

  // ===== Build DOM =====
  function build() {
    const w = document.createElement("div");
    w.id = "cs-widget";

    // --- Mode 1: Circle (< 30) ---
    const circ = 2 * Math.PI * 24;
    w.innerHTML = `
      <div id="cs-circle">
        <svg viewBox="0 0 56 56">
          <circle class="cs-ring-bg" cx="28" cy="28" r="24"/>
          <circle class="cs-ring-fill" id="cs-ring" cx="28" cy="28" r="24"
            stroke-dasharray="${circ}" stroke-dashoffset="${circ}"/>
        </svg>
        <span class="cs-circle-score" id="cs-circle-score">0</span>
        <span class="cs-circle-pct">%</span>
      </div>

      <div id="cs-explain">
        <div class="cs-explain-header">
          <div class="cs-explain-title">&#9888;&#65039; Caution</div>
          <span class="cs-explain-score" id="cs-explain-score">0</span>
        </div>
        <div class="cs-explain-bar"><div class="cs-explain-bar-fill" id="cs-explain-bar" style="width:0%"></div></div>
        <div class="cs-explain-body">
          <div class="cs-explain-label">What we found</div>
          <div class="cs-explain-text" id="cs-explain-text">Analyzing...</div>
          <span class="cs-explain-type" id="cs-explain-type">--</span>
        </div>
        <div class="cs-explain-actions" id="cs-explain-actions">
          <button class="cs-btn-ignore" data-d="ignore">&#10004; Ignore</button>
          <button class="cs-btn-investigate" data-d="investigate">&#128270; Investigate</button>
          <button class="cs-btn-threat" data-d="mark_as_threat">&#9888; Threat</button>
        </div>
        <div class="cs-explain-logged" id="cs-explain-logged">&#9989; Decision logged</div>
      </div>
    `;
    document.body.appendChild(w);

    // --- Mode 3: Big alert overlay (> 50) ---
    const ov = document.createElement("div");
    ov.id = "cs-alert-overlay";
    ov.innerHTML = `
      <div id="cs-alert-box">
        <div class="cs-alert-top">
          <div class="cs-alert-icon">&#128680;</div>
          <div class="cs-alert-title">HIGH RISK DETECTED</div>
          <div class="cs-alert-subtitle">This page may contain dangerous content</div>
          <div class="cs-alert-score-ring">
            <div class="cs-alert-score-circle">
              <span class="cs-alert-score-num" id="cs-alert-score">0</span>
              <span class="cs-alert-score-label">Risk Score</span>
            </div>
          </div>
          <span class="cs-alert-type-badge" id="cs-alert-type">--</span>
        </div>
        <div class="cs-alert-body">
          <div class="cs-alert-explain-title">Why this was flagged</div>
          <ul class="cs-alert-explain-list" id="cs-alert-explain-list"></ul>
        </div>
        <div class="cs-alert-actions" id="cs-alert-actions">
          <button class="cs-alert-act-ignore" data-d="ignore">&#10004; Ignore</button>
          <button class="cs-alert-act-investigate" data-d="investigate">&#128270; Investigate</button>
          <button class="cs-alert-act-threat" data-d="mark_as_threat">&#9888; Threat</button>
        </div>
        <div class="cs-alert-logged" id="cs-alert-logged">&#9989; Decision logged</div>
      </div>
    `;
    document.body.appendChild(ov);

    // Click outside alert box to dismiss
    ov.addEventListener("click", (e) => {
      if (e.target === ov) dismissAlert();
    });

    // Decision buttons
    document.querySelectorAll("#cs-explain-actions button").forEach(b => {
      b.addEventListener("click", () => logDecision(b.dataset.d, "explain"));
    });
    document.querySelectorAll("#cs-alert-actions button").forEach(b => {
      b.addEventListener("click", () => logDecision(b.dataset.d, "alert"));
    });
  }

  // ===== Viewport text extraction =====
  function getViewportText() {
    const vh = window.innerHeight, vw = window.innerWidth;
    const texts = [], seen = new Set();
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        const p = node.parentElement;
        if (!p) return NodeFilter.FILTER_REJECT;
        const tag = p.tagName.toLowerCase();
        if (["script","style","noscript","iframe","svg","meta","link"].includes(tag)) return NodeFilter.FILTER_REJECT;
        if (p.closest("#cs-widget") || p.closest("#cs-alert-overlay")) return NodeFilter.FILTER_REJECT;
        const t = node.textContent.trim();
        if (!t || t.length < 2) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    let n;
    while ((n = walker.nextNode())) {
      const p = n.parentElement;
      if (!p) continue;
      const r = p.getBoundingClientRect();
      if (r.bottom > 0 && r.top < vh && r.right > 0 && r.left < vw && r.width > 0 && r.height > 0) {
        const s = window.getComputedStyle(p);
        if (s.display === "none" || s.visibility === "hidden" || s.opacity === "0") continue;
        const t = n.textContent.trim();
        if (t.length >= 2 && !seen.has(t)) { seen.add(t); texts.push(t); }
      }
    }
    return texts.join(" ").replace(/\s+/g, " ").trim().substring(0, 15000);
  }

  function hash(s) {
    if (!s) return "";
    let h = 0;
    for (let i = 0; i < s.length; i++) { h = ((h << 5) - h) + s.charCodeAt(i); h |= 0; }
    return String(h);
  }

  // ===== API via background service worker =====
  function analyze(text) {
    return new Promise((resolve, reject) => {
      if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.sendMessage) {
        chrome.runtime.sendMessage({ type: "analyze", text: text.substring(0, 15000) }, (resp) => {
          if (chrome.runtime.lastError) { reject(new Error(chrome.runtime.lastError.message)); return; }
          if (resp && resp.error) { reject(new Error(resp.error)); return; }
          resolve(resp);
        });
      } else {
        reject(new Error("No chrome runtime"));
      }
    });
  }

  function offlineAnalyze(text) {
    const pats = {
      phishing: [/click\s+here\s+to\s+verify/i, /your\s+account\s+(has\s+been|was)\s+(compromised|suspended)/i, /enter\s+your\s+(password|bank|credit)/i, /urgent.*verify/i],
      manipulation: [/act\s+now\s+or/i, /share\s+(this|before)/i, /you\s+should\s+be\s+ashamed/i],
      disinformation: [/they\s+don'?t\s+want\s+you\s+to\s+know/i, /mainstream\s+media\s+is\s+hiding/i, /miracle\s+cure/i, /government\s+is\s+secretly/i],
    };
    let maxS = 0, typ = "safe";
    const expl = [];
    for (const [c, ps] of Object.entries(pats)) {
      let m = 0;
      for (const p of ps) if (p.test(text)) m++;
      if (m > 0) {
        const s = Math.min(m * 25, 80);
        expl.push(`${m} ${c} pattern(s) detected`);
        if (s > maxS) { maxS = s; typ = c; }
      }
    }
    return { risk_score: maxS, threat_type: typ, explanation: expl, confidence: maxS > 0 ? 0.4 : 0.2 };
  }

  // ===== Decision logging =====
  async function logDecision(decision, source) {
    if (!currentResult) return;
    const container = source === "alert" ? "#cs-alert-actions" : "#cs-explain-actions";
    const loggedEl = source === "alert" ? "cs-alert-logged" : "cs-explain-logged";
    document.querySelectorAll(`${container} button`).forEach(b => b.disabled = true);
    try {
      if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.sendMessage) {
        chrome.runtime.sendMessage({
          type: "logDecision",
          payload: { input_text: currentText.substring(0, 5000), ai_decision: currentResult, user_decision: decision }
        });
      }
    } catch (e) { /* silent */ }
    document.getElementById(loggedEl).style.display = "block";
    // If alert, dismiss after 1.5s
    if (source === "alert") {
      setTimeout(dismissAlert, 1500);
    }
  }

  function dismissAlert() {
    document.getElementById("cs-alert-overlay").classList.remove("visible");
    alertDismissedHash = lastHash;
  }

  // ===== Build explanation text from result =====
  function buildExplainText(result) {
    if (result.explanation && result.explanation.length > 0) {
      return result.explanation.join(". ") + ".";
    }
    const score = result.risk_score;
    if (score < 30) return "Content appears mostly safe. Minor signals detected.";
    if (score < 50) return "Some suspicious patterns were found. Exercise caution with this content.";
    return "Significant risk indicators detected. Review this content carefully.";
  }

  // ===== UI Update =====
  function updateUI(result) {
    const score = result.risk_score;
    const circle = document.getElementById("cs-circle");
    const explain = document.getElementById("cs-explain");
    const overlay = document.getElementById("cs-alert-overlay");
    const circ = 2 * Math.PI * 24;

    if (score < 30) {
      // MODE 1: Circle only
      circle.style.display = "flex";
      explain.style.display = "none";

      const color = score <= 10 ? "#22c55e" : score <= 20 ? "#4ade80" : "#a3e635";
      circle.style.borderColor = color;
      document.getElementById("cs-circle-score").textContent = score;
      document.getElementById("cs-circle-score").style.color = color;
      circle.querySelector(".cs-circle-pct").style.color = color;
      const ring = document.getElementById("cs-ring");
      const offset = circ - (score / 100) * circ;
      ring.setAttribute("stroke-dashoffset", offset);
      ring.setAttribute("stroke", color);

    } else if (score <= 50) {
      // MODE 2: Text explanation card
      circle.style.display = "none";
      explain.style.display = "block";
      explain.style.animation = "none";
      void explain.offsetHeight; // reflow
      explain.style.animation = "cs-slideUp 0.3s ease";

      document.getElementById("cs-explain-score").textContent = score;
      document.getElementById("cs-explain-bar").style.width = `${score}%`;
      document.getElementById("cs-explain-text").textContent = buildExplainText(result);
      document.getElementById("cs-explain-type").textContent = result.threat_type;
      document.querySelectorAll("#cs-explain-actions button").forEach(b => b.disabled = false);
      document.getElementById("cs-explain-logged").style.display = "none";

    } else {
      // MODE 3: Big center popup
      circle.style.display = "none";
      explain.style.display = "none";

      if (alertDismissedHash !== lastHash) {
        document.getElementById("cs-alert-score").textContent = score;
        document.getElementById("cs-alert-type").textContent = result.threat_type;

        const list = document.getElementById("cs-alert-explain-list");
        list.innerHTML = "";
        const items = result.explanation && result.explanation.length > 0
          ? result.explanation
          : ["High risk content detected on this page"];
        items.forEach(e => {
          const li = document.createElement("li");
          li.textContent = e;
          list.appendChild(li);
        });

        document.querySelectorAll("#cs-alert-actions button").forEach(b => b.disabled = false);
        document.getElementById("cs-alert-logged").style.display = "none";
        overlay.classList.add("visible");
      }
    }
  }

  // ===== Scan loop =====
  async function scan() {
    if (busy) return;
    const text = getViewportText();
    const h = hash(text);
    if (h === lastHash || !text || text.length < 10) return;
    lastHash = h;
    currentText = text;
    busy = true;
    try {
      let result;
      try { result = await analyze(text); } catch (e) { result = offlineAnalyze(text); }
      currentResult = result;
      updateUI(result);
      // Share result with popup via storage
      if (typeof chrome !== "undefined" && chrome.storage) {
        chrome.storage.local.set({ csLastResult: result, csLastScore: result.risk_score, csLastUpdate: Date.now() });
      }
    } catch (e) { /* silent */ }
    busy = false;
  }

  // ===== Init =====
  function loadAndStart() {
    go();
  }

  function go() {
    build();
    scan();
    setInterval(scan, SCAN_MS);
  }

  loadAndStart();
})();
