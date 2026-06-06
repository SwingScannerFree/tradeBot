# app.py

import streamlit as st
from swing_engine import run_screener

st.set_page_config(page_title="SwingBot Mobile", layout="wide")

st.title("SwingBot Mobile")
st.caption("Free swing trading screener — weekly universe — no login required.")

if st.button("Run Scan"):
    with st.spinner("Scanning universe..."):
        results = run_screener()

    if not results:
        st.warning("No candidates found.")
    else:
        for r in results[:5]:   # top 5 only
            header = f"{r['symbol']} — Score {r['score']} — Price ${r['price']:.2f}"
            with st.expander(header):
                st.markdown(r["reasoning"])
else:
    st.info("Tap 'Run Scan' to see today's swing candidates.")

# -------------------------------
# AMAZON AFFILIATE FOOTER (BOTTOM)
# -------------------------------

st.markdown("""
<hr>

<a href="https://www.amazon.com/?tag=swingbot00-20" target="_blank">
    <img src="https://m.media-amazon.com/images/G/01/AUIClients/AmazonUIBaseCSS-amazonlogo._CB485936611_.png" width="100%">
</a>

<p style="text-align:center;"><strong>As an Amazon Associate I earn from qualifying purchases.</strong></p>
""", unsafe_allow_html=True)
