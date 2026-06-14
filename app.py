import streamlit as st
from swing_engine import run_screener, render_results

# -------------------------------
# PAGE CONFIG (must come first)
# -------------------------------
st.set_page_config(page_title="SwingScan Free", layout="wide")

# -------------------------------
# GOOGLE ANALYTICS (GA4)
# Script + iframe fallback
# -------------------------------
GA_SCRIPT = """
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-TKXHMKH4WK"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-TKXHMKH4WK');
</script>
"""
st.markdown(GA_SCRIPT, unsafe_allow_html=True)

# Guaranteed execution inside Streamlit Cloud
GA_IFRAME = """
<iframe src="https://www.googletagmanager.com/ns.html?id=G-TKXHMKH4WK"
height="0" width="0" style="display:none;visibility:hidden"></iframe>
"""
st.markdown(GA_IFRAME, unsafe_allow_html=True)

# -------------------------------
# MAIN APP
# -------------------------------
st.title("SwingScan Free")
st.caption("ONLY SHOWING RESULTS WITH A SCORE OF 7 OR BETTER")

if st.button("Run Scan"):
    with st.spinner("Analyzing a universe of over 4,000 stocks for high‑probability swing setups..."):
        results = run_screener()

        # -------------------------------
        # HARD‑WIRED FILTERS
        # -------------------------------

        # Only show score 7 or better
        results = [r for r in results if r["score"] >= 7]

        # Only show confluence 2 or better
        results = [r for r in results if r["confluence"] >= 2]

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
