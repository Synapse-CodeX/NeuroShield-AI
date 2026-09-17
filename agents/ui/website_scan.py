import streamlit as st
import json

from agents.website_scan_agent.graph import build_graph as build_scan_graph
from agents.website_scan_agent.chat_agent import ask_website_safety_question


# ── Cached graph ──
@st.cache_resource
def get_scan_app():
    return build_scan_graph()


scan_app = get_scan_app()

# ── Page config is set in main.py; do NOT call set_page_config here ──

# ── Colour helpers ──
_VERDICT_CFG = {
    "SAFE":       {"color": "#10b981", "icon": "✅", "bg": "#052e16"},
    "CAUTION":    {"color": "#f59e0b", "icon": "⚠️",  "bg": "#422006"},
    "SUSPICIOUS": {"color": "#f97316", "icon": "🚨", "bg": "#431407"},
    "DANGEROUS":  {"color": "#ef4444", "icon": "🛑", "bg": "#450a0a"},
}

_SCORE_LABELS = {
    "url_structure":   ("🔗", "URL Structure"),
    "domain_age":      ("📅", "Domain Age"),
    "scam_reports":    ("🚨", "Scam Reports"),
    "ssl_certificate": ("🔒", "SSL Certificate"),
    "content_quality": ("📝", "Content Quality"),
    "reputation":      ("⭐", "Reputation"),
}


def _score_color(score: int) -> str:
    if score >= 75:
        return "#10b981"
    if score >= 50:
        return "#f59e0b"
    if score >= 25:
        return "#f97316"
    return "#ef4444"


def _progress_bar(label: str, score: int, icon: str = "") -> str:
    color = _score_color(score)
    return f"""
    <div style="margin-bottom:12px">
      <div style="display:flex;justify-content:space-between;margin-bottom:4px">
        <span style="font-weight:600;font-size:0.9rem">{icon} {label}</span>
        <span style="font-weight:700;color:{color}">{score}/100</span>
      </div>
      <div style="background:#1e293b;border-radius:8px;height:10px;overflow:hidden">
        <div style="width:{score}%;height:100%;background:{color};border-radius:8px;
                    transition:width .6s ease"></div>
      </div>
    </div>"""


