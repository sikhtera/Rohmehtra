"""
NSE Swing Trading Scanner — Sahil Rohmetra Strategy
Streamlit App — Deploy free on Streamlit Cloud
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import time

st.set_page_config(
    page_title="NSE Swing Scanner | Sahil Rohmetra Strategy",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Dark theme custom CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0d1117; }
[data-testid="stSidebar"] { background: #161b22; border-right: 1px solid #21262d; }
[data-testid="stHeader"] { background: #0d1117; }
.block-container { padding-top: 1.5rem; }

.metric-card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.strong-card { border-left: 3px solid #3fb950; }
.buy-card    { border-left: 3px solid #58a6ff; }
.watch-card  { border-left: 3px solid #d29922; }

.sym  { font-size: 1.2rem; font-weight: 800; color: #e6edf3; font-family: monospace; }
.price{ font-size: 1.5rem; font-weight: 700; color: #e6edf3; font-family: monospace; }
.pos  { color: #3fb950; }
.neg  { color: #f85149; }

.badge {
    display: inline-block;
    font-size: 0.62rem;
    font-weight: 700;
    padding: 2px 9px;
    border-radius: 100px;
    letter-spacing: 0.07em;
    margin-right: 4px;
    font-family: monospace;
}
.b-strong { background: rgba(63,185,80,0.15);  color: #3fb950; border: 1px solid rgba(63,185,80,0.3); }
.b-buy    { background: rgba(88,166,255,0.15); color: #58a6ff; border: 1px solid rgba(88,166,255,0.3); }
.b-watch  { background: rgba(210,153,34,0.15); color: #d29922; border: 1px solid rgba(210,153,34,0.3); }
.b-fno    { background: rgba(88,166,255,0.08); color: #58a6ff; border: 1px solid rgba(88,166,255,0.18); }
.b-mid    { background: rgba(163,113,247,0.08);color: #a371f7; border: 1px solid rgba(163,113,247,0.18); }
.b-sm     { background: rgba(219,109,40,0.08); color: #db6d28; border: 1px solid rgba(219,109,40,0.18); }

.met-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: #21262d;
    border-top: 1px solid #21262d;
    border-bottom: 1px solid #21262d;
    margin: 8px -18px;
}
.met-cell {
    background: #161b22;
    padding: 6px 10px;
}
.met-lbl { font-size: 0.58rem; color: #484f58; letter-spacing: 0.06em; font-family: monospace; }
.met-val { font-size: 0.82rem; font-weight: 700; font-family: monospace; }
.v-g { color: #3fb950; }
.v-b { color: #58a6ff; }
.v-r { color: #f85149; }
.v-d { color: #d29922; }
.v-p { color: #a371f7; }

.trade-row {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 12px;
    padding: 8px 0 4px;
}
.trade-item {}
.trade-lbl { font-size: 0.58rem; color: #484f58; letter-spacing: 0.06em; font-family: monospace; }
.trade-val { font-size: 0.85rem; font-weight: 700; font-family: monospace; }
.rr-pill {
    display: inline-block;
    font-size: 0.62rem; font-weight: 700;
    padding: 1px 7px; border-radius: 100px;
    background: rgba(210,153,34,0.15); color: #d29922;
    border: 1px solid rgba(210,153,34,0.3);
    font-family: monospace; margin-top: 3px;
}
.cond-item {
    font-size: 0.72rem; color: #8b949e;
    padding: 3px 0;
    border-bottom: 1px solid #21262d;
    font-family: monospace;
}
.cond-fail { color: #484f58; }
.score-bar {
    display: flex; gap: 3px; align-items: center;
    padding: 6px 0;
}
.sdot {
    flex: 1; height: 3px; border-radius: 100px;
    background: #21262d;
}
.sdot.f-s { background: #3fb950; }
.sdot.f-b { background: #58a6ff; }
.sdot.f-w { background: #d29922; }

.stat-box {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 10px 16px;
    text-align: center;
}
.stat-lbl { font-size: 0.62rem; color: #484f58; letter-spacing: 0.08em; font-family: monospace; }
.stat-val { font-size: 1.6rem; font-weight: 800; font-family: monospace; }

.strat-pill {
    display: inline-block;
    font-size: 0.65rem;
    background: #161b22;
    border: 1px solid #21262d;
    color: #8b949e;
    padding: 3px 10px;
    border-radius: 100px;
    margin: 2px;
    font-family: monospace;
}
.strat-pill span { color: #3fb950; margin-right: 4px; }
</style>
""", unsafe_allow_html=True)

