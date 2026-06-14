import os
import json
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime

# ============================================================
# 0. UNIVERSE (LOCAL ONLY — NO FINVIZ)
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_UNIVERSE_FILE = os.path.join(BASE_DIR, "universe.json")
PICKS_FILE = os.path.join(BASE_DIR, "recent_picks.json")

def load_local_universe():
    if not os.path.exists(LOCAL_UNIVERSE_FILE):
        return []

    try:
        with open(LOCAL_UNIVERSE_FILE, "r") as f:
            data = json.load(f)

        if isinstance(data, dict) and "tickers" in data:
            tickers = data["tickers"]
        elif isinstance(data, list):
            tickers = data
        else:
            tickers = []

        return [t.upper() for t in tickers if isinstance(t, str)]
    except Exception:
        return []

def get_universe():
    return load_local_universe()


# ============================================================
# 1. DATA LOAD (YFINANCE)
# ============================================================

@st.cache_data(ttl=3600)
def load_bulk_data(universe):
    data = yf.download(
        universe,
        period="6mo",
        interval="1d",
        group_by="ticker",
        threads=True
    )

    frames = []
    for symbol in universe:
        try:
            df = data[symbol].copy()
            df["symbol"] = symbol
            df.reset_index(inplace=True)
            df.rename(columns={
                "Date": "datetime",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Adj Close": "adj_close",
                "Volume": "volume",
            }, inplace=True)
            frames.append(df)
        except Exception:
            continue

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


# ============================================================
# 2. INDICATORS (BOT-ACCURATE)
# ============================================================

def add_indicators(df):
    if df.empty:
        return df

    df = df.sort_values(["symbol", "datetime"]).reset_index(drop=True)

    df["ema9"] = df.groupby("symbol")["close"].transform(
        lambda x: x.ewm(span=9, adjust=False).mean()
    )
    df["ema21"] = df.groupby("symbol")["close"].transform(
        lambda x: x.ewm(span=21, adjust=False).mean()
    )

    df["vwap"] = (
        ((df["high"] + df["low"] + df["close"]) / 3 * df["volume"])
        .groupby(df["symbol"])
        .cumsum()
        / df["volume"].groupby(df["symbol"]).cumsum()
    )

    bb = (
        df.groupby("symbol")[["close"]]
          .apply(lambda g: pd.DataFrame({
              "bb_mid": g["close"].rolling(20).mean(),
              "bb_upper": g["close"].rolling(20).mean() + 2 * g["close"].rolling(20).std()
          }))
          .reset_index(level=0, drop=True)
    )
    df["bb_upper"] = bb["bb_upper"]

    df["avg_vol_20"] = df.groupby("symbol")["volume"].transform(
        lambda x: x.rolling(20).mean()
    )
    df["sma20"] = df.groupby("symbol")["close"].transform(
        lambda x: x.rolling(20).mean()
    )
    df["sma50"] = df.groupby("symbol")["close"].transform(
        lambda x: x.rolling(50).mean()
    )

    return df


# ============================================================
# 3. BOT SCORING FUNCTION (0–12)
# ============================================================

def score_signal(last, prev):
    score = 0

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

    try:
        vwap_strength = (last["close"] - last["vwap"]) / last["vwap"]
        if vwap_strength > 0.01:
            score += 2
        elif vwap_strength > 0.003:
            score += 1
    except:
        pass

    try:
        vol_ratio = last["volume"] / last["avg_vol_20"]
        if vol_ratio > 1.8:
            score += 3
        elif vol_ratio > 1.4:
            score += 2
        elif vol_ratio > 1.2:
            score += 1
    except:
        pass

    try:
        atr_ratio = last["atr14"] / last["close"]
        if atr_ratio > 0.025:
            score += 2
        elif atr_ratio > 0.018:
            score += 1
    except:
        pass

    try:
        body = abs(last["close"] - last["open"]) / last["open"]
        rng = (last["high"] - last["low"]) / last["low"]
        if body < 0.01 and rng < 0.02:
            score += 2
        elif body < 0.015 and rng < 0.025:
            score += 1
    except:
        pass

    try:
        sma20_dist = (last["close"] - last["sma20"]) / last["sma20"]
        if sma20_dist > 0.02:
            score += 2
        elif sma20_dist > 0.01:
            score += 1
    except:
        pass

    return int(score)


