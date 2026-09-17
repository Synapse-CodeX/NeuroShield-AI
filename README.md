# 🛡️ NeuroShield AI

### AI Trust Layer for the Web

> **Detect → Verify → Explain → Recommend**

NeuroShield AI is an AI-powered web trust and safety platform designed to help users understand **what they are trusting online**.

It analyzes privacy policies, verifies factual claims using web evidence, and evaluates websites for observable security and trust signals.

Instead of simply producing an AI-generated verdict, NeuroShield follows an **evidence-first approach**:

> **Every important conclusion should be explainable through evidence, signals, confidence, and recommendations.**

---

## 🚀 Why NeuroShield?

The modern web creates three major trust problems:

- Websites collect increasingly large amounts of personal information.
- False or misleading claims spread rapidly.
- Users often cannot determine whether an unfamiliar website is trustworthy.

Traditional tools usually solve only one of these problems.

NeuroShield combines multiple forms of web intelligence into a single platform:

```text
                    ┌──────────────────────┐
                    │      NEUROSHIELD     │
                    │    AI TRUST LAYER    │
                    └──────────┬───────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
       ┌───────────┐     ┌────────────┐    ┌─────────────┐
       │  Privacy  │     │    Fact    │    │   Website   │
       │Intelligence│    │Intelligence│    │ Intelligence│
       └─────┬─────┘     └──────┬─────┘    └──────┬──────┘
             │                  │                  │
             └──────────────────┼──────────────────┘
                                ▼
                     ┌────────────────────┐
                     │ Evidence + Risk    │
                     │     Analysis       │
                     └─────────┬──────────┘
                               ▼
                     ┌────────────────────┐
                     │ Explain + Recommend│
                     └────────────────────┘
```

---

# ✨ Core Capabilities

## 1. 🔐 Privacy Intelligence

Analyze privacy policies and identify potentially concerning data practices.

NeuroShield can detect signals such as:

- Personal data collection
- Location collection
- Third-party data sharing
- Advertising and profiling
- Tracking technologies
- Data retention practices
- International data transfers
- Automated profiling
- Contact information collection

The system doesn't stop at identifying a risk.

Each finding can contain:

```text
Finding
├── Category
├── Description
├── Severity
├── Confidence
├── Evidence
└── Recommendation
```

Example:

```text
THIRD-PARTY DATA SHARING

Severity: High
Confidence: 95%

Evidence:
"We may share your personal information
with advertising partners..."

Recommendation:
Review which third parties receive
personal information and for what purpose.
```

---

# 2. 🔎 AI Fact Intelligence

NeuroShield converts natural-language input into **atomic, independently verifiable claims**.

Example:

```text
Input:
"The Earth revolves around the Sun once every
365.25 days and the Eiffel Tower is in London."

            ↓

Claim Extraction

Claim #1
The Earth revolves around the Sun once every
365.25 days.

Claim #2
The Eiffel Tower is located in London.

            ↓

Web Evidence Retrieval

            ↓

Evidence Verification

            ↓

Verdict + Confidence + Explanation
```

The Fact Checker uses:

- LLM-based claim extraction
- Atomic claim decomposition
- Tavily web search
- Evidence collection
- Source credibility heuristics
- Batched structured verification
- Supporting/conflicting evidence
- Confidence estimation
- Deterministic report generation

Supported verification outcomes:

```text
✓ True
✕ False
⚠ Partially True
? Unverifiable
```

The goal is not to make the model sound confident.

The goal is to make the result **traceable to evidence**.

---

# 3. 🌐 Website Intelligence

The Website Scanner evaluates websites using multiple signals.

Current analysis includes:

### URL Structure

Detects patterns such as:

- Suspicious top-level domains
- Excessive subdomains
- Suspicious hyphenation
- IP-based URLs
- Brand impersonation patterns
- Suspicious paths
- Encoded characters
- Leetspeak-like substitutions
- `@` characters
- Non-HTTPS URLs
- Unusually long URLs

### SSL / TLS

The scanner can inspect:

- HTTPS availability
- TLS connectivity
- Certificate information
- Certificate issuer
- Subject/SAN information
- Certificate expiration

### Website Content

The scanner can retrieve website content and analyze characteristics such as:

- Content quality
- Website purpose
- Trust indicators
- Suspicious messaging
- Reputation-related signals

The scanner combines multiple signals into a normalized safety score and risk verdict.

---

# 🧠 Evidence-First Architecture

NeuroShield is designed around one principle:

