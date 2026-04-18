import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime

# Page Config
st.set_page_config(page_title="Sahil Rohmetra Swing Scanner", layout="wide")

st.title("🚀 Sahil Rohmetra Swing Strategy Scanner")
st.sidebar.header("Scan Settings")

# 1. Define Stock Universes (Sample lists - You can expand these)
universes = {
    "NSE FnO": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "INFY.NS", "ITC.NS"],
    "Midcap Best": ["MAZDOCK.NS", "RVNL.NS", "IRFC.NS", "ZOMATO.NS", "PFC.NS", "RECLTD.NS", "POLYCAB.NS"],
    "Smallcap High Momentum": ["KAYNES.NS", "SUZLON.NS", "DATA-PATTERNS.NS", "IRB.NS", "HUDCO.NS"]
}

selected_universe = st.sidebar.selectbox("Select Segment", list(universes.keys()))
adx_threshold = st.sidebar.slider("Min ADX Strength", 20, 40, 25)

def get_signals(symbol):
    try:
        df = yf.download(symbol, period="1y", interval="1d", progress=False)
        if len(df) < 50: return None
        
        # 2. Technical Indicators (Rohmetra Setup)
        df['SMA20'] = ta.sma(df['Close'], length=20)
        df['SMA50'] = ta.sma(df['Close'], length=50)
        adx_df = ta.adx(df['High'], df['Low'], df['Close'], length=14)
        df = pd.concat([df, adx_df], axis=1)
        
        # Supertrend (10, 3)
        st_df = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
        df['ST_Dir'] = st_df['SUPERTd_10_3.0']
        df['ST_Val'] = st_df['SUPERT_10_3.0']
        
        # 3. Strategy Logic
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Condition A: Trend Alignment (Supertrend Green + Price above MAs)
        is_bullish = (last['ST_Dir'] == 1) and (last['Close'] > last['SMA20']) and (last['SMA20'] > last['SMA50'])
        
        # Condition B: Strength (ADX > Threshold)
        is_strong = last['ADX_14'] > adx_threshold
        
        # Condition C: Entry Trigger (Inside bar or Pullback to 20SMA or 52W High Breakout)
        is_52w_high = last['Close'] >= df['Close'].rolling(252).max().iloc[-1]
        is_pullback = last['Low'] <= last['SMA20'] and last['Close'] > last['SMA20']

        if is_bullish and is_strong:
            return {
                "Symbol": symbol,
                "LTP": round(last['Close'], 2),
                "ADX": round(last['ADX_14'], 2),
                "Signal": "🚀 52W Breakout" if is_52w_high else "📉 Pullback Entry",
                "Entry Range": f"{round(last['Low'], 2)} - {round(last['High'], 2)}",
                "Stoploss": round(last['ST_Val'], 2),
                "Target (1:2)": round(last['Close'] + (last['Close'] - last['ST_Val']) * 2, 2)
            }
    except:
        return None

# Execution Button
if st.sidebar.button("Run Scanner"):
    st.write(f"### Scanning {selected_universe} stocks...")
    results = []
    
    progress_bar = st.progress(0)
    stock_list = universes[selected_universe]
    
    for idx, stock in enumerate(stock_list):
        sig = get_signals(stock)
        if sig:
            results.append(sig)
        progress_bar.progress((idx + 1) / len(stock_list))
    
    if results:
        res_df = pd.DataFrame(results)
        st.success(f"Found {len(results)} Best Bets!")
        
        # Displaying Results with Styling
        st.dataframe(res_df.style.highlight_max(axis=0, subset=['ADX'], color='lightgreen'))
        
        # Detail Analysis Section
        st.write("### Detailed Entry Conditions")
        for r in results:
            with st.expander(f"Why trade {r['Symbol']}?"):
                st.write(f"- **Trend:** Supertrend is POSITIVE (Green).")
                st.write(f"- **Momentum:** ADX is at {r['ADX']} (Strong Trend).")
                st.write(f"- **Structure:** Price is above 20 & 50 SMA (Bullish Stack).")
                st.write(f"- **Trigger:** {r['Signal']} identified on Daily chart.")
    else:
        st.error("No stocks currently match the Sahil Rohmetra criteria.")
else:
    st.info("Click 'Run Scanner' in the sidebar to start.")