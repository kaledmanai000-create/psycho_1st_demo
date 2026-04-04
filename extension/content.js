/**
 * Cognitive Shield TN - Content Script
 * Extracts visible text content from the current web page.
 * Runs in the context of the web page.
 */

(() => {
  // Listen for messages from the popup
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "extractText") {
      const text = extractVisibleText();
      sendResponse({ text: text, url: window.location.href, title: document.title });
    }
    return true; // Keep message channel open for async response
  });

  /**
   * Extract visible text content from the page.
   * Focuses on meaningful content, skipping scripts, styles, and hidden elements.
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

    // Try to find main content area first
    for (const selector of selectors) {
      const el = document.querySelector(selector);
      if (el && el.innerText.trim().length > 100) {
        return cleanText(el.innerText);
      }
    }

    // Fallback: extract from body, filtering out noise
    const body = document.body;
    if (!body) return "";

    // Clone body and remove non-content elements
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
      .substring(0, 15000); // Limit to 15K chars
  }
})();