# ── Stock Universe ─────────────────────────────────────────────────────────────
FNO_STOCKS = [
    "RELIANCE","TCS","HDFCBANK","INFY","ICICIBANK","KOTAKBANK","HINDUNILVR",
    "AXISBANK","SBIN","BAJFINANCE","BHARTIARTL","MARUTI","ITC","ASIANPAINT",
    "WIPRO","HCLTECH","ULTRACEMCO","TITAN","NESTLEIND","POWERGRID","NTPC",
    "SUNPHARMA","ONGC","TATAMOTORS","TATASTEEL","JSWSTEEL","ADANIENT",
    "ADANIPORTS","COALINDIA","BPCL","GRASIM","HEROMOTOCO","DIVISLAB",
    "DRREDDY","CIPLA","APOLLOHOSP","TECHM","LTIM","INDUSINDBK","BAJAJFINSV",
    "SHRIRAMFIN","SBILIFE","HDFCLIFE","PIDILITIND","BERGEPAINT","HAVELLS",
    "DABUR","MARICO","BALKRISIND","BANDHANBNK","FEDERALBNK","PNB","CANBK",
    "TATACONSUM","BRITANNIA","GODREJCP","COLPAL","AUROPHARMA","TORNTPHARM",
    "LUPIN","ALKEM","VOLTAS","POLYCAB","SIEMENS","CUMMINSIND","BHEL",
    "ZOMATO","DMART","TRENT","VEDL","HINDALCO","NMDC","SAIL","DLF",
    "GODREJPROP","OBEROIRLTY","AMBUJACEM","ACC"
]

MIDCAP_STOCKS = [
    "PERSISTENT","COFORGE","MPHASIS","LTTS","KPITTECH","TATAELXSI",
    "ZYDUSLIFE","IPCALAB","NATCOPHARM","GRANULES","IRCTC","RVNL","IRFC",
    "HUDCO","RECLTD","PFC","NHPC","SJVN","TATAPOWER","SUZLON",
    "KAJARIACER","AIAENG","TIMKEN","RELAXO","METROPOLIS","LALPATHLAB",
    "ASHOKLEY","ESCORTS","TIINDIA","MOTHERSON","APOLLOTYRE","MRF","CEAT",
    "RATNAMANI","BLUESTAR","SYMPHONY","IIFL","MUTHOOTFIN","CHOLAFIN",
    "MANAPPURAM","SUNTV","CANFINHOME","APTUS","AAVAS","HOMEFIRST"
]

SMALLCAP_STOCKS = [
    "KAYNES","CDSL","CAMS","RAILTEL","NBCC","BEML","NELCO",
    "DATAPATTNS","TANLA","NUCLEUS","NEWGEN","MASTEK","EQUITAS",
    "SURYODAY","UJJIVAN","RAMKRISHNA","GPIL","HGINFRA","NCC","PNCINFRA",
    "KNR","ORIENTCEM","JKLAKSHMI","IGARASHI","KFINTECH","MSTCLTD",
    "INFIBEAM","NAZARA","CAPACITE","TIMETECHNO"
]

# ── Indicator Functions ────────────────────────────────────────────────────────
def ema(s, p): return s.ewm(span=p, adjust=False).mean()

def rsi(s, p=14):
    d = s.diff()
    g = d.clip(lower=0).ewm(com=p-1, min_periods=p).mean()
    l = (-d.clip(upper=0)).ewm(com=p-1, min_periods=p).mean()
    return 100 - (100 / (1 + g/l))

def macd(s):
    m = ema(s,12) - ema(s,26)
    sig = ema(m,9)
    return m, sig, m-sig

def atr(h, l, c, p=14):
    tr = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(com=p-1, min_periods=p).mean()

