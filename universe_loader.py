import json
import streamlit as st

@st.cache_data(ttl=604800)
def load_universe():
    with open("universe.json", "r") as f:
        data = json.load(f)

    # Extract the list
    tickers = data.get("tickers", [])

    # Validate
    if not isinstance(tickers, list):
        st.error("Universe file is invalid — expected a list under 'tickers'.")
        return ["AAPL", "MSFT", "NVDA"]

    if len(tickers) == 0:
        st.error("Universe is empty — using fallback.")
        return ["AAPL", "MSFT", "NVDA"]

    return tickers