# ══════════════════════════════════════════════════════════════════════
#  PAGE LAYOUT
# ══════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
  .scan-header {
    text-align:center; padding:1.5rem 0 0.5rem;
  }
  .scan-header h1 {
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-size:2.4rem; font-weight:800; margin:0;
  }
  .scan-header p { color:#94a3b8; font-size:1.05rem; margin-top:4px; }
  .verdict-card {
    border-radius:16px; padding:24px 28px; margin:20px 0;
    text-align:center; border:1px solid rgba(255,255,255,0.08);
  }
  .verdict-score { font-size:3.2rem; font-weight:800; margin:8px 0 0; }
  .verdict-label { font-size:1.4rem; font-weight:700; letter-spacing:1px; }
  .detail-card {
    background:#0f172a; border:1px solid #1e293b; border-radius:12px;
    padding:18px 20px; margin-bottom:14px;
  }
  .detail-card h4 { margin:0 0 8px; color:#e2e8f0; }
  .flag-item { color:#fbbf24; font-size:0.88rem; margin:2px 0; }
  .rec-item {
    background:#1e293b; border-radius:8px; padding:10px 14px;
    margin:6px 0; font-size:0.92rem; color:#e2e8f0;
  }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="scan-header">
  <h1>🛡️ Website Safety Scanner</h1>
  <p>Detect phishing, scam &amp; fake websites instantly</p>
</div>
""", unsafe_allow_html=True)


# ── Session state ──
if "scan_done" not in st.session_state:
    st.session_state.scan_done = False
if "scan_result" not in st.session_state:
    st.session_state.scan_result = {}
if "scan_chat_history" not in st.session_state:
    st.session_state.scan_chat_history = []

# ── URL Input ──
col_input, col_btn = st.columns([4, 1])
with col_input:
    url_input = st.text_input(
        "Enter website URL",
        placeholder="e.g.  https://example.com",
        label_visibility="collapsed",
    )
with col_btn:
    scan_clicked = st.button("🔍 Scan", use_container_width=True, type="primary")

# ── Scan action ──
if scan_clicked:
    url = url_input.strip()
    if not url:
        st.warning("Please enter a URL to scan.")
    else:
        try:
            st.session_state.scan_done = False
            with st.spinner("🔍 Scanning website… this may take a moment"):
                result = scan_app.invoke({"url": url})
                st.session_state.scan_result = result
                st.session_state.scan_done = True
                st.session_state.scan_chat_history = []
        except Exception as e:
            st.error(f"Scan failed: {e}")
            st.stop()


# ══════════════════════════════════════════════════════════════════════
#  RESULTS
# ══════════════════════════════════════════════════════════════════════

if st.session_state.scan_done:
    result = st.session_state.scan_result

    overall  = result.get("overall_score", 0)
    verdict  = result.get("verdict", "CAUTION")
    scores   = result.get("scores", {})
    recs     = result.get("recommendations", [])
    vcfg     = _VERDICT_CFG.get(verdict, _VERDICT_CFG["CAUTION"])

    # ── Verdict banner ──
    st.markdown(f"""
    <div class="verdict-card" style="background:{vcfg['bg']};border-color:{vcfg['color']}40">
      <div class="verdict-score" style="color:{vcfg['color']}">{overall}/100</div>
      <div class="verdict-label" style="color:{vcfg['color']}">{vcfg['icon']} {verdict}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Two-column layout ──
    col_left, col_right = st.columns([3, 2])

    # ═══ LEFT: Score breakdown ═══
    with col_left:
        st.subheader("📊 Score Breakdown")

        bars_html = ""
        for key, (icon, label) in _SCORE_LABELS.items():
            s = scores.get(key, 0)
            bars_html += _progress_bar(label, s, icon)

        st.markdown(bars_html, unsafe_allow_html=True)

        # ── Flags / findings ──
        st.subheader("🔎 Findings")

        detail_keys = [
            ("url_analysis",         "🔗 URL Structure"),
            ("domain_age_analysis",  "📅 Domain Age"),
            ("scam_report_analysis", "🚨 Scam Reports"),
            ("ssl_analysis",         "🔒 SSL Certificate"),
            ("content_analysis",     "📝 Content Quality"),
            ("reputation_analysis",  "⭐ Reputation"),
        ]

        for key, title in detail_keys:
            data = result.get(key, {})
            flags = data.get("flags", [])
            details = data.get("details", [])
            notes = data.get("notes", [])
            red_flags = data.get("red_flags", [])
            items = flags + details + notes + red_flags

            if not items:
                continue

            with st.expander(f"{title}", expanded=False):
                for item in items:
                    st.markdown(f"- ⚠️ {item}")

    # ═══ RIGHT: Recommendations + Chat ═══
    with col_right:
        st.subheader("💡 Recommendations")
        if recs:
            for i, rec in enumerate(recs, 1):
                st.markdown(f"""<div class="rec-item">
                    <strong>{i}.</strong> {rec}
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No specific recommendations.")

        st.markdown("---")

        # ── Chat ──
        st.subheader("💬 Ask about this scan")

        for role, msg in st.session_state.scan_chat_history:
            with st.chat_message("user" if role == "You" else "assistant"):
                st.markdown(msg)

        if user_q := st.chat_input("e.g. Is the SSL certificate valid?"):
            with st.chat_message("user"):
                st.markdown(user_q)

            try:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking…"):
                        answer = ask_website_safety_question(
                            question=user_q,
                            analysis_result=result,
                            chat_history=st.session_state.scan_chat_history,
                        )
                        st.markdown(answer)

                        st.session_state.scan_chat_history.append(("You", user_q))
                        st.session_state.scan_chat_history.append(("Agent", answer))
            except Exception as e:
                st.error(f"Chat error: {e}")

        # ── Action buttons ──
        bcol1, bcol2 = st.columns(2)
        with bcol1:
            if st.button("🧹 Clear Chat", key="scan_clear"):
                st.session_state.scan_chat_history = []
        with bcol2:
            if st.button("🔄 New Scan", key="scan_reset"):
                st.session_state.scan_done = False
                st.session_state.scan_result = {}
                st.session_state.scan_chat_history = []