def bollinger(s, p=20):
    sma = s.rolling(p).mean()
    std = s.rolling(p).std()
    return sma + 2*std, sma, sma - 2*std

# ── Scanner Logic ──────────────────────────────────────────────────────────────
def analyze(ticker_ns, category):
    try:
        df = yf.download(ticker_ns, period="6mo", interval="1d",
                         progress=False, auto_adjust=True)
        if df is None or len(df) < 60:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        c = df['Close'].squeeze()
        h = df['High'].squeeze()
        l = df['Low'].squeeze()
        v = df['Volume'].squeeze()

        e20, e50, e200 = ema(c,20), ema(c,50), ema(c,200)
        r = rsi(c)
        ml, sl, hist = macd(c)
        at = atr(h, l, c)
        bb_up, _, _ = bollinger(c)
        vol20 = v.rolling(20).mean()

        ltp    = float(c.iloc[-1])
        E20    = float(e20.iloc[-1])
        E50    = float(e50.iloc[-1])
        E200   = float(e200.iloc[-1])
        RSI    = float(r.iloc[-1])
        MACD_H = float(hist.iloc[-1])
        MACD_H_prev = float(hist.iloc[-2])
        MACD_L = float(ml.iloc[-1])
        MACD_S = float(sl.iloc[-1])
        ATR    = float(at.iloc[-1])
        VOL    = float(v.iloc[-1])
        VOL20  = float(vol20.iloc[-1])
        BB_UP  = float(bb_up.iloc[-1])
        SW_LOW = float(l.tail(15).min())
        SW_HIGH= float(h.tail(30).max())
        W52_H  = float(h.tail(252).max())
        W52_L  = float(l.tail(252).min())

        chg1d = float((c.iloc[-1]-c.iloc[-2])/c.iloc[-2]*100)
        chg1w = float((c.iloc[-1]-c.iloc[-6])/c.iloc[-6]*100) if len(c)>=7 else 0
        chg1m = float((c.iloc[-1]-c.iloc[-22])/c.iloc[-22]*100) if len(c)>=23 else 0

        vol_ratio = VOL / VOL20 if VOL20 > 0 else 0
        ema20_dist = abs(ltp - E20) / E20 * 100

        c1 = E20 > E50 > E200
        c2 = ltp > E50
        c3 = ema20_dist <= 3.0
        c4 = 40 <= RSI <= 65
        c5 = MACD_H > MACD_H_prev
        c6 = vol_ratio >= 1.2
        c7 = abs(ltp - BB_UP) / BB_UP * 100 > 1.0

        score = sum([c1,c2,c3,c4,c5,c6,c7])
        if score < 4: return None

        sl_price = max(SW_LOW * 0.995, E20 * 0.985)
        entry    = ltp
        risk     = entry - sl_price
        tgt1     = SW_HIGH
        tgt2     = entry + risk * 2.5
        rr       = (tgt1 - entry) / risk if risk > 0 else 0

        if rr < 1.2: return None

        if score == 7:   signal, sig_cls = "STRONG BUY", "strong"
        elif score >= 5: signal, sig_cls = "BUY", "buy"
        else:            signal, sig_cls = "WATCH", "watch"

        conditions = [
            (c1, f"EMA Stack Bullish (20>50>200) — Primary uptrend confirmed"),
            (c2, f"Price above 50 EMA — Uptrend territory"),
            (c3, f"Price within {ema20_dist:.1f}% of 20 EMA — Pullback zone"),
            (c4, f"RSI {RSI:.1f} — Optimal momentum zone (40–65)"),
            (c5, f"MACD histogram turning up — Momentum pickup"),
            (c6, f"Volume {vol_ratio:.1f}x above average — Strong participation"),
            (c7, f"Not overbought — Room to run above BB midline"),
        ]

        return dict(
            symbol=ticker_ns.replace(".NS",""), category=category,
            signal=signal, sig_cls=sig_cls, score=score,
            ltp=round(ltp,2), chg1d=round(chg1d,2),
            chg1w=round(chg1w,2), chg1m=round(chg1m,2),
            w52h=round(W52_H,2), w52l=round(W52_L,2),
            from52h=round((W52_H-ltp)/W52_H*100,1),
            E20=round(E20,2), E50=round(E50,2), E200=round(E200,2),
            RSI=round(RSI,1), MACD_H=round(MACD_H,3),
            ATR=round(ATR,2), ATR_pct=round(ATR/ltp*100,2),
            vol_ratio=round(vol_ratio,2),
            BB_UP=round(BB_UP,2),
            entry=round(entry,2), sl=round(sl_price,2),
            tgt1=round(tgt1,2), tgt2=round(tgt2,2),
            rr=round(rr,2),
            risk_pct=round((entry-sl_price)/entry*100,2),
            upside_pct=round((tgt1-entry)/entry*100,2),
            conditions=conditions, conditions_met=score
        )
    except:
        return None

