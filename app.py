import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.title("📊 Trend + Momentum Stock Scanner")

# Sample NSE stocks (you can expand this list)
stocks = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS",
    "ICICIBANK.NS", "ITC.NS", "LT.NS", "SBIN.NS",
    "NTPC.NS", "POWERGRID.NS", "CGPOWER.NS",
    "PIDILITIND.NS", "VBL.NS"
]

results = []

st.write("Scanning stocks...")

for stock in stocks:
    try:
        data = yf.download(stock, period="6mo", interval="1d")

        if data.empty:
            continue

        # Indicators
        data["EMA50"] = ta.trend.ema_indicator(data["Close"], window=50)
        data["EMA200"] = ta.trend.ema_indicator(data["Close"], window=200)
        data["RSI"] = ta.momentum.rsi(data["Close"], window=14)
        data["Volume_MA"] = data["Volume"].rolling(20).mean()

        latest = data.iloc[-1]

        # Scanner Conditions
        if (
            latest["Close"] > latest["EMA50"] and
            latest["Close"] > latest["EMA200"] and
            latest["RSI"] > 55 and
            latest["Volume"] > latest["Volume_MA"]
        ):
            results.append({
                "Stock": stock,
                "Price": round(latest["Close"], 2),
                "RSI": round(latest["RSI"], 2)
            })

    except:
        continue

# Show results
if results:
    df = pd.DataFrame(results)
    st.success(f"Found {len(df)} stocks")
    st.dataframe(df)
else:
    st.warning("No stocks found today")
