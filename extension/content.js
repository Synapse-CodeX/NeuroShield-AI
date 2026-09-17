// ═══════════════════════════════════════════════════════════════
//  VeritAI Content Script
//  Handles: Domain safety badge + Fact check overlay on page
// ═══════════════════════════════════════════════════════════════

let factCheckOverlay = null;
let safetyBadge = null;
let safetyPanel = null;
let badgeAutoHideTimer = null;

// ── Message Listener ──
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  switch (request.action) {
    case "factCheckText":
      showFactCheckOverlay(request.text);
      break;
    case "domainScanStarted":
      showSafetyBadge("scanning", null);
      break;
    case "domainScanComplete":
      showSafetyBadge("complete", request.result);
      break;
    case "domainScanError":
      showSafetyBadge("error", null);
      break;
    case "getPageText":
      sendResponse({ text: document.body.innerText });
      return true;
  }
});

// ═══════════════════════════════════════════════════════════════
//  DOMAIN SAFETY BADGE
// ═══════════════════════════════════════════════════════════════

function showSafetyBadge(status, result) {
  // Remove existing badge/panel
  if (safetyBadge) safetyBadge.remove();
  if (safetyPanel) safetyPanel.remove();
  clearTimeout(badgeAutoHideTimer);

  safetyBadge = document.createElement("div");
  safetyBadge.id = "veritai-safety-badge";

  if (status === "scanning") {
    safetyBadge.className = "veritai-badge-scanning";
    safetyBadge.innerHTML = `
      <div class="veritai-badge-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        </svg>
      </div>
      <div class="veritai-badge-spinner-ring"></div>
    `;
    safetyBadge.title = "VeritAI: Scanning domain safety...";
  } else if (status === "error") {
    safetyBadge.className = "veritai-badge-error";
    safetyBadge.innerHTML = `
      <div class="veritai-badge-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        </svg>
      </div>
      <span class="veritai-badge-label">!</span>
    `;
    safetyBadge.title = "VeritAI: Scan failed — backend may be offline";
  } else if (status === "complete" && result) {
    const score = result.overall_score || 0;
    const verdict = result.verdict || "UNKNOWN";
    let colorClass = "veritai-badge-caution";
    if (verdict === "SAFE" || score >= 70) colorClass = "veritai-badge-safe";
    else if (verdict === "UNSAFE" || score < 40) colorClass = "veritai-badge-unsafe";

    safetyBadge.className = colorClass;
    safetyBadge.innerHTML = `
      <div class="veritai-badge-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        </svg>
      </div>
      <span class="veritai-badge-score">${score}</span>
    `;
    safetyBadge.title = `VeritAI Safety Score: ${score}/100 — ${verdict}`;

    // Click to expand details
    safetyBadge.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleSafetyPanel(result);
    });

    // Auto-minimize after 8 seconds
    badgeAutoHideTimer = setTimeout(() => {
      if (safetyBadge) safetyBadge.classList.add("veritai-badge-minimized");
    }, 8000);
  }

  document.body.appendChild(safetyBadge);
}

function toggleSafetyPanel(result) {
  if (safetyPanel) {
    safetyPanel.remove();
    safetyPanel = null;
    return;
  }

  safetyPanel = document.createElement("div");
  safetyPanel.id = "veritai-safety-panel";

  const score = result.overall_score || 0;
  const verdict = result.verdict || "UNKNOWN";
  const scores = result.scores || {};
  const recommendations = result.recommendations || [];
  const summary = result.summary || "";

  let verdictClass = "veritai-verdict-caution";
  let verdictIcon = "⚠️";
  if (verdict === "SAFE" || score >= 70) { verdictClass = "veritai-verdict-safe"; verdictIcon = "✅"; }
  else if (verdict === "UNSAFE" || score < 40) { verdictClass = "veritai-verdict-unsafe"; verdictIcon = "🚨"; }

  // Build score bars
  let scoreBarsHtml = "";
  const scoreLabels = {
    url_safety: "URL Safety",
    domain_age: "Domain Age",
    ssl_certificate: "SSL Certificate",
    content_quality: "Content Quality",
    reputation: "Reputation",
    scam_reports: "Scam Reports"
  };

  for (const [key, label] of Object.entries(scoreLabels)) {
    const val = scores[key] ?? scores[key.replace("_", "")] ?? null;
    if (val !== null && val !== undefined) {
      let barColor = "#f59e0b";
      if (val >= 70) barColor = "#10b981";
      else if (val < 40) barColor = "#ef4444";
      scoreBarsHtml += `
        <div class="veritai-score-row">
          <span class="veritai-score-label">${label}</span>
          <div class="veritai-score-bar-bg">
            <div class="veritai-score-bar-fill" style="width:${val}%; background:${barColor}"></div>
          </div>
          <span class="veritai-score-value">${val}</span>
        </div>
      `;
    }
  }

  // Recommendations
  let recsHtml = "";
  if (recommendations.length > 0) {
    recsHtml = `<div class="veritai-recs"><h4>Recommendations</h4><ul>${recommendations.map(r => `<li>${r}</li>`).join("")}</ul></div>`;
  }

  safetyPanel.innerHTML = `
    <div class="veritai-safety-panel-inner">
      <div class="veritai-safety-panel-header">
        <div class="veritai-safety-panel-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#818cf8" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
          <span>Domain Safety Report</span>
        </div>
        <button id="veritai-safety-panel-close">&times;</button>
      </div>
      <div class="veritai-safety-panel-body">
        <div class="veritai-verdict-card ${verdictClass}">
          <span class="veritai-verdict-icon">${verdictIcon}</span>
          <div>
            <div class="veritai-verdict-label">${verdict}</div>
            <div class="veritai-verdict-score">Overall Score: <strong>${score}/100</strong></div>
          </div>
        </div>
        ${scoreBarsHtml ? `<div class="veritai-scores-section"><h4>Breakdown</h4>${scoreBarsHtml}</div>` : ""}
        ${summary ? `<div class="veritai-summary-section"><h4>Summary</h4><p>${summary}</p></div>` : ""}
        ${recsHtml}
      </div>
    </div>
  `;

  document.body.appendChild(safetyPanel);

  document.getElementById("veritai-safety-panel-close").addEventListener("click", () => {
    safetyPanel.remove();
    safetyPanel = null;
  });
}

