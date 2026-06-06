# universe_loader.py

import streamlit as st
import requests
from bs4 import BeautifulSoup
import random
import time

FINVIZ_URL = (
    "https://finviz.com/screener.ashx?v=111&f="
    "exch_amex,exch_nasd,exch_nyse,"
    "sh_price_o2,sh_avgvol_o100,sh_mktcap_o50,geo_usa"
)

# Multiple strong user agents to rotate through
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0 Safari/537.36",
]


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


def fetch_page(url):
    """Fetch a Finviz page with retries and rotating user agents."""
    for _ in range(3):
        try:
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200 and "table-light" in resp.text:
                return resp.text
        except:
            pass
        time.sleep(1.2)  # small delay between retries
    return None


@st.cache_data(ttl=604800)  # 7 days
def load_universe():
    tickers = []
    page = 1

    while True:
        url = FINVIZ_URL + f"&r={1 + (page - 1) * 20}"
        html = fetch_page(url)

        if html is None:
            st.warning(f"Finviz blocked page {page}. Stopping early.")
            break

        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("table.table-light tr[valign='top']")

        if not rows:
            break  # no more pages

        for row in rows:
            cols = row.find_all("td")
            if len(cols) > 1:
                t = cols[1].text.strip()
                t = clean_ticker(t)
                if t:
                    tickers.append(t)

        page += 1
        if page > 200:  # safety limit
            break

    tickers = sorted(list(set(tickers)))

    # Safety fallback so the app never crashes
    if len(tickers) == 0:
        st.error("Finviz returned no tickers. Using fallback universe.")
        return ["AAPL", "MSFT", "NVDA", "META", "AMZN"]

    return tickers
