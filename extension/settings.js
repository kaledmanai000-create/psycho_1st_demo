/**
 * Cognitive Shield TN - Settings Script
 */

const DEFAULT_BACKEND_URL = "http://localhost:8000";
const DEFAULT_API_KEY = "changeme-cognitive-shield-key";

document.addEventListener("DOMContentLoaded", () => {
  // Load saved settings
  chrome.storage.local.get(["backendUrl", "apiKey"], (data) => {
    document.getElementById("backend-url").value = data.backendUrl || DEFAULT_BACKEND_URL;
    document.getElementById("api-key").value = data.apiKey || DEFAULT_API_KEY;
  });

  document.getElementById("save-btn").addEventListener("click", () => {
    const backendUrl = document.getElementById("backend-url").value.trim();
    const apiKey = document.getElementById("api-key").value.trim();

    chrome.storage.local.set(
      {
        backendUrl: backendUrl || DEFAULT_BACKEND_URL,
        apiKey: apiKey || DEFAULT_API_KEY,
      },
      () => {
        const msg = document.getElementById("status-msg");
        msg.textContent = "Settings saved!";
        setTimeout(() => (msg.textContent = ""), 2000);
      }
    );
  });

  document.getElementById("back-btn").addEventListener("click", () => {
    window.location.href = "popup.html";
  });
});
