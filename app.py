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
        for r in results:
            header = f"{r['symbol']} — Score {r['score']} — Price ${r['price']:.2f}"
            with st.expander(header):
                st.markdown(r["reasoning"])
else:
    st.info("Tap 'Run Scan' to see today's swing candidates.")