> **Don't ask the user to trust the AI. Show them why the AI reached its conclusion.**

A shared evidence model is used across the system.

```text
Evidence
├── Source type
├── Title
├── URL
├── Excerpt
├── Relevance score
├── Credibility score
└── Metadata
```

Higher-level findings contain:

```text
Finding
├── Category
├── Title
├── Description
├── Severity
├── Confidence
├── Evidence[]
└── Recommendation
```

This allows the frontend to present conclusions together with the underlying evidence.

---

# 🏗️ System Architecture

```text
                         USER
                           │
                           ▼
                ┌─────────────────────┐
                │     React Web App    │
                │       / Streamlit    │
                │     / VeritAI        │
                └──────────┬──────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    FastAPI   │
                    │   REST API   │
                    └──────┬───────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
      ┌────────────┐ ┌────────────┐ ┌────────────┐
      │  Privacy   │ │    Fact    │ │  Website   │
      │   Agent    │ │  Checker   │ │   Agent    │
      └─────┬──────┘ └──────┬─────┘ └──────┬─────┘
            │               │               │
            └───────────────┼───────────────┘
                            ▼
                 ┌────────────────────┐
                 │  Shared AI Layer   │
                 ├────────────────────┤
                 │ Gemini             │
                 │ Tavily             │
                 │ HF Embeddings      │
                 │ FAISS              │
                 └─────────┬──────────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │ Evidence Layer     │
                 │ + Risk Engine      │
                 └─────────┬──────────┘
                           │
                           ▼
                 ┌────────────────────┐
                 │ Explanation +      │
                 │ Recommendations    │
                 └────────────────────┘
```

---

# 🤖 Agent Architecture

NeuroShield uses **LangGraph** to structure its agent workflows.

## Privacy Agent

```text
Raw Policy
    ↓
Chunking
    ↓
Local Vector Store
    ↓
Structured Extraction
    ↓
Evidence Mapping
    ↓
Risk Detection
    ↓
Risk Scoring
    ↓
Summary
    ↓
Analysis Report
```

## Fact Checker

```text
User Input
    ↓
Claim Extraction
    ↓
Atomic Claims
    ↓
Tavily Evidence Retrieval
    ↓
Evidence Collection
    ↓
Batch Verification
    ↓
Deterministic Report Generation
```

## Website Scanner

```text
URL
 ↓
URL Structure Analysis
 ↓
Domain Analysis
 ↓
SSL/TLS Analysis
 ↓
Website Content Analysis
 ↓
Reputation Signals
 ↓
Risk Scoring
 ↓
Verdict + Recommendations
```

---

# 🧩 Technology Stack

## Backend

| Technology | Purpose |
|---|---|
| Python | Core backend and AI logic |
| FastAPI | REST API |
| LangGraph | Agent orchestration |
| Pydantic | Structured state and validation |
| Uvicorn | ASGI server |
| python-dotenv | Environment configuration |

## AI / ML

| Technology | Purpose |
|---|---|
| Gemini | LLM reasoning and structured extraction |
| Tavily | Web search and evidence retrieval |
| Hugging Face | Local embedding models |
| Sentence Transformers | Text embeddings |
| FAISS | Local vector similarity search |

### Current embedding model

```text
sentence-transformers/all-MiniLM-L6-v2
```

Embeddings run locally on CPU, avoiding a separate hosted embedding API.

---

## Frontend

| Technology | Purpose |
|---|---|
| React | Web application |
| Vite | Frontend tooling |
| React Router | Navigation |
| Framer Motion | UI animation |
| Lucide React | Icons |
| React Markdown | Markdown rendering |
| React Hot Toast | Notifications |

---

## Browser Extension

NeuroShield also contains **VeritAI**, a browser-extension interface intended to bring NeuroShield's trust analysis directly into the browsing experience.

The extension is designed around the idea of:

```text
Current Page
     ↓
Current URL / Selected Text
     ↓
NeuroShield API
     ↓
Trust Analysis
     ↓
Actionable Result
```

---

# 📁 Project Structure

