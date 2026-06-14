import streamlit as st
from swing_engine import (
    run_screener,
    render_results,
    save_picks,
    evaluate_pick_performance
)

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(page_title="Swing Scan", layout="wide")

# -----------------------------------
# MAIN APP
# -----------------------------------
st.title("Swing Scan")
st.caption("ONLY SHOWING RESULTS WITH A SCORE OF 7 OR BETTER")

if st.button("RUN SCAN"):

    # UI elements for progress + description
    progress = st.progress(0)
    status = st.empty()
    description = st.empty()

    # General description shown during the scan
    description.write(
        """
        <div style='font-size:16px; padding:8px 0;'>
            <strong>Swing Scan is analyzing the entire U.S. stock universe…</strong><br>
            Evaluating trend structure, volatility, volume patterns, VWAP alignment, 
            Bollinger positioning, and multi‑factor confluence to identify high‑probability swing setups.
        </div>
        """,
        unsafe_allow_html=True
    )

    # Progress callback
    def update_progress(ticker, i, total):
        percent = int((i + 1) / total * 100)
        progress.progress(percent)
        status.write(f"Scanning… {percent}%")

    # Run the screener
    results = run_screener(progress_callback=update_progress)

    # Cleanup UI
    description.empty()
    status.empty()
    progress.empty()

    # Filter results
    results = [r for r in results if r["score"] >= 7]
    results = [r for r in results if r["confluence"] >= 2]

    # Save today's picks
    save_picks(results)

    # Display results
    if not results:
        st.warning("No candidates found.")
    else:
        render_results(results)

# -----------------------------------
# RECENT PICK PERFORMANCE (COLOR CODED + TRADINGVIEW LINKS)
# -----------------------------------
st.subheader("Recent Picks Performance")

perf = evaluate_pick_performance()

for p in perf:
    symbol = p["symbol"]
    change = p["change_pct"]

    if change is None:
        color = "gray"
        text = "no data"
    else:
        color = "green" if change >= 0 else "red"
        sign = "+" if change >= 0 else ""
        text = f"{sign}{change:.2f}%"

    tv_url = f"https://www.tradingview.com/symbols/{symbol}/"

    st.markdown(
        f"<a href='{tv_url}' target='_blank' style='text-decoration:none;'>"
        f"<span style='color:{color}; font-size:16px;'><strong>{symbol}</strong> — {text}</span>"
        f"</a>",
        unsafe_allow_html=True
    )


else:
    st.info("Tap 'RUN SCAN' to see current swing candidates.")

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
