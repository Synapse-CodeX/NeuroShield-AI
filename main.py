import streamlit as st

pg = st.navigation([
    st.Page("agents/ui/app.py", title="Privacy Policy Analyzer", icon="🔐"),
    st.Page("agents/ui/website_scan.py", title="Website Safety Scanner", icon="🛡️"),
])
pg.run()
