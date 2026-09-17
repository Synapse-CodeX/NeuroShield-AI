// ═══════════════════════════════════════════════════════════════
//  VeritAI Popup — 3-Tab Dashboard
//  Safety | Fact Check | Privacy
// ═══════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {

  // ── Tab Switching ──
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabPanels = document.querySelectorAll('.tab-panel');
  const tabIndicator = document.querySelector('.tab-indicator');

  function switchTab(tabName) {
    tabBtns.forEach(btn => btn.classList.toggle('active', btn.dataset.tab === tabName));
    tabPanels.forEach(panel => panel.classList.toggle('active', panel.id === `tab-${tabName}`));
    updateIndicator();
  }

  function updateIndicator() {
    const activeBtn = document.querySelector('.tab-btn.active');
    if (activeBtn && tabIndicator) {
      tabIndicator.style.width = `${activeBtn.offsetWidth}px`;
      tabIndicator.style.left = `${activeBtn.offsetLeft}px`;
    }
  }

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });

  // Initialize indicator position
  setTimeout(updateIndicator, 50);

  // ═══════════════════════════════════════════════════════════════
  //  SAFETY TAB
  // ═══════════════════════════════════════════════════════════════

  const safetyLoading = document.getElementById('safety-loading');
  const safetyNoScan = document.getElementById('safety-no-scan');
  const safetyResults = document.getElementById('safety-results');

  // Get current tab and load scan results
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (!tabs[0]) {
      safetyLoading.classList.add('hidden');
      safetyNoScan.classList.remove('hidden');
      return;
    }

    const tabId = tabs[0].id;
    const tabUrl = tabs[0].url || "";

    // Skip non-http pages
    if (!tabUrl.startsWith("http://") && !tabUrl.startsWith("https://")) {
      safetyLoading.classList.add('hidden');
      safetyNoScan.classList.remove('hidden');
      return;
    }

    // Ask background for scan result
    chrome.runtime.sendMessage({ action: "getScanResult", tabId: tabId }, (response) => {
      safetyLoading.classList.add('hidden');

      if (response && response.result) {
        safetyResults.classList.remove('hidden');
        renderSafetyResults(response.result, response.url);
      } else {
        safetyNoScan.classList.remove('hidden');
      }
    });
  });

  function renderSafetyResults(data, url) {
    const score = data.overall_score || 0;
    const verdict = data.verdict || "UNKNOWN";
    const scores = data.scores || {};
    const recommendations = data.recommendations || [];
    const summary = data.summary || "";

    let verdictClass = "verdict-caution";
    let verdictIcon = "⚠️";
    let gaugeColor = "#f59e0b";
    if (verdict === "SAFE" || score >= 70) {
      verdictClass = "verdict-safe";
      verdictIcon = "✅";
      gaugeColor = "#10b981";
    } else if (verdict === "UNSAFE" || score < 40) {
      verdictClass = "verdict-unsafe";
      verdictIcon = "🚨";
      gaugeColor = "#ef4444";
    }

    // Domain name
    let domain = "";
    try { domain = new URL(url).hostname; } catch (e) { domain = url; }

    // Score bars HTML
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
      const val = scores[key] ?? null;
      if (val !== null && val !== undefined) {
        let barColor = "#f59e0b";
        if (val >= 70) barColor = "#10b981";
        else if (val < 40) barColor = "#ef4444";
        scoreBarsHtml += `
          <div class="score-row">
            <span class="score-label">${label}</span>
            <div class="score-bar-bg"><div class="score-bar-fill" style="width:${val}%;background:${barColor}"></div></div>
            <span class="score-val">${val}</span>
          </div>
        `;
      }
    }

    let recsHtml = "";
    if (recommendations.length > 0) {
      recsHtml = `
        <div class="recs-section">
          <h4>Recommendations</h4>
          <ul>${recommendations.map(r => `<li>${r}</li>`).join("")}</ul>
        </div>
      `;
    }

    safetyResults.innerHTML = `
      <div class="safety-domain">${domain}</div>
      <div class="safety-gauge-row">
        <div class="safety-gauge">
          <svg viewBox="0 0 120 120" class="gauge-svg">
            <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="8"/>
            <circle cx="60" cy="60" r="52" fill="none" stroke="${gaugeColor}" stroke-width="8"
              stroke-dasharray="${(score / 100) * 327} 327"
              stroke-linecap="round" transform="rotate(-90 60 60)"
              class="gauge-progress"/>
          </svg>
          <div class="gauge-center">
            <span class="gauge-score">${score}</span>
            <span class="gauge-label">/ 100</span>
          </div>
        </div>
        <div class="verdict-badge ${verdictClass}">
          <span class="verdict-icon">${verdictIcon}</span>
          <span class="verdict-text">${verdict}</span>
        </div>
      </div>
      ${scoreBarsHtml ? `<div class="scores-breakdown"><h4>Breakdown</h4>${scoreBarsHtml}</div>` : ""}
      ${summary ? `<div class="summary-section"><h4>Summary</h4><p>${summary}</p></div>` : ""}
      ${recsHtml}
    `;
  }

  // ═══════════════════════════════════════════════════════════════
  //  PRIVACY TAB
  // ═══════════════════════════════════════════════════════════════

  const analyzeBtn = document.getElementById('analyze-privacy-btn');
  const privacyIdle = document.getElementById('privacy-idle');
  const privacyLoading = document.getElementById('privacy-loading');
  const privacyResults = document.getElementById('privacy-results');
  const privacyError = document.getElementById('privacy-error');

  analyzeBtn.addEventListener('click', async () => {
    // Get the current tab's text content
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) return;

    privacyIdle.classList.add('hidden');
    privacyError.classList.add('hidden');
    privacyResults.classList.add('hidden');
    privacyLoading.classList.remove('hidden');

    try {
      // Execute script to get page text
      const [result] = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => document.body.innerText
      });

      const pageText = result.result;
      if (!pageText || pageText.trim().length < 50) {
        throw new Error("Not enough text content found on this page.");
      }

      // Send to background for analysis
      chrome.runtime.sendMessage(
        { action: "analyzePrivacyPolicy", text: pageText },
        (response) => {
          privacyLoading.classList.add('hidden');
          if (response && response.success) {
            privacyResults.classList.remove('hidden');
            renderPrivacyResults(response.data);
          } else {
            privacyError.textContent = `Error: ${response?.error || "Unknown error"}. Ensure backend is running.`;
            privacyError.classList.remove('hidden');
            privacyIdle.classList.remove('hidden');
          }
        }
      );
    } catch (err) {
      privacyLoading.classList.add('hidden');
      privacyError.textContent = `Error: ${err.message}`;
      privacyError.classList.remove('hidden');
      privacyIdle.classList.remove('hidden');
    }
  });

  function renderPrivacyResults(data) {
    const score = data.score ?? 0;
    const riskLevel = data.risk_level || "Unknown";
    const risks = data.risks || [];
    const summary = data.summary || "";
    const structured = data.structured_data || {};

    // Risk color
    let riskColor = "#f59e0b";
    let riskIcon = "⚠️";
    if (riskLevel.toLowerCase().includes("low")) {
      riskColor = "#10b981"; riskIcon = "✅";
    } else if (riskLevel.toLowerCase().includes("high") || riskLevel.toLowerCase().includes("critical")) {
      riskColor = "#ef4444"; riskIcon = "🚨";
    }

    // Data categories
    let categoriesHtml = "";
    const categoryLabels = {
      data_collected: { label: "Data Collected", icon: "📊" },
      data_usage: { label: "Data Usage", icon: "⚙️" },
      third_party_sharing: { label: "Third-Party Sharing", icon: "🔗" },
      tracking_methods: { label: "Tracking Methods", icon: "👁️" }
    };

    for (const [key, meta] of Object.entries(categoryLabels)) {
      const items = structured[key] || [];
      if (items.length > 0) {
        categoriesHtml += `
          <div class="privacy-category">
            <div class="privacy-category-header">
              <span>${meta.icon}</span>
              <span>${meta.label}</span>
              <span class="privacy-category-count">${items.length}</span>
            </div>
            <div class="privacy-category-items">
              ${items.map(item => `<span class="privacy-tag">${item}</span>`).join("")}
            </div>
          </div>
        `;
      }
    }

    // Retention policy
    const retention = structured.retention_policy || "";
    let retentionHtml = "";
    if (retention) {
      retentionHtml = `
        <div class="privacy-category">
          <div class="privacy-category-header">
            <span>🕐</span>
            <span>Data Retention</span>
          </div>
          <p class="privacy-retention-text">${retention}</p>
        </div>
      `;
    }

    // Risks
    let risksHtml = "";
    if (risks.length > 0) {
      risksHtml = `
        <div class="privacy-risks">
          <h4>⚡ Risks Identified</h4>
          <ul>${risks.map(r => `<li>${r}</li>`).join("")}</ul>
        </div>
      `;
    }

    privacyResults.innerHTML = `
      <div class="privacy-score-card">
        <div class="privacy-score-gauge">
          <svg viewBox="0 0 100 100" class="gauge-svg-sm">
            <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="6"/>
            <circle cx="50" cy="50" r="42" fill="none" stroke="${riskColor}" stroke-width="6"
              stroke-dasharray="${(score / 100) * 264} 264"
              stroke-linecap="round" transform="rotate(-90 50 50)"
              class="gauge-progress"/>
          </svg>
          <div class="gauge-center-sm">
            <span class="gauge-score-sm">${score}</span>
          </div>
        </div>
        <div class="privacy-score-info">
          <div class="privacy-risk-badge" style="background:${riskColor}20;color:${riskColor};border:1px solid ${riskColor}40">
            ${riskIcon} ${riskLevel}
          </div>
          <span class="privacy-score-subtitle">Privacy Risk Score</span>
        </div>
      </div>
      ${categoriesHtml}
      ${retentionHtml}
      ${risksHtml}
      ${summary ? `<div class="privacy-summary"><h4>Summary</h4><p>${summary}</p></div>` : ""}
    `;
  }

});
