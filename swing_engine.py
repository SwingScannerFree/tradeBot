# swing_engine.py
# Merged SwingBot Technical Engine (identical logic, yfinance version)

import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
import streamlit as st

###############################################################
# 1. LOAD UNIVERSE (universe.json)
###############################################################

def load_universe():
    path = "universe.json"
    if not os.path.exists(path):
        return []

    with open(path, "r") as f:
        data = json.load(f)

    if isinstance(data, dict) and "tickers" in data:
        return [t.upper() for t in data["tickers"]]
    if isinstance(data, list):
        return [t.upper() for t in data]

    return []


###############################################################
# 2. BULK DATA DOWNLOAD (6 months daily)
###############################################################

@st.cache_data(ttl=3600)
def load_bulk_data(universe):
    return yf.download(
        universe,
        period="6mo",
        interval="1d",
        group_by="ticker",
        threads=True
    )


###############################################################
# 3. INDICATORS (IDENTICAL TO BOT)
###############################################################

def add_indicators(df):
    df["ema9"] = df["Close"].ewm(span=9, adjust=False).mean()
    df["ema21"] = df["Close"].ewm(span=21, adjust=False).mean()

    df["vwap"] = (
        ((df["High"] + df["Low"] + df["Close"]) / 3 * df["Volume"]).cumsum()
        / df["Volume"].cumsum()
    )

    df["avg_vol_20"] = df["Volume"].rolling(20).mean()
    df["sma20"] = df["Close"].rolling(20).mean()
    df["sma50"] = df["Close"].rolling(50).mean()

    # Bollinger upper band
    mid = df["Close"].rolling(20).mean()
    std = df["Close"].rolling(20).std()
    df["bb_upper"] = mid + 2 * std

    # ATR14 (simple version like bot)
    df["tr"] = df["High"] - df["Low"]
    df["atr14"] = df["tr"].rolling(14).mean()

    return df


###############################################################
# 4. BOT SCORING FUNCTION (0–12 RAW SCORE)
###############################################################

def score_signal(last, prev):
    score = 0

    # EMA cross strength
    try:
        cross_strength = (last["ema9"] - last["ema21"]) / last["ema21"]
        if cross_strength > 0.002:
            score += 3
        elif cross_strength > 0.001:
            score += 2
        else:
            score += 1
    except:
        pass

    # VWAP strength
    try:
        vwap_strength = (last["Close"] - last["vwap"]) / last["vwap"]
        if vwap_strength > 0.01:
            score += 2
        elif vwap_strength > 0.003:
            score += 1
    except:
        pass

    # Volume surge
    try:
        vol_ratio = last["Volume"] / last["avg_vol_20"]
        if vol_ratio > 1.8:
            score += 3
        elif vol_ratio > 1.4:
            score += 2
        elif vol_ratio > 1.2:
            score += 1
    except:
        pass

    # ATR expansion
    try:
        atr_ratio = last["atr14"] / last["Close"]
        if atr_ratio > 0.025:
            score += 2
        elif atr_ratio > 0.018:
            score += 1
    except:
        pass

    # Candle quality
    try:
        body = abs(last["Close"] - last["Open"]) / last["Open"]
        rng = (last["High"] - last["Low"]) / last["Low"]
        if body < 0.01 and rng < 0.02:
            score += 2
        elif body < 0.015 and rng < 0.025:
            score += 1
    except:
        pass

    # Distance above SMA20
    try:
        sma20_dist = (last["Close"] - last["sma20"]) / last["sma20"]
        if sma20_dist > 0.02:
            score += 2
        elif sma20_dist > 0.01:
            score += 1
    except:
        pass

    return score


###############################################################
# 5. BOT SCAN LOGIC (IDENTICAL TECHNICAL FILTERS)
###############################################################

def run_screener():
    universe = load_universe()
    data = load_bulk_data(universe)

    results = []

    for symbol in universe:
        try:
            df = data[symbol].copy()
        except:
            continue

        df = add_indicators(df)

        if len(df) < 50:
            continue

        last = df.iloc[-1]
        prev = df.iloc[-2]

        close = float(last["Close"])
        volume = int(last["Volume"])

        # Price filter
        if not (5 < close < 250):
            continue

        # Volume filter
        if volume < 100000:
            continue

        # Candle quality
        body = abs(last["Close"] - last["Open"]) / last["Open"]
        rng = (last["High"] - last["Low"]) / last["Low"]
        if body > 0.02 or rng > 0.03:
            continue

        # ATR filter
        atr = last["atr14"]
        if pd.isna(atr) or (atr / close) < 0.015:
            continue

        # Fresh EMA cross
        if not (
            prev["ema9"] < prev["ema21"]
            and last["ema9"] > last["ema21"]
            and (last["ema9"] - last["ema21"]) / last["ema21"] > 0.0005
        ):
            continue

        # SMA20 rising + price above SMA20
        if last["sma20"] <= prev["sma20"]:
            continue
        if close <= last["sma20"]:
            continue

        # VWAP
        above_vwap = (close - last["vwap"]) / last["vwap"] > 0.002

        # Not overbought
        not_overbought = close < last["bb_upper"] * 0.985

        # High volume
        high_volume = volume > last["avg_vol_20"] * 1.4

        # Confluence
        confluence = sum([above_vwap, not_overbought, high_volume])
        if confluence < 2:
            continue

        # Score
        score = score_signal(last, prev)

        results.append({
            "symbol": symbol,
            "price": close,
            "volume": volume,
            "confluence": confluence,
            "atr": float(atr),
            "score": int(score),
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)
