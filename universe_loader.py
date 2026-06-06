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

    while True:
        url = FINVIZ_URL + f"&r={1 + (page - 1) * 20}"
        html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
        soup = BeautifulSoup(html, "html.parser")

        rows = soup.select("table.table-light tr[valign='top']")
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

    return sorted(list(set(tickers)))
