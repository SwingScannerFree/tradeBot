# universe_loader.py

import streamlit as st
import requests
from bs4 import BeautifulSoup

FINVIZ_URL = (
    "https://finviz.com/screener.ashx?v=111&f="
    "exch_amex,exch_nasd,exch_nyse,"
    "sh_price_o2,sh_avgvol_o100,sh_mktcap_o50,geo_usa"
)

def clean_ticker(t):
    """Remove ETFs, warrants, SPAC units, rights, preferred shares, etc."""
    bad_suffixes = ("W", "WS", "U", "R")
    if "." in t:
        return None
    if t.endswith(bad_suffixes):
        return None
    if len(t) > 5:
        return None
    return t


@st.cache_data(ttl=604800)  # 7 days
def load_universe():
    tickers = []
    page = 1

    # Strong User-Agent to avoid Finviz blocking Streamlit Cloud
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        )
    }

    while True:
        url = FINVIZ_URL + f"&r={1 + (page - 1) * 20}"

        try:
            response = requests.get(url, headers=headers, timeout=10)
            html = response.text
        except Exception:
            break

        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("table.table-light tr[valign='top']")

        # If Finviz blocks or no more pages → stop
        if not rows:
            break

        for row in rows:
            cols = row.find_all("td")
            if len(cols) > 1:
                t = cols[1].text.strip()
                t = clean_ticker(t)
                if t:
                    tickers.append(t)

        page += 1

    tickers = sorted(list(set(tickers)))

    # Safety fallback so the app never crashes
    if len(tickers) == 0:
        return ["AAPL", "MSFT", "NVDA"]

    return tickers