# ============================================================
# 3b. EXPLANATION BUILDER
# ============================================================

def explain_signal(last, prev):
    reasons = []

    try:
        if prev["ema9"] < prev["ema21"] and last["ema9"] > last["ema21"]:
            reasons.append("Fresh EMA9 > EMA21 bullish cross")
        else:
            reasons.append("EMA trend is positive but not a fresh cross")
    except:
        pass

    try:
        if (last["close"] - last["vwap"]) / last["vwap"] > 0.002:
            reasons.append("Price is above VWAP (intraday strength)")
        else:
            reasons.append("Price is near VWAP (neutral intraday strength)")
    except:
        pass

    try:
        if last["close"] < last["bb_upper"] * 0.985:
            reasons.append("Not overbought (below Bollinger upper band)")
        else:
            reasons.append("Near overbought levels")
    except:
        pass

    try:
        vol_ratio = last["volume"] / last["avg_vol_20"]
        if vol_ratio > 1.8:
            reasons.append("Strong volume surge")
        elif vol_ratio > 1.4:
            reasons.append("Moderate volume increase")
        elif vol_ratio > 1.2:
            reasons.append("Slight volume increase")
        else:
            reasons.append("Volume is normal")
    except:
        pass

    try:
        atr_ratio = last["atr14"] / last["close"]
        if atr_ratio > 0.025:
            reasons.append("ATR expansion (volatility rising)")
        elif atr_ratio > 0.018:
            reasons.append("Moderate ATR expansion")
        else:
            reasons.append("Low ATR expansion")
    except:
        pass

    try:
        body = abs(last["close"] - last["open"]) / last["open"]
        rng = (last["high"] - last["low"]) / last["low"]
        if body < 0.01 and rng < 0.02:
            reasons.append("Small‑body candle (controlled price action)")
        elif body < 0.015 and rng < 0.025:
            reasons.append("Moderate candle size")
        else:
            reasons.append("Wide candle (higher risk)")
    except:
        pass

    try:
        if last["close"] > last["sma20"] and last["sma20"] > prev["sma20"]:
            reasons.append("Price above rising SMA20 (trend confirmation)")
        else:
            reasons.append("Weak SMA20 trend")
    except:
        pass

    return reasons


# ============================================================
# 4. PICK TRACKING
# ============================================================

from datetime import datetime, timedelta

RETENTION_DAYS = 7  # keep picks for 7 days

def evaluate_pick_performance():
    data = load_recent_picks()
    if not data:
        return []

    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    cleaned = {}
    results = []

    for date, picks in data.items():
        try:
            entry_date = datetime.strptime(date, "%Y-%m-%d")
        except:
            continue

        # Skip old entries
        if entry_date < cutoff:
            continue

        # Keep fresh entries
        cleaned[date] = picks

        # Evaluate performance
        for p in picks:
            symbol = p["symbol"]
            entry = p["price"]

            try:
                df = yf.download(symbol, period="5d", interval="1d")
                latest = float(df["Close"].iloc[-1])
                change = (latest - entry) / entry * 100
            except:
                latest = None
                change = None

            results.append({
                "symbol": symbol,
                "entry_date": date,
                "entry_price": entry,
                "latest_price": latest,
                "change_pct": change
            })

    # Save cleaned data back to file
    with open(PICKS_FILE, "w") as f:
        json.dump(cleaned, f, indent=4)

    return results



# ============================================================
# 5. SCAN LOGIC (WITH PROGRESS CALLBACK)
# ============================================================

def is_etf(symbol):
    return symbol.endswith(("X", "F", "Q")) or symbol in {"SPY", "QQQ", "IWM", "DIA"}