// ═══════════════════════════════════════════════════════════════
//  FACT CHECK OVERLAY
// ═══════════════════════════════════════════════════════════════

function showFactCheckOverlay(text) {
  if (factCheckOverlay) {
    factCheckOverlay.remove();
  }

  factCheckOverlay = document.createElement("div");
  factCheckOverlay.id = "veritai-extension-overlay";
  
  const container = document.createElement("div");
  container.className = "veritai-extension-container";
  
  const header = document.createElement("div");
  header.className = "veritai-header";
  header.innerHTML = `
    <div class="veritai-header-title">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="#818cf8" stroke-width="2"/>
        <path d="M7 12.5L10 15.5L17 8.5" stroke="#818cf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <h3>VeritAI Fact Check</h3>
    </div>
    <button id="veritai-close-btn">&times;</button>
  `;
  
  const content = document.createElement("div");
  content.className = "veritai-content";
  content.innerHTML = `
    <div class="veritai-loading">
      <div class="veritai-spinner"></div>
      <p>Analyzing selected text...</p>
    </div>
  `;
  
  container.appendChild(header);
  container.appendChild(content);
  factCheckOverlay.appendChild(container);
  
  document.body.appendChild(factCheckOverlay);
  
  document.getElementById("veritai-close-btn").addEventListener("click", () => {
    factCheckOverlay.remove();
    factCheckOverlay = null;
  });

  fetchFactCheck(text, content);
}

async function fetchFactCheck(text, contentElement) {
  try {
    const response = await fetch("http://localhost:8000/api/factcheck/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ input_text: text })
    });

    if (!response.ok) {
      throw new Error(`API returned ${response.status}`);
    }

    const data = await response.json();
    renderFactCheckResults(data, contentElement);
  } catch (error) {
    contentElement.innerHTML = `
      <div class="veritai-error">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <p>Error checking facts. Ensure VeritAI backend is running on localhost:8000.</p>
        <p class="veritai-error-detail">${error.message}</p>
      </div>
    `;
  }
}

function renderFactCheckResults(data, container) {
  let html = `<div class="veritai-results">`;
  
  // Show overall report if available
  if (data.final_report) {
    let formattedReport = data.final_report
      .replace(/\n/g, '<br>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    html += `
      <div class="veritai-report">
        <h4>Analysis Report</h4>
        <div class="veritai-report-text">${formattedReport}</div>
      </div>
    `;
  }

  if (data.claims && data.claims.length > 0) {
    html += `<h4>Claims Verified</h4><ul class="veritai-claims-list">`;
    data.claims.forEach(claim => {
      const v = data.verifications[claim.id];
      const verdict = v ? v.verdict : 'UNKNOWN';
      const reason = v ? v.reason : '';
      
      let badgeClass = 'veritai-badge-unknown';
      if (verdict === 'TRUE') badgeClass = 'veritai-badge-true';
      if (verdict === 'FALSE') badgeClass = 'veritai-badge-false';
      if (verdict === 'MIXED') badgeClass = 'veritai-badge-mixed';
      
      html += `
        <li class="veritai-claim-item">
          <div class="veritai-claim-header">
            <span class="veritai-badge ${badgeClass}">${verdict}</span>
            <span class="veritai-claim-text">${claim.claim}</span>
          </div>
          ${reason ? `<div class="veritai-claim-reason">${reason}</div>` : ''}
        </li>
      `;
    });
    html += `</ul>`;
  } else {
    html += `<p class="veritai-no-claims">No specific claims found to verify.</p>`;
  }

  html += `</div>`;
  container.innerHTML = html;
}
