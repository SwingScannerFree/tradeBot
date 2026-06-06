# swing_engine.py

import yfinance as yf
import pandas as pd
import numpy as np
from universe_loader import load_universe
import streamlit as st

@st.cache_data(ttl=3600)
def load_bulk_data(universe):
    return yf.download(
        universe,
        period="6mo",
        interval="1d",
        group_by="ticker",
        threads=True
    )

def add_indicators(df):
    df["sma20"] = df["Close"].rolling(20).mean()
    df["sma50"] = df["Close"].rolling(50).mean()
    df["atr14"] = (df["High"] - df["Low"]).rolling(14).mean()
    return df

def score_stock(df):
    if df is None or len(df) < 60:
        return None

    last = df.iloc[-1]
    score = 0
    reasons = []

    # Trend
    if last["sma20"] > last["sma50"]:
        score += 30
        reasons.append("Short-term trend (20 SMA) above medium-term (50 SMA).")
    else:
        reasons.append("Short-term trend not above medium-term.")

    # Price vs 50 SMA
    if last["Close"] > last["sma50"]:
        score += 20
        reasons.append("Price above 50 SMA (uptrend confirmation).")
    else:
        reasons.append("Price below 50 SMA (possible weakness).")

    # ATR sanity
    if last["atr14"] and last["atr14"] > 0:
        atr_pct = last["atr14"] / last["Close"]
        if 0.01 <= atr_pct <= 0.05:
            score += 20
            reasons.append("ATR volatility in a reasonable swing range.")
        else:
            reasons.append(f"ATR volatility {atr_pct:.2%} outside ideal swing range.")
    else:
        reasons.append("ATR not available or zero.")

    # Momentum
    recent = df.tail(10)
    up_days = np.sum(recent["Close"] > recent["Open"])
    if up_days >= 6:
        score += 15
        reasons.append(f"{up_days}/10 recent days closed green (positive momentum).")
    else:
        reasons.append(f"{up_days}/10 recent days closed green (weak momentum).")

    # Liquidity
    avg_vol = recent["Volume"].mean()
    if avg_vol > 2_000_000:
        score += 15
        reasons.append("Average volume > 2M (good liquidity).")
    else:
        reasons.append("Average volume < 2M (low liquidity).")

    return {
        "symbol": df.name,
        "score": score,
        "price": last["Close"],
        "atr": last["atr14"],
        "reasoning": "\n".join(f"• {r}" for r in reasons)
    }

def run_screener():
    universe = load_universe()
    data = load_bulk_data(universe)

    results = []
    for symbol in universe:
        try:
            df = data[symbol]
            df.name = symbol
            df = add_indicators(df)
            scored = score_stock(df)
            if scored:
                results.append(scored)
        except:
            continue

    return sorted(results, key=lambda x: x["score"], reverse=True)
