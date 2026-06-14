import streamlit as st
from swing_engine import run_screener, render_results

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(page_title="SwingScan Free", layout="wide")

# -----------------------------------
# MAIN APP
# -----------------------------------
st.title("SwingScan Free")
st.caption("ONLY SHOWING RESULTS WITH A SCORE OF 7 OR BETTER")

if st.button("Run Scan"):

    # UI elements for progress
    progress = st.progress(0)
    status = st.empty()

    # Define callback for engine to update UI
    def update_progress(ticker, i, total):
        percent = int((i + 1) / total * 100)
        progress.progress(percent)
        status.write(f"Scanning {ticker} ({percent}%)")

    # Run the screener with progress callback
    results = run_screener(progress_callback=update_progress)

    # Cleanup UI
    progress.empty()
    status.empty()

    # Filter results
    results = [r for r in results if r["score"] >= 7]
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
