import streamlit as st
from swing_engine import run_screener, render_results

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(page_title="SwingScan Free", layout="wide")

# -----------------------------------
# GA4 LOADER (GitHub Pages iframe with sandbox permissions)
# -----------------------------------
st.markdown("""
<iframe 
    src="https://swingbotscanner.github.io/ga4-loader/" 
    height="0" 
    width="0" 
    style="display:none;"
    sandbox="allow-scripts allow-same-origin"
></iframe>
""", unsafe_allow_html=True)

# -----------------------------------
# MAIN APP
# -----------------------------------
st.title("SwingScan Free")
st.caption("ONLY SHOWING RESULTS WITH A SCORE OF 7 OR BETTER")

if st.button("Run Scan"):
    with st.spinner("Analyzing a universe of over 4,000 stocks for high‑probability swing setups..."):
        results = run_screener()

        # Only show score 7 or better
        results = [r for r in results if r["score"] >= 7]

        # Only show confluence 2 or better
        results = [r for r in results if r["confluence"] >= 2]

    if not results:
        st.warning("No candidates found.")
    else:
        render_results(results)
else:
    st.info("Tap 'Run Scan' to see today's swing candidates.")

# -----------------------------------
# AMAZON DEALS AFFILIATE BANNER
# -----------------------------------
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
