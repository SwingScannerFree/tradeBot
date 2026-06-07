import streamlit as st
from swing_engine import run_screener, render_results

st.set_page_config(page_title="SwingScan Free", layout="wide")

# -------------------------------
# MAIN APP
# -------------------------------
st.title("SwingScan Free")
st.caption("Free swing trading screener — no login required.")

if st.button("Run Scan"):
    with st.spinner("Analyzing a universe of over 4,000 stocks for high‑probability swing setups..."):
        results = run_screener()

    if not results:
        st.warning("No candidates found.")
    else:
        render_results(results)   # <-- NEW UI CARDS
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


