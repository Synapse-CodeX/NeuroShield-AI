# VeritAI — Smart Web Guardian (Chrome Extension)

> **3-in-1 browser extension**: Domain Safety Scanning, Fact Checking, and Privacy Policy Analysis — powered by AI agents.

---

## 📦 Installation

### Prerequisites

- **Google Chrome** (version 88+ recommended)
- **VeritAI Backend** running on `http://localhost:8000`

### Load the Extension

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable **Developer Mode** (toggle in the top-right corner)
3. Click **"Load unpacked"**
4. Select the `extension/` folder from this project
5. The VeritAI shield icon will appear in your browser toolbar

### Start the Backend

The extension requires the FastAPI backend to be running:

```bash
cd backend
pip install -r requirements.txt
python server.py
```

Or from the project root:

```bash
uvicorn backend.server:app --host 0.0.0.0 --port 8000 --reload
```

> **Note**: Make sure your `.env` file at the project root contains valid API keys for the agents (e.g., `GOOGLE_API_KEY`, `TAVILY_API_KEY`).

---

## 🛡️ Mode 1: Domain Safety Scanner

### What it does
Automatically scans every website you visit for safety threats using the `website_scan_agent`. Checks include:
- URL pattern analysis (phishing/typosquatting detection)
- Domain age verification
- SSL certificate validation
- Content quality assessment
- Online reputation lookup
- Scam report database check

### How to use
1. **Simply browse the web** — scanning triggers automatically when you navigate to any website
2. A **floating shield badge** appears in the bottom-right corner of the page:
   - 🟢 **Green** = Safe (score ≥ 70)
   - 🟡 **Amber** = Caution (score 40–69)
   - 🔴 **Red** = Unsafe (score < 40)
3. **Click the badge** to expand a detailed safety report with:
   - Overall score out of 100
   - Category-by-category breakdown with score bars
   - Summary and recommendations
4. The badge auto-minimizes after 8 seconds (hover to expand again)
5. You can also view results in the **popup** (click the extension icon → Safety tab)

### Pages skipped
- `chrome://` internal pages
- `localhost` addresses
- Extension pages

---

## 🔍 Mode 2: Fact Checker

### What it does
Analyzes selected text for factual claims using the `fact_check_agent`. It extracts claims, searches for evidence, and provides verdicts (TRUE / FALSE / MIXED / UNKNOWN) with supporting reasoning.

### How to use
1. **Select any text** on a webpage (highlight it with your mouse)
2. **Right-click** on the selected text
3. Click **"🔍 Fact Check with VeritAI"** from the context menu
4. A **fact-check overlay** appears in the top-right corner of the page showing:
   - Analysis report
   - Individual claims with verdict badges
   - Reasoning for each verdict
5. Click the **✕** button to close the overlay

### Tips
- Select substantial text (full paragraphs, article excerpts) for best results
- The more claims in the text, the more detailed the analysis
- Each claim is independently verified against multiple sources

---

## 📜 Mode 3: Privacy Policy Analyzer

### What it does
Analyzes the privacy policy of any website using the `privacy_agent`. It extracts and categorizes:
- Types of personal data collected
- How your data is used
- Third-party sharing practices
- Tracking methods employed
- Data retention policies
- Privacy risk scoring

### How to use
1. **Navigate to a website's privacy policy page** (usually found in the footer links)
2. **Click the VeritAI extension icon** in the toolbar
3. Switch to the **Privacy** tab
4. Click **"Analyze This Page"**
5. The analysis results will show:
   - Privacy Risk Score (0–100) with risk level
   - Categorized data practices (with tag chips)
   - Data retention information
   - Identified risks
   - Overall summary

### Tips
- For best results, be on the actual privacy policy page (not the homepage)
- Longer, more detailed policies produce richer analysis
- The risk score is relative — higher = more concerning practices

---

## 🎯 Quick Reference

| Action | How |
|--------|-----|
| View domain safety | Just browse — badge appears automatically |
| See detailed safety report | Click the shield badge on page |
| See safety in popup | Extension icon → Safety tab |
| Fact check text | Select text → Right-click → "Fact Check with VeritAI" |
| Analyze privacy policy | Go to privacy page → Extension icon → Privacy tab → Analyze |

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Badge doesn't appear | Check that the backend is running at `localhost:8000` |
| "Error checking facts" | Verify backend is running: `curl http://localhost:8000/api/health` |
| Context menu missing | Reload the extension in `chrome://extensions/` |
| Privacy analysis fails | Make sure you're on a page with substantial text content |
| Extension not loading | Ensure `manifest.json` is valid — check Chrome DevTools console |

---

## 📁 File Structure

```
extension/
├── manifest.json       # Chrome extension configuration (MV3)
├── background.js       # Service worker: auto-scan, context menu, message routing
├── content.js          # Injected into pages: safety badge + fact check overlay
├── content.css         # Styles for in-page UI elements
├── popup.html          # Extension popup: 3-tab dashboard
├── popup.js            # Popup logic: tab switching, results rendering
├── popup.css           # Popup styles: dark theme, gauges, cards
├── icons/              # Extension icons (16px, 48px, 128px)
└── README.md           # This file
```

---

## 🔌 Backend API Endpoints Used

| Endpoint | Method | Mode | Payload |
|----------|--------|------|---------|
| `/api/scanner/scan` | POST | Domain Safety | `{ "url": "https://..." }` |
| `/api/factcheck/analyze` | POST | Fact Check | `{ "input_text": "..." }` |
| `/api/privacy/analyze` | POST | Privacy Policy | `{ "raw_text": "..." }` |
| `/api/health` | GET | Health Check | — |