# ── Render Card ────────────────────────────────────────────────────────────────
def render_card(s):
    sig_cls = s['sig_cls']
    card_cls = f"{sig_cls}-card"

    sig_badge = {"strong":"b-strong","buy":"b-buy","watch":"b-watch"}[sig_cls]
    sig_label = s['signal']
    cat_cls = {"FNO":"b-fno","MIDCAP":"b-mid","SMALLCAP":"b-sm"}[s['category']]

    chg_cls  = "pos" if s['chg1d'] >= 0 else "neg"
    chg_sign = "+" if s['chg1d'] >= 0 else ""

    dots = ""
    dot_cls = f"f-{sig_cls[0]}"
    for i in range(7):
        filled = "f-s" if sig_cls=="strong" and i<s['score'] else \
                 "f-b" if sig_cls=="buy" and i<s['score'] else \
                 "f-w" if sig_cls=="watch" and i<s['score'] else ""
        dots += f'<div class="sdot {filled}"></div>'

    macd_cls = "v-g" if s['MACD_H'] > 0 else "v-r"
    rsi_cls  = "v-d" if s['RSI'] > 60 else "v-b" if s['RSI'] < 45 else "v-g"
    vol_cls  = "v-g" if s['vol_ratio'] >= 1.5 else "v-b" if s['vol_ratio'] >= 1.2 else "v-r"
    from52_cls = "v-g" if s['from52h'] < 10 else "v-d"

    conds_html = ""
    for passed, text in s['conditions']:
        icon = "✅" if passed else "⚠️"
        cls  = "cond-item" if passed else "cond-item cond-fail"
        conds_html += f'<div class="{cls}">{icon} {text}</div>'

    html = f"""
    <div class="metric-card {card_cls}">
      <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <div>
          <div class="sym">{s['symbol']}</div>
          <div class="price">₹{s['ltp']:,.2f} <span class="{chg_cls}" style="font-size:0.9rem">{chg_sign}{s['chg1d']}%</span></div>
        </div>
        <div>
          <span class="badge {sig_badge}">{sig_label}</span>
          <span class="badge {cat_cls}">{s['category']}</span>
        </div>
      </div>

      <div style="display:flex;align-items:center;gap:8px;padding:6px 0 4px">
        <span style="font-size:0.58rem;color:#484f58;font-family:monospace">STRENGTH</span>
        <div class="score-bar" style="flex:1;padding:0">{dots}</div>
        <span style="font-size:0.65rem;color:#8b949e;font-family:monospace">{s['score']}/7</span>
      </div>

      <div class="met-row">
        <div class="met-cell"><div class="met-lbl">RSI(14)</div><div class="met-val {rsi_cls}">{s['RSI']}</div></div>
        <div class="met-cell"><div class="met-lbl">EMA20</div><div class="met-val v-b">₹{s['E20']:,.0f}</div></div>
        <div class="met-cell"><div class="met-lbl">VOL RATIO</div><div class="met-val {vol_cls}">{s['vol_ratio']}x</div></div>
        <div class="met-cell"><div class="met-lbl">ATR%</div><div class="met-val">{s['ATR_pct']}%</div></div>
        <div class="met-cell"><div class="met-lbl">MACD HIST</div><div class="met-val {macd_cls}">{s['MACD_H']}</div></div>
        <div class="met-cell"><div class="met-lbl">52W HIGH</div><div class="met-val">₹{s['w52h']:,.0f}</div></div>
        <div class="met-cell"><div class="met-lbl">FROM 52W H</div><div class="met-val {from52_cls}">{s['from52h']}%</div></div>
        <div class="met-cell"><div class="met-lbl">EMA50</div><div class="met-val v-b">₹{s['E50']:,.0f}</div></div>
      </div>

      <div class="trade-row">
        <div class="trade-item">
          <div class="trade-lbl">ENTRY</div>
          <div class="trade-val v-b">₹{s['entry']:,.2f}</div>
          <div style="font-size:0.58rem;color:#484f58;font-family:monospace">CMP</div>
        </div>
        <div class="trade-item">
          <div class="trade-lbl">STOP LOSS</div>
          <div class="trade-val v-r">₹{s['sl']:,.2f}</div>
          <div style="font-size:0.58rem;color:#f85149;font-family:monospace">-{s['risk_pct']}%</div>
        </div>
        <div class="trade-item">
          <div class="trade-lbl">TARGET 1</div>
          <div class="trade-val v-g">₹{s['tgt1']:,.2f}</div>
          <div class="rr-pill">R:R {s['rr']}:1</div>
        </div>
      </div>

      <details style="margin-top:6px">
        <summary style="font-size:0.68rem;color:#484f58;cursor:pointer;font-family:monospace;padding:4px 0">
          📋 ENTRY CONDITIONS ({s['conditions_met']}/7 met)
        </summary>
        <div style="padding-top:4px">{conds_html}</div>
        <div style="font-size:0.65rem;color:#484f58;font-family:monospace;padding-top:6px">
          1W: <span class="{'pos' if s['chg1w']>=0 else 'neg'}">{'+' if s['chg1w']>=0 else ''}{s['chg1w']}%</span> &nbsp;|&nbsp;
          1M: <span class="{'pos' if s['chg1m']>=0 else 'neg'}">{'+' if s['chg1m']>=0 else ''}{s['chg1m']}%</span> &nbsp;|&nbsp;
          EMA200: <span style="color:#58a6ff">₹{s['E200']:,.0f}</span> &nbsp;|&nbsp;
          Target2: <span style="color:#3fb950">₹{s['tgt2']:,.0f}</span>
        </div>
      </details>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📈 NSE Swing Scanner")
    st.markdown("**Sahil Rohmetra Strategy**")
    st.markdown("---")

    st.markdown("#### 📂 Select Universe")
    scan_fno      = st.checkbox("F&O Stocks", value=True)
    scan_midcap   = st.checkbox("Midcap Stocks", value=True)
    scan_smallcap = st.checkbox("Smallcap Stocks", value=False)

    st.markdown("---")
    st.markdown("#### 🔎 Filters")
    sig_filter = st.selectbox("Signal", ["All", "STRONG BUY", "BUY", "WATCH"])
    cat_filter = st.selectbox("Category", ["All", "FNO", "MIDCAP", "SMALLCAP"])
    min_rr     = st.slider("Min R:R Ratio", 1.0, 4.0, 1.2, 0.1)
    min_score  = st.slider("Min Score (out of 7)", 4, 7, 4)

    st.markdown("---")
    scan_btn = st.button("🔍 SCAN NOW", use_container_width=True, type="primary")

    st.markdown("---")
    st.markdown("""
    **Strategy Rules (Sahil Rohmetra)**
    - EMA 20 > 50 > 200 Stack
    - RSI 40–65 zone
    - Pullback to 20 EMA ≤3%
    - MACD histogram turning up
    - Volume ≥ 1.2× avg
    - Min R:R 1.2:1
    """)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.62rem;color:#484f58;font-family:monospace;line-height:1.6">
    ⚠️ Educational use only.<br>
    NOT financial advice.<br>
    Data: Yahoo Finance (may be delayed).<br>
    Always verify before trading.
    </div>
    """, unsafe_allow_html=True)