```text
NeuroShield/
│
├── agents/
│   │
│   ├── fact_check_agent/
│   │   ├── __init__.py
│   │   ├── agent_state.py
│   │   ├── extraction_claim.py
│   │   ├── main.py
│   │   ├── report_gen.py
│   │   └── search_and_verify.py
│   │
│   ├── privacy_agent/
│   │   ├── __init__.py
│   │   ├── chat_agent.py
│   │   ├── graph.py
│   │   ├── nodes.py
│   │   └── state.py
│   │
│   ├── website_scan_agent/
│   │   ├── __init__.py
│   │   ├── chat_agent.py
│   │   ├── graph.py
│   │   ├── nodes.py
│   │   └── state.py
│   │
│   └── shared/
│       ├── config.py
│       ├── embeddings.py
│       ├── evidence.py
│       ├── llm.py
│       ├── reliability.py
│       ├── risk_engine.py
│       └── utils.py
│
├── backend/
│   └── server.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   │   └── hero.png
│   │   │
│   │   ├── components/
│   │   │   ├── ChatPanel.jsx
│   │   │   ├── FeatureCard.jsx
│   │   │   ├── Footer.jsx
│   │   │   ├── LoadingState.jsx
│   │   │   ├── Navbar.jsx
│   │   │   ├── ProgressBar.jsx
│   │   │   ├── ScoreGauge.jsx
│   │   │   └── VerdictBadge.jsx
│   │   │
│   │   ├── pages/
│   │   │   ├── FactChecker.jsx
│   │   │   ├── LandingPage.jsx
│   │   │   ├── PrivacyAnalyzer.jsx
│   │   │   └── WebsiteScanner.jsx
│   │   │
│   │   ├── services/
│   │   │   └── api.js
│   │   │
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── package.json
│   └── vite.config.js
│
├── extension/
│   └── ...
│
├── .gitignore
├── .python-version
├── LICENSE
├── README.md
├── main.py
├── pyproject.toml
├── requirements.txt
└── uv.lock
```

---

# ⚙️ Local Setup

## Prerequisites

Make sure you have:

- Python 3.12+
- Node.js 20+
- npm
- Git
- `uv` package manager

---

# 🔑 Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Optional configuration:

```env
GEMINI_MODEL=gemini-3.6-flash

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

MAX_LLM_WORKERS=3
MAX_SEARCH_WORKERS=3

TAVILY_MAX_RESULTS=5

REQUEST_TIMEOUT=15
MAX_RETRIES=3
```

> **Never commit `.env` or API keys to GitHub.**

---

# ▶️ Running the Backend

From the project root:

```bash
uv sync
```

Then:

```bash
uv run uvicorn backend.server:app --reload --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

Health endpoint:

```text
/api/health
```

---

# ▶️ Running the Frontend

Open a second terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Frontend:

```text
http://localhost:5173
```

The Vite development server proxies API requests to the FastAPI backend.

---

# 🧪 Testing

Python compilation:

```bash
uv run python -m py_compile backend/server.py
```

Run the test suite:

```bash
uv run pytest
```

Frontend production build:

```bash
cd frontend
npm run build
```

---

# 🔌 API Endpoints

## Privacy

### Analyze Privacy Policy

```http
POST /api/privacy/analyze
```

Request:

```json
{
  "raw_text": "Privacy policy text..."
}
```

---

### Privacy Chat

```http
POST /api/privacy/chat
```

---

## Fact Checker

### Analyze Claims

```http
POST /api/factcheck/analyze
```

Request:

```json
{
  "input_text": "The Earth revolves around the Sun..."
}
```

Response contains:

- extracted claims
- evidence
- verification results
- confidence
- final report

---

## Website Scanner

### Scan Website

```http
POST /api/scanner/scan
```

Request:

```json
{
  "url": "https://example.com"
}
```

---

### Website Safety Chat

```http
POST /api/scanner/chat
```

---

## Health

```http
GET /api/health
```

---

# 🛡️ Risk Scoring

NeuroShield uses a shared risk engine for deterministic score calculation.

The scoring model starts at:

```text
100 = maximum trust score
```

Risk signals apply penalties according to their severity and relevance.

The resulting score is mapped into a verdict:

```text
80–100   → Safe
50–79    → Moderate Risk
25–49    → High Risk
0–24     → Critical Risk
```

The score is intended to summarize detected signals rather than represent an absolute guarantee of safety.

---

# 🔬 Design Principles

## 1. Evidence over confidence

A confident AI answer is not automatically a trustworthy answer.

NeuroShield prioritizes:

```text
Evidence
   ↓
Reasoning
   ↓
Confidence
   ↓