def run_screener(progress_callback=None):
    universe = get_universe()
    total = len(universe)

    raw_df = load_bulk_data(universe)
    df = add_indicators(raw_df)

    results = []

    if df.empty:
        return []

    for i, symbol in enumerate(universe):

        if progress_callback:
            progress_callback(symbol, i, total)

        if symbol not in df["symbol"].unique():
            continue

        data = df[df["symbol"] == symbol].copy()

        if is_etf(symbol):
            continue

        if data["volume"].isna().all():
            continue
        if data["close"].isna().all():
            continue

        data = data.dropna(subset=["volume", "close", "open", "high", "low"])
        if len(data) < 50:
            continue

        data = data.sort_values("datetime")
        last = data.iloc[-1]
        prev = data.iloc[-2]

        if pd.isna(last["volume"]):
            continue

        close = float(last["close"])
        volume = int(last["volume"])

        if not (5 < close < 250):
            continue
        if volume < 500000:
            continue

        body = abs(last["close"] - last["open"]) / last["open"]
        rng = (last["high"] - last["low"]) / last["low"]
        if body > 0.02 or rng > 0.03:
            continue

        data["tr"] = data["high"] - data["low"]
        data["atr14"] = data["tr"].rolling(14).mean()
        atr = data["atr14"].iloc[-1]
        if pd.isna(atr) or (atr / close) < 0.015:
            continue

        last["atr14"] = atr

        ema9_prev, ema21_prev = prev["ema9"], prev["ema21"]
        ema9_now, ema21_now = last["ema9"], last["ema21"]

        if any(pd.isna(x) for x in (ema9_now, ema21_now)):
            continue

        fresh_cross = (
            ema9_prev < ema21_prev and
            ema9_now > ema21_now and
            (ema9_now - ema21_now) / ema21_now > 0.0005
        )
        if not fresh_cross:
            continue

        sma20_now, sma20_prev = last["sma20"], prev["sma20"]
        if any(pd.isna(x) for x in (sma20_now, sma20_prev)):
            continue
        if sma20_now <= sma20_prev or close <= sma20_now:
            continue

        vwap_now = last["vwap"]
        if pd.isna(vwap_now):
            continue
        above_vwap = (close - vwap_now) / vwap_now > 0.002

        bb_upper = last["bb_upper"]
        if pd.isna(bb_upper):
            continue
        not_overbought = close < bb_upper * 0.985

        avg_vol_20 = last["avg_vol_20"]
        if pd.isna(avg_vol_20):
            continue
        high_volume = volume > avg_vol_20 * 1.4

        confluence = sum([above_vwap, not_overbought, high_volume])
        if confluence < 2:
            continue

        score = score_signal(last, prev)
        explanation = explain_signal(last, prev)

        results.append({
            "symbol": symbol,
            "price": close,
            "volume": volume,
            "confluence": int(confluence),
            "atr": float(atr),
            "score": int(score),
            "explanation": explanation,
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)


# ============================================================
# 6. UI CARD RENDERER
# ============================================================

def render_results(results):
    st.subheader("SwingBot Signals")

    for r in results:
        symbol = r["symbol"]
        price = r["price"]
        score = r["score"]
        atr = r["atr"]
        vol = r["volume"]
        conf = r["confluence"]

        with st.container(border=True):
            cols = st.columns([2, 2, 2, 2])
            cols[0].markdown(f"**{symbol}**")
            cols[1].markdown(f"**Score:** {score}")
            cols[2].markdown(f"**Price:** ${price:,.2f}")
            cols[3].markdown(f"**ATR:** {atr:,.2f}")

            st.caption(
                f"Volume: {vol:,} | Confluence: {conf} "
                f"(VWAP / Bollinger / Volume)"
            )

            if "explanation" in r and r["explanation"]:
                st.markdown("**Why this stock was selected:**")
                for reason in r["explanation"]:
                    st.markdown(f"- {reason}")
