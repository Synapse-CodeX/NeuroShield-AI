// ═══════════════════════════════════════════════════════════════
//  VeritAI Background Service Worker
//  Handles: Context menu, auto domain scanning, message routing
// ═══════════════════════════════════════════════════════════════

const API_BASE = "http://localhost:8000";

// Track tabs currently being scanned to avoid duplicate requests
const scanningTabs = new Set();

// ── Context Menu Setup ──
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "veritai-fact-check",
    title: "🔍 Fact Check with VeritAI",
    contexts: ["selection"]
  });
});

// ── Context Menu Click Handler ──
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "veritai-fact-check" && info.selectionText) {
    chrome.tabs.sendMessage(tab.id, {
      action: "factCheckText",
      text: info.selectionText
    });
  }
});

// ── Auto Domain Safety Scan on Navigation ──
chrome.webNavigation.onCompleted.addListener(async (details) => {
  // Only scan main frame navigations, skip iframes
  if (details.frameId !== 0) return;

  const url = details.url;

  // Skip non-http pages (chrome://, about:, extensions, etc.)
  if (!url.startsWith("http://") && !url.startsWith("https://")) return;

  // Skip localhost and extension pages
  if (url.includes("localhost") || url.includes("chrome-extension://")) return;

  const tabId = details.tabId;

  // Prevent duplicate scans for the same tab
  if (scanningTabs.has(tabId)) return;
  scanningTabs.add(tabId);

  try {
    // Notify content script that scan is starting
    chrome.tabs.sendMessage(tabId, {
      action: "domainScanStarted",
      url: url
    }).catch(() => {}); // Content script might not be ready yet

    // Call the backend scanner API
    const response = await fetch(`${API_BASE}/api/scanner/scan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: url })
    });

    if (!response.ok) {
      throw new Error(`API returned ${response.status}`);
    }

    const data = await response.json();

    // Store the result for the popup to read
    const storageKey = `scan_${tabId}`;
    await chrome.storage.local.set({
      [storageKey]: {
        url: url,
        result: data,
        timestamp: Date.now()
      }
    });

    // Send results to content script to show the badge
    chrome.tabs.sendMessage(tabId, {
      action: "domainScanComplete",
      url: url,
      result: data
    }).catch(() => {});

  } catch (error) {
    // Notify content script of error
    chrome.tabs.sendMessage(tabId, {
      action: "domainScanError",
      url: url,
      error: error.message
    }).catch(() => {});
  } finally {
    scanningTabs.delete(tabId);
  }
});

// ── Clean up storage when tab is closed ──
chrome.tabs.onRemoved.addListener((tabId) => {
  chrome.storage.local.remove(`scan_${tabId}`);
});

// ── Message handler for popup requests ──
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getScanResult") {
    // Popup asking for current tab's scan result
    chrome.storage.local.get(`scan_${request.tabId}`, (data) => {
      sendResponse(data[`scan_${request.tabId}`] || null);
    });
    return true; // Keep channel open for async response
  }

  if (request.action === "analyzePrivacyPolicy") {
    // Popup requesting privacy policy analysis
    fetch(`${API_BASE}/api/privacy/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ raw_text: request.text })
    })
    .then(res => {
      if (!res.ok) throw new Error(`API returned ${res.status}`);
      return res.json();
    })
    .then(data => sendResponse({ success: true, data }))
    .catch(err => sendResponse({ success: false, error: err.message }));

    return true; // Keep channel open for async response
  }
});
