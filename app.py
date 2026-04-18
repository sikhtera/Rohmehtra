import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# Page Layout
st.set_page_config(page_title="Rohmetra Swing Scanner", layout="wide")

st.title("🏹 Sahil Rohmetra Swing System")
st.subheader("Automated Mechanical Trend Following")

# Define Stock Lists
universes = {
    "NSE FnO": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "INFY.NS", "BHARTIARTL.NS", "ITC.NS", "TATAMOTORS.NS", "AXISBANK.NS"],
    "Midcap 100": ["MAZDOCK.NS", "RVNL.NS", "IRFC.NS", "PFC.NS", "RECLTD.NS", "POLYCAB.NS", "KEI.NS", "BEL.NS", "HAL.NS", "TRENT.NS"],
    "Smallcap 100": ["KAYNES.NS", "DATA-PATTERNS.NS", "SJVN.NS", "HUDCO.NS", "JWL.NS", "UJJIVANSFB.NS", "MAPMYINDIA.NS", "NBCC.NS"]
}

selected_universe = st.sidebar.selectbox("Choose Segment", list(universes.keys()))

def get_data_and_scan(symbol):
    try:
        # Get data
        df = yf.download(symbol, period="1y", interval="1d", progress=False)
        if len(df) < 50: return None
        
        # 1. Supertrend (10, 3) - The Trend Bias
        # Using pandas_ta: returns columns ['SUPERT_10_3.0', 'SUPERTd_10_3.0', ...]
        st_df = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
        df['ST_Dir'] = st_df['SUPERTd_10_3.0']
        df['ST_Value'] = st_df['SUPERT_10_3.0']
        
        # 2. ADX (14) - The Strength
        adx_df = ta.adx(df['High'], df['Low'], df['Close'], length=14)
        df['ADX'] = adx_df['ADX_14']
        
        # 3. Moving Averages - The Structure
        df['SMA20'] = ta.sma(df['Close'], length=20)
        df['SMA50'] = ta.sma(df['Close'], length=50)
        
        last = df.iloc[-1]
        
        # --- ENTRY CONDITIONS ---
        # Condition 1: Supertrend is Green (Bullish Bias)
        c1 = last['ST_Dir'] == 1
        # Condition 2: ADX > 25 (High Strength Momentum)
        c2 = last['ADX'] > 25
        # Condition 3: Bullish Alignment (SMA20 > SMA50)
        c3 = last['SMA20'] > last['SMA50']
        # Condition 4: Current Price is above 20 SMA (Active Momentum)
        c4 = last['Close'] > last['SMA20']

        if c1 and c2 and c3 and c4:
            # Check for 52-Week High Breakout
            year_high = df['Close'].rolling(252).max().iloc[-1]
            is_ath = last['Close'] >= year_high
            
            return {
                "Ticker": symbol,
                "LTP": round(last['Close'], 2),
                "ADX": round(last['ADX'], 2),
                "Type": "🔥 Breakout" if is_ath else "📈 Trend Ride",
                "Entry Condition": "Price > SMA20 + ADX Strength",
                "StopLoss": round(last['ST_Value'], 2),
                "Risk/Reward": "1:2 Target Recommended"
            }
    except Exception as e:
        return None

if st.button("🚀 Start Scanning Market"):
    results = []
    stocks = universes[selected_universe]
    
    progress_bar = st.progress(0)
    for i, s in enumerate(stocks):
        res = get_data_and_scan(s)
        if res:
            results.append(res)
        progress_bar.progress((i + 1) / len(stocks))
        
    if results:
        res_df = pd.DataFrame(results)
        st.success(f"Found {len(results)} Best Bets!")
        
        # Formatting the Table
        st.table(res_df)
        
        st.info("**Trading Instructions:**\n"
                "1. Wait for price to cross previous day's High for entry.\n"
                "2. Exit immediately if Supertrend turns Red on Daily Close.\n"
                "3. Trail Stoploss along the Supertrend line.")
    else:
        st.warning("No stocks currently match the Sahil Rohmetra criteria.")
