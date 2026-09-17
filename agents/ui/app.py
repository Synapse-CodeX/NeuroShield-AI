import streamlit as st

from agents.shared.utils import get_risk_level
from agents.privacy_agent.graph import build_graph
from agents.privacy_agent.chat_agent import ask_privacy_question

# --- INIT ---
@st.cache_resource
def get_app():
    return build_graph()

app = get_app()

st.set_page_config(page_title="Privacy Policy Analyzer", layout="wide")

st.title("🔐 Privacy Policy Analyzer")
st.markdown("Analyze privacy policies and ask questions about them.")

# --- SESSION STATE ---
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "result" not in st.session_state:
    st.session_state.result = {}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- INPUT ---
text_input = st.text_area("Paste Privacy Policy Text", height=250)

# --- ANALYZE BUTTON ---
if st.button("Analyze"):
    if not text_input.strip():
        st.warning("Please enter some text.")
    else:
        try:
            st.session_state.analysis_done = False  # reset

            with st.spinner("Analyzing..."):
                input_data = {"raw_text": text_input}
                result = app.invoke(input_data)

                # Save results
                st.session_state.result = result
                st.session_state.analysis_done = True
                st.session_state.chat_history = []

        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
            st.stop()

# --- DISPLAY RESULTS ---
# --- DISPLAY RESULTS ---
if st.session_state.analysis_done:
    result = st.session_state.result

    # Safe extraction
    score = result.get("score", 0)
    structured_data = result.get("structured_data", {})
    risks = result.get("risks", [])
    summary = result.get("summary", "No summary available.")

    risk_level = get_risk_level(score)

    # 🔥 MOVE COLUMNS HERE (inside block)
    col1, col2 = st.columns([2, 1])

    # ================= LEFT SIDE (ANALYSIS) =================
    with col1:
        st.subheader("📊 Privacy Score")
        st.metric("Score", f"{score}/100", delta=risk_level)

        if risk_level == "HIGH":
            st.error(f"⚠️ Risk Level: {risk_level}")
        elif risk_level == "MEDIUM":
            st.warning(f"⚠️ Risk Level: {risk_level}")
        else:
            st.success(f"✅ Risk Level: {risk_level}")

        st.subheader("📌 Key Data Insights")
        for key, value in structured_data.items():
            if value:
                if isinstance(value, list):
                    st.write(f"**{key.replace('_', ' ').title()}**: {', '.join(value)}")
                else:
                    st.write(f"**{key.replace('_', ' ').title()}**: {value}")

        st.subheader("🚨 Risks Detected")
        if risks:
            for r in risks:
                st.write(f"- {r}")
        else:
            st.write("No major risks detected.")

        st.subheader("🧾 Summary")
        st.write(summary)

    # ================= RIGHT SIDE (CHAT) =================
    with col2:
        st.subheader("💬 Chat")

        if "vector_store" not in result:
            st.warning("Chat unavailable")
        else:
            # Chat history
            for role, msg in st.session_state.chat_history:
                with st.chat_message("user" if role == "You" else "assistant"):
                    st.markdown(msg)

            # Chat input
            if user_query := st.chat_input("Ask..."):
                with st.chat_message("user"):
                    st.markdown(user_query)

                try:
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            answer = ask_privacy_question(
                                question=user_query,
                                analysis_result=result,
                                chat_history=st.session_state.chat_history,
                            )

                            st.markdown(answer)

                            st.session_state.chat_history.append(("You", user_query))
                            st.session_state.chat_history.append(("Agent", answer))

                except Exception as e:
                    st.error(f"Chat error: {str(e)}")

        # Buttons
        if st.button("🧹 Clear Chat"):
            st.session_state.chat_history = []

        if st.button("🔄 Reset"):
            st.session_state.analysis_done = False
            st.session_state.result = {}
            st.session_state.chat_history = []