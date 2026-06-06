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
# AMAZON DEALS AFFILIATE BANNER
# -------------------------------

st.markdown("""
<hr>

<div style="
    width:100%;
    background:#232F3E;
    padding:18px 0;
    border-radius:6px;
    text-align:center;
">
    <a href="https://www.amazon.com/deals?tag=swingbot00-20" target="_blank" style="text-decoration:none;">
        <div style="color:white; font-size:22px; font-weight:700;">
            Amazon Deals
        </div>
        <div style="color:#FF9900; font-size:16px; margin-top:4px;">
            Support SwingBot at no extra cost
        </div>
    </a>
</div>

<p style="text-align:center; margin-top:10px;">
    <strong>As an Amazon Associate I earn from qualifying purchases.</strong>
</p>
""", unsafe_allow_html=True)

