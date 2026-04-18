import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import time

# --- CONFIGURATION & LISTS ---
# These lists cover the core of NSE FnO, Midcap, and Smallcap momentum stocks
TICKERS = {
    "NSE FnO (Top 50)": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "INFY.NS", "BHARTIARTL.NS", "ITC.NS", "AXISBANK.NS", "KOTAKBANK.NS", "LT.NS", "BAJFINANCE.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS", "ADANIENT.NS", "TATAMOTORS.NS", "HINDALCO.NS", "ONGC.NS", "JSWSTEEL.NS"],
    "Midcap Momentum": ["MAZDOCK.NS", "RVNL.NS", "IRFC.NS", "ZOMATO.NS", "PFC.NS", "RECLTD.NS", "POLYCAB.NS", "KEI.NS", "BEL.NS", "HAL.NS", "OBEROIRLTY.NS", "DIXON.NS", "MAXHEALTH.NS", "MPHASIS.NS", "TRENT.NS"],
    "Smallcap High Growth": ["KAYNES.NS", "DATA-PATTERNS.NS", "IRB.NS", "HUDCO.NS", "MAPMYINDIA.NS", "NBCC.NS", "UJJIVANSFB.NS", "ZENTEC.NS", "JWL.NS", "SJVN.NS"]
}

# --- PAGE SETUP ---
st.set_page_config(page_title="Sahil Rohmetra Pro Scanner", layout="wide")
st.title("📈 Sahil Rohmetra Swing System")
st.markdown("Automated scan for **Trend (Supertrend)** + **Strength (ADX)** + **Momentum (MAs)**")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Scanner Settings")
selected_group = st.sidebar.selectbox("Select Universe", list(TICKERS.keys()))
st.sidebar.divider()
st.sidebar.write("**Strategy Rules:**")
st.sidebar.info("1. Supertrend (10,3) = Green\n2. ADX > 25 (Trending)\n3. SMA 20 > SMA 50\n4. Price > SMA 20")

# --- CORE LOGIC ---
def fetch_and_analyze(symbol):
    try:
        # Fetching 1 year of daily data
        df = yf.download(symbol, period="1y", interval="1d", progress=False)
        if len(df) < 50: return None
        
        # Technicals
        df['SMA20'] = ta.sma(df['Close'], length=20)
        df['SMA50'] = ta.sma(df['Close'], length=50)
        
        # ADX
        adx_df = ta.adx(df['High'], df['Low'], df['Close'], length=14)
        df['ADX'] = adx_df['ADX_14']
        
        # Supertrend
        st_data = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
        df['ST_Dir'] = st_data['SUPERTd_10_3.0']
        df['ST_Val'] = st_data['SUPERT_10_3.0']
        
        last = df.iloc[-1]
        
        # Sahil Rohmetra Conditions
        c1 = last['ST_Dir'] == 1                 # Supertrend Green
        c2 = last['ADX'] > 25                    # Strong Trend
        c3 = last['SMA20'] > last['SMA50']       # Bullish Structure
        c4 = last['Close'] > last['SMA20']       # Price Momentum
        
        if c1 and c2 and c3 and c4:
            # Check for Breakout vs Pullback
            is_breakout = last['Close'] >= df['Close'].rolling(252).max().iloc[-1]
            status = "🔥 52W Breakout" if is_breakout else "💹 Trend Ride"
            
            return {
                "Ticker": symbol,
                "Price": round(last['Close'], 2),
                "ADX": round(last['ADX'], 2),
                "Type": status,
                "Entry": f"Above {round(last['High'], 2)}",
                "StopLoss": round(last['ST_Val'], 2),
                "Target (1:2)": round(last['Close'] + (last['Close'] - last['ST_Val']) * 2, 2)
            }
    except Exception as e:
        return None
    return None

# --- EXECUTION ---
if st.button(f"Scan {selected_group}"):
    stocks_to_scan = TICKERS[selected_group]
    results = []
    
    progress_text = "Scanning market... Please wait."
    my_bar = st.progress(0, text=progress_text)
    
    for i, stock in enumerate(stocks_to_scan):
        res = fetch_and_analyze(stock)
        if res:
            results.append(res)
        my_bar.progress((i + 1) / len(stocks_to_scan))
        time.sleep(0.1) # Prevent rate limiting
        
    my_bar.empty()
    
    if results:
        df_final = pd.DataFrame(results)
        
        # Highlighting the "Best Bets"
        st.subheader(f"✅ Found {len(results)} Best Bets")
        
        # Custom display
        for _, row in df_final.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(row['Ticker'], row['Price'])
                with col2:
                    st.write(f"**Signal:** {row['Type']}")
                    st.write(f"**ADX:** {row['ADX']}")
                with col3:
                    st.write(f"**Entry:** {row['Entry']}")
                    st.error(f"**SL:** {row['StopLoss']}")
                with col4:
                    st.success(f"**Tgt:** {row['Target (1:2)']}")
                st.divider()
    else:
        st.warning("No stocks currently match the Sahil Rohmetra criteria in this segment.")
