/**
 * Cognitive Shield TN - Content Script
 * Extracts visible text from the current VIEWPORT (what's on screen),
 * not the full page. Supports real-time monitoring.
 */

(() => {
  // Listen for messages from the popup
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "extractText") {
      const text = extractVisibleText();
      sendResponse({ text: text, url: window.location.href, title: document.title });
    }
    if (request.action === "extractViewportText") {
      const text = extractViewportText();
      sendResponse({ text: text, url: window.location.href, title: document.title });
    }
    return true;
  });

  /**
   * Extract text ONLY from elements visible in the current viewport.
   * This means when the user scrolls or navigates, different text is returned.
   */
  function extractViewportText() {
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;
    const texts = [];
    const seen = new Set();

    // Get all text-containing elements
    const walker = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_TEXT,
      {
        acceptNode: (node) => {
          const parent = node.parentElement;
          if (!parent) return NodeFilter.FILTER_REJECT;
          const tag = parent.tagName.toLowerCase();
          // Skip invisible/non-content elements
          if (["script", "style", "noscript", "iframe", "svg", "meta", "link"].includes(tag)) {
            return NodeFilter.FILTER_REJECT;
          }
          const text = node.textContent.trim();
          if (!text || text.length < 2) return NodeFilter.FILTER_REJECT;
          return NodeFilter.FILTER_ACCEPT;
        },
      }
    );

    let node;
    while ((node = walker.nextNode())) {
      const parent = node.parentElement;
      if (!parent) continue;

      const rect = parent.getBoundingClientRect();

      // Check if element is within the visible viewport
      if (
        rect.bottom > 0 &&
        rect.top < viewportHeight &&
        rect.right > 0 &&
        rect.left < viewportWidth &&
        rect.width > 0 &&
        rect.height > 0
      ) {
        // Check element is actually visible (not hidden via CSS)
        const style = window.getComputedStyle(parent);
        if (
          style.display === "none" ||
          style.visibility === "hidden" ||
          style.opacity === "0"
        ) {
          continue;
        }

        const text = node.textContent.trim();
        if (text.length >= 2 && !seen.has(text)) {
          seen.add(text);
          texts.push(text);
        }
      }
    }

    return cleanText(texts.join(" "));
  }

  /**
   * Fallback: Extract visible text content from the full page.
   */
  function extractVisibleText() {
    const selectors = [
      "article",
      "main",
      '[role="main"]',
      ".post-content",
      ".article-content",
      ".entry-content",
      ".content",
    ];

    for (const selector of selectors) {
      const el = document.querySelector(selector);
      if (el && el.innerText.trim().length > 100) {
        return cleanText(el.innerText);
      }
    }

    const body = document.body;
    if (!body) return "";

    const clone = body.cloneNode(true);
    const removeSelectors = [
      "script", "style", "noscript", "iframe", "svg",
      "nav", "header", "footer", "aside",
      '[role="navigation"]', '[role="banner"]', '[role="contentinfo"]',
      ".sidebar", ".menu", ".nav", ".footer", ".header",
      ".advertisement", ".ad", ".ads",
    ];

    removeSelectors.forEach((sel) => {
      clone.querySelectorAll(sel).forEach((el) => el.remove());
    });

    return cleanText(clone.innerText);
  }

  /**
   * Clean extracted text by normalizing whitespace and trimming.
   */
  function cleanText(text) {
    if (!text) return "";
    return text
      .replace(/\s+/g, " ")
      .replace(/\n{3,}/g, "\n\n")
      .trim()
      .substring(0, 15000);
  }
})();
