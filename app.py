import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.title("🚀 Pro Stock Scanner (Trend + Entry Signals)")

stocks = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS",
    "ICICIBANK.NS", "ITC.NS", "LT.NS", "SBIN.NS",
    "NTPC.NS", "POWERGRID.NS", "CGPOWER.NS",
    "PIDILITIND.NS", "VBL.NS"
]

results = []

st.write("Scanning market...")

for stock in stocks:
    try:
        data = yf.download(stock, period="6mo", interval="1d")

        if data.empty:
            continue

        # Indicators
        data["EMA20"] = ta.trend.ema_indicator(data["Close"], window=20)
        data["EMA50"] = ta.trend.ema_indicator(data["Close"], window=50)
        data["EMA200"] = ta.trend.ema_indicator(data["Close"], window=200)
        data["RSI"] = ta.momentum.rsi(data["Close"], window=14)

        latest = data.iloc[-1]
        prev = data.iloc[-2]

        trend = "❌"
        signal = "REJECT"

        # 🔹 Trend Check
        if latest["Close"] > latest["EMA50"] > latest["EMA200"]:
            trend = "UPTREND"

            # 🔹 Pullback Setup
            if latest["Close"] < latest["EMA20"] * 1.03:
                signal = "WATCH (Pullback)"

                # 🔹 Entry Confirmation (Bullish candle)
                if latest["Close"] > prev["High"]:
                    signal = "BUY (Pullback Confirmed)"

            # 🔹 Breakout Setup
            recent_high = data["High"].rolling(20).max().iloc[-2]
            if latest["Close"] > recent_high:
                signal = "BUY (Breakout)"

        results.append({
            "Stock": stock,
            "Price": round(latest["Close"], 2),
            "Trend": trend,
            "Signal": signal,
            "RSI": round(latest["RSI"], 2)
        })

    except:
        continue

df = pd.DataFrame(results)

# Show only good setups
filtered = df[df["Signal"] != "REJECT"]

if not filtered.empty:
    st.success(f"Found {len(filtered)} opportunities")
    st.dataframe(filtered)
else:
    st.warning("No good setups today")