# ── Main ───────────────────────────────────────────────────────────────────────
st.markdown("## 📈 NSE Swing Scanner — Sahil Rohmetra Strategy")

st.markdown("""
<div style="margin-bottom:16px">
<span class="strat-pill"><span>▲</span>EMA 20>50>200 Stack</span>
<span class="strat-pill"><span>▲</span>RSI 40–65 Zone</span>
<span class="strat-pill"><span>▲</span>Pullback to 20 EMA</span>
<span class="strat-pill"><span>▲</span>MACD Histogram Up</span>
<span class="strat-pill"><span>▲</span>Volume ≥ 1.2× Avg</span>
<span class="strat-pill"><span>▲</span>Min R:R 1.2:1</span>
</div>
""", unsafe_allow_html=True)

# ── Run Scan ───────────────────────────────────────────────────────────────────
if scan_btn:
    stocks = []
    if scan_fno:      stocks += [(s+".NS","FNO")      for s in FNO_STOCKS]
    if scan_midcap:   stocks += [(s+".NS","MIDCAP")   for s in MIDCAP_STOCKS]
    if scan_smallcap: stocks += [(s+".NS","SMALLCAP") for s in SMALLCAP_STOCKS]

    if not stocks:
        st.warning("Please select at least one universe.")
    else:
        results = []
        progress = st.progress(0, text="Starting scan...")
        status   = st.empty()

        for i, (ticker, cat) in enumerate(stocks):
            pct = (i+1) / len(stocks)
            progress.progress(pct, text=f"Scanning {ticker.replace('.NS','')} ({i+1}/{len(stocks)})...")
            res = analyze(ticker, cat)
            if res:
                results.append(res)
            time.sleep(0.05)

        progress.empty()
        results.sort(key=lambda x: (x['score'], x['rr']), reverse=True)
        st.session_state['results'] = results
        st.session_state['scan_time'] = datetime.now().strftime("%d %b %Y, %I:%M %p")
        status.success(f"✅ Scan complete! Found {len(results)} setups from {len(stocks)} stocks scanned.")