Verdict
```

---

## 2. Structured AI outputs

Where AI reasoning is required, NeuroShield uses structured Pydantic outputs rather than relying exclusively on free-form text.

This provides:

- predictable schemas
- validation
- easier API integration
- more reliable frontend rendering
- easier testing

---

## 3. Deterministic components where possible

Not every task requires an LLM.

NeuroShield deliberately uses deterministic logic for areas such as:

- risk scoring
- verdict mapping
- report generation
- evidence mapping
- URL heuristics
- validation

This reduces unnecessary LLM calls and makes system behavior more reproducible.

---

## 4. Graceful degradation

External AI and search services can fail because of:

- rate limits
- network errors
- provider outages
- API failures

The architecture therefore separates:

```text
AI reasoning
      +
Search evidence
      +
Deterministic processing
```

so individual failures can be handled without making the entire system dependent on a single component.

---

# 🎯 Hackathon Vision

NeuroShield is being developed as more than a collection of AI demos.

The larger vision is:

> **A real-time trust layer that helps users evaluate digital information before they act on it.**

A future browsing experience could look like:

```text
User opens a website
        ↓
NeuroShield detects the page
        ↓
Website Intelligence
        ↓
Privacy Intelligence
        ↓
Fact Intelligence
        ↓
Evidence aggregation
        ↓
Risk analysis
        ↓
┌─────────────────────────────┐
│     NEUROSHIELD TRUST       │
│                             │
│     Score: 82 / 100         │
│     SAFE                    │
│                             │
│  ✓ Valid HTTPS              │
│  ✓ Normal URL structure     │
│  ⚠ Data sharing detected    │
│  ✓ Evidence available       │
│                             │
│     View Evidence →         │
└─────────────────────────────┘
```

The long-term objective is to make web trust analysis **contextual, explainable, and actionable**.

---

# 🗺️ Roadmap

## Current Development

- [x] FastAPI backend
- [x] LangGraph agent architecture
- [x] Privacy policy analysis
- [x] Structured privacy findings
- [x] Evidence model
- [x] Shared risk engine
- [x] Gemini integration
- [x] Tavily integration
- [x] Local Hugging Face embeddings
- [x] FAISS retrieval
- [x] AI claim extraction
- [x] Web evidence retrieval
- [x] Fact verification pipeline
- [x] Deterministic report generation
- [x] Website URL analysis
- [x] SSL/TLS inspection
- [x] React frontend
- [x] Responsive application shell
- [x] VeritAI extension foundation

## In Progress

- [ ] Evidence-first React UX
- [ ] Advanced website reputation signals
- [ ] Stronger domain intelligence
- [ ] Fact Checker fallback/reliability layer
- [ ] Advanced Chrome extension experience
- [ ] Comprehensive automated test suite
- [ ] Performance optimization
- [ ] Production deployment

## Future

- [ ] RDAP/domain registration intelligence
- [ ] Larger reputation-source aggregation
- [ ] Real-time browsing analysis
- [ ] Cross-agent evidence correlation
- [ ] Explainable trust graphs
- [ ] Advanced phishing detection
- [ ] Multimodal webpage analysis
- [ ] Privacy-risk trend tracking
- [ ] Browser-wide trust dashboard

---

# ⚠️ Current Limitations

NeuroShield is an active development project.

Some analysis currently relies on heuristics or AI interpretation and should therefore **not be treated as a definitive security, legal, or factual guarantee**.

In particular:

- Website reputation analysis is still being strengthened with more direct observable sources.
- Domain-age intelligence is currently an area of active improvement.
- External AI/search services may impose rate limits.
- AI-generated conclusions can still contain errors.
- Website safety scores are risk indicators, not guarantees of safety.
- Fact verification depends on the quality and availability of retrieved evidence.

The system is designed to communicate uncertainty rather than hide it.

---

# 🔐 Security & Privacy

NeuroShield is designed with a local-first mindset where practical.

For example:

- Embeddings are generated locally.
- FAISS retrieval runs locally.
- API credentials are stored in environment variables.
- `.env` is excluded from version control.
- Deterministic processing is preferred when LLM reasoning is unnecessary.

Users should still avoid submitting highly sensitive personal information to external AI/search providers unless they understand the applicable provider policies.

---

# 📜 License

This project is licensed under the terms specified in the repository's `LICENSE` file.

---

# 👨‍💻 Project

**NeuroShield AI**

### AI Trust Layer for the Web

```text
Detect → Verify → Explain → Recommend
```

Built with:

**Python · FastAPI · LangGraph · Gemini · Tavily · Hugging Face · FAISS · React · Vite**

---

> **Don't just trust the web. Understand it.**
