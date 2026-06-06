# universe_loader.py

import json
import streamlit as st

@st.cache_data(ttl=604800)  # refresh weekly
def load_universe():
    with open("universe.json", "r") as f:
        tickers = json.load(f)

    # safety fallback
    if len(tickers) == 0:
        return ["AAPL", "MSFT", "NVDA"]

    return tickers