# ── Display Results ────────────────────────────────────────────────────────────
if 'results' in st.session_state and st.session_state['results']:
    results = st.session_state['results']

    # Apply filters
    filtered = results
    if sig_filter != "All":
        filtered = [r for r in filtered if r['signal'] == sig_filter]
    if cat_filter != "All":
        filtered = [r for r in filtered if r['category'] == cat_filter]
    filtered = [r for r in filtered if r['rr'] >= min_rr and r['score'] >= min_score]

    # Stats row
    strong = sum(1 for r in filtered if r['signal'] == "STRONG BUY")
    buy    = sum(1 for r in filtered if r['signal'] == "BUY")
    watch  = sum(1 for r in filtered if r['signal'] == "WATCH")
    best_rr= max((r['rr'] for r in filtered), default=0)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f'<div class="stat-box"><div class="stat-lbl">STRONG BUY</div><div class="stat-val" style="color:#3fb950">{strong}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><div class="stat-lbl">BUY</div><div class="stat-val" style="color:#58a6ff">{buy}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-box"><div class="stat-lbl">WATCH</div><div class="stat-val" style="color:#d29922">{watch}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-box"><div class="stat-lbl">BEST R:R</div><div class="stat-val" style="color:#3fb950">{best_rr:.1f}:1</div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="stat-box"><div class="stat-lbl">SHOWING</div><div class="stat-val" style="color:#a371f7">{len(filtered)}</div></div>', unsafe_allow_html=True)

    st.markdown(f"<div style='font-size:0.65rem;color:#484f58;font-family:monospace;margin:8px 0 16px'>Last scanned: {st.session_state.get('scan_time','—')}</div>", unsafe_allow_html=True)

    if not filtered:
        st.info("No stocks match the current filters. Try relaxing the criteria.")
    else:
        # 2-column grid
        cols = st.columns(2)
        for i, stock in enumerate(filtered):
            with cols[i % 2]:
                render_card(stock)

elif not scan_btn:
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;color:#484f58">
        <div style="font-size:3rem;margin-bottom:1rem">📡</div>
        <div style="font-size:1.1rem;font-weight:700;color:#8b949e;margin-bottom:0.5rem">Ready to Scan</div>
        <div style="font-size:0.8rem;font-family:monospace">
            Select categories in the sidebar and click <strong style="color:#3fb950">SCAN NOW</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)
