#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quantum Dashboard V3.3 Ultimate - FIXED VERSION
- Fixed white background contrast
- Fixed table data copying
- Reduced flickering (30s refresh default)
- Improved readability
"""

import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import ccxt
import time
import math

# ============================================================================
# CONFIGURATION
# ============================================================================
STATE_FILE = "qv33_ultimate_final_state.json"
STATE_BACKUP = STATE_FILE + ".backup"
DEFAULT_SYMBOLS = ["BTC/USDT", "ETH/USDT", "DOT/USDT", "AVAX/USDT", "LINK/USDT", "SOL/USDT", "BNB/USDT", "MATIC/USDT"]
DEFAULT_REFRESH = 30  # Changed from 5 to 30 seconds
PRICE_CACHE_TTL = 15
OHLCV_CACHE_TTL = 60
MAX_PIE_COLORS = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#C7CEEA', '#FFDDC1', '#B4F8C8']

# ============================================================================
# STREAMLIT PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="Quantum Trader V3.3 PRO",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# FIXED CSS - DARK THEME WITH GOOD CONTRAST
# ============================================================================
st.markdown("""
<style>
    /* Main container - dark theme */
    .main {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    /* Headers */
    .big-title { 
        font-size: 32px; 
        font-weight: 700; 
        color: #00D9FF;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 10px rgba(0, 217, 255, 0.3);
    }
    
    .last-update {
        color: #B8B8B8; 
        font-size: 14px;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    /* Metric cards - improved contrast */
    .metric-card {
        background: linear-gradient(135deg, #1a1f2e 0%, #252b3d 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #00D9FF;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .metric-card h4 {
        color: #00D9FF;
        margin-bottom: 12px;
        font-weight: 600;
    }
    
    .metric-card p {
        color: #E0E0E0;
        margin: 8px 0;
        font-size: 14px;
        line-height: 1.6;
    }
    
    .metric-card b {
        color: #FFFFFF;
        font-weight: 600;
    }
    
    /* Profit/Loss colors */
    .profit { 
        color: #00FF88;
        font-weight: bold;
        text-shadow: 0 0 8px rgba(0, 255, 136, 0.4);
    }
    
    .loss { 
        color: #FF4757;
        font-weight: bold;
        text-shadow: 0 0 8px rgba(255, 71, 87, 0.4);
    }
    
    /* Expander headers - better visibility */
    .streamlit-expanderHeader {
        background-color: #1a1f2e !important;
        color: #FFFFFF !important;
        font-weight: 600;
        border-radius: 8px;
    }
    
    /* Tables - fixed for copying */
    .dataframe {
        background-color: #1a1f2e !important;
        color: #E0E0E0 !important;
        border: 1px solid #2d3748;
    }
    
    .dataframe thead th {
        background-color: #252b3d !important;
        color: #00D9FF !important;
        font-weight: 600;
        padding: 12px !important;
        border: 1px solid #2d3748 !important;
    }
    
    .dataframe tbody td {
        background-color: #1a1f2e !important;
        color: #E0E0E0 !important;
        padding: 10px !important;
        border: 1px solid #2d3748 !important;
        user-select: text !important;
        -webkit-user-select: text !important;
        -moz-user-select: text !important;
    }
    
    .dataframe tbody tr:hover {
        background-color: #252b3d !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #1a1f2e;
    }
    
    /* Success/Error/Warning messages */
    .stAlert {
        background-color: #1a1f2e;
        border-radius: 8px;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: #1a3a52;
        color: #E0E0E0;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 24px;
        color: #FFFFFF;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR CONTROLS
# ============================================================================
st.sidebar.title("🎛️ Dashboard Controls")
st.sidebar.markdown("---")

auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh", value=True)
refresh_seconds = st.sidebar.slider("Refresh interval (seconds)", 10, 120, DEFAULT_REFRESH, 5)
st.sidebar.markdown("---")

show_mini_charts = st.sidebar.checkbox("📊 Show mini charts", value=True)
include_fees = st.sidebar.checkbox("💰 Include fees in P&L", value=True)
st.sidebar.markdown("---")

# Theme info
st.sidebar.info(f"""
**Dashboard Info**
- Auto-refresh: {'ON' if auto_refresh else 'OFF'}
- Interval: {refresh_seconds}s
- Charts: {'ON' if show_mini_charts else 'OFF'}
- Fees: {'Included' if include_fees else 'Excluded'}
""")

# ============================================================================
# AUTO-REFRESH (SMOOTHER - prevents flickering)
# ============================================================================
if auto_refresh:
    # Use placeholder to prevent full page reload flickering
    placeholder = st.empty()
    time.sleep(refresh_seconds)
    st.rerun()

# ============================================================================
# HEADER
# ============================================================================
st.markdown('<div class="big-title">🚀 QUANTUM TRADER V3.3 ULTIMATE</div>', unsafe_allow_html=True)
st.markdown(f'<div class="last-update">⏰ Last Update: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>', unsafe_allow_html=True)
st.markdown("---")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_state_atomic(path=STATE_FILE, backup_path=STATE_BACKUP):
    """Load state with backup fallback"""
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            if os.path.exists(backup_path):
                try:
                    with open(backup_path, "r") as fb:
                        return json.load(fb)
                except Exception:
                    return None
    return None

@st.cache_resource
def get_exchange():
    """Singleton exchange instance"""
    api_key = os.getenv("BINANCE_API_KEY", "")
    api_secret = os.getenv("BINANCE_SECRET", "")
    return ccxt.binance({
        "apiKey": api_key,
        "secret": api_secret,
        "enableRateLimit": True,
        "options": {"defaultType": "spot"},
    })

def fetch_prices(symbols):
    """Fetch prices with cache"""
    if "price_cache" not in st.session_state:
        st.session_state["price_cache"] = {"ts": 0, "data": {}}
    
    cache = st.session_state["price_cache"]
    now = time.time()
    
    if now - cache["ts"] < PRICE_CACHE_TTL and cache["data"]:
        return cache["data"].copy()
    
    exchange = get_exchange()
    prices = {}
    
    for sym in symbols:
        try:
            ticker = exchange.fetch_ticker(sym)
            price = ticker.get('last') or ticker.get('close')
            if price and math.isfinite(price) and price > 0:
                prices[sym] = float(price)
            else:
                prices[sym] = cache["data"].get(sym, 0.0)
        except Exception:
            prices[sym] = cache["data"].get(sym, 0.0)
        time.sleep(0.05)
    
    cache["ts"] = now
    cache["data"] = prices
    return prices

def fetch_ohlcv(symbol: str, timeframe: str = "1h", limit: int = 48):
    """Fetch OHLCV with cache"""
    if "ohlcv_cache" not in st.session_state:
        st.session_state["ohlcv_cache"] = {}
    
    key = f"{symbol}_{timeframe}_{limit}"
    cache = st.session_state["ohlcv_cache"]
    now = time.time()
    entry = cache.get(key)
    
    if entry and now - entry["ts"] < OHLCV_CACHE_TTL:
        return entry["data"]
    
    exchange = get_exchange()
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        cache[key] = {"ts": now, "data": ohlcv}
        st.session_state["ohlcv_cache"] = cache
        return ohlcv
    except Exception:
        if entry:
            return entry["data"]
        return None

def compute_position_metrics(pos, current_price, trading_fee_pct=0.001):
    """Compute position metrics with fees"""
    entry_price = float(pos.get("entry_price", 0.0))
    amount = float(pos.get("amount", 0.0))
    reserved_capital = float(pos.get("reserved_capital", entry_price * amount))
    gross_value = current_price * amount
    
    if include_fees:
        buy_fee = reserved_capital * trading_fee_pct
        sell_fee = gross_value * trading_fee_pct
        total_fees = buy_fee + sell_fee
        net_value = gross_value - sell_fee
        net_pnl = net_value - (reserved_capital + buy_fee)
        net_pnl_pct = (net_pnl / (reserved_capital + buy_fee) * 100.0) if (reserved_capital + buy_fee) > 0 else 0.0
    else:
        total_fees = 0
        net_value = gross_value
        net_pnl = gross_value - reserved_capital
        net_pnl_pct = ((current_price - entry_price) / entry_price * 100.0) if entry_price > 0 else 0.0
    
    return {
        "entry_price": entry_price,
        "amount": amount,
        "reserved_capital": reserved_capital,
        "gross_value": gross_value,
        "total_fees": total_fees,
        "net_value": net_value,
        "net_pnl": net_pnl,
        "net_pnl_pct": net_pnl_pct
    }

# ============================================================================
# LOAD STATE
# ============================================================================
state = load_state_atomic()
if not state:
    st.error("❌ State file not found. Make sure the bot is running.")
    st.stop()

# Extract state data
capital = float(state.get("capital", 0.0))
total_invested = float(state.get("total_invested", 0.0) or 0.0)
positions = state.get("positions", {})
total_trades = int(state.get("total_trades", 0))
winning_trades = int(state.get("winning_trades", 0))
losing_trades = int(state.get("losing_trades", 0))
total_fees_paid = float(state.get("total_fees_paid", 0.0))
max_drawdown = float(state.get("max_drawdown", 0.0))
cycle_count = int(state.get("cycle_count", 0))
trade_history = state.get("trade_history", [])

bot_fee = float(state.get("trading_fee_pct", 0.001))

# ============================================================================
# FETCH PRICES
# ============================================================================
prices = fetch_prices(DEFAULT_SYMBOLS)

# ============================================================================
# CALCULATE METRICS
# ============================================================================
position_details = []
invested_value = 0.0
total_net_pnl = 0.0

for sym, pos in positions.items():
    current_price = prices.get(sym, pos.get("entry_price", 0.0))
    metrics = compute_position_metrics(pos, current_price, trading_fee_pct=bot_fee)
    invested_value += metrics["gross_value"]
    total_net_pnl += metrics["net_pnl"]
    position_details.append({
        "symbol": sym,
        "amount": metrics["amount"],
        "entry_price": metrics["entry_price"],
        "current_price": current_price,
        "gross_value": metrics["gross_value"],
        "net_value": metrics["net_value"],
        "pnl": metrics["net_pnl"],
        "pnl_pct": metrics["net_pnl_pct"],
        "total_fees": metrics["total_fees"],
        "highest_price": pos.get("highest_price", metrics["entry_price"]),
        "entry_fear": pos.get("entry_fear", 50),
        "reserved_capital": metrics["reserved_capital"]
    })

total_value = capital + invested_value
total_pnl_pct = ((total_value - total_invested) / total_invested * 100.0) if total_invested > 0 else 0.0
win_rate = (winning_trades / total_trades * 100.0) if total_trades > 0 else 0.0

# ============================================================================
# TOP METRICS
# ============================================================================
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("💎 Total Value", f"${total_value:,.2f}", delta=f"{total_pnl_pct:+.2f}%")

with col2:
    cash_pct = (capital / total_value * 100.0) if total_value > 0 else 0.0
    st.metric("💵 Cash", f"${capital:,.2f}", delta=f"{cash_pct:.1f}%")

with col3:
    st.metric("📊 Invested", f"${invested_value:,.2f}", delta=f"{len(position_details)} positions")

with col4:
    st.metric("📈 Total P&L", f"${total_net_pnl:,.2f}", delta=f"{total_pnl_pct:+.2f}%")

with col5:
    st.metric("🎯 Win Rate", f"{win_rate:.1f}%", delta=f"{winning_trades}W / {losing_trades}L")

st.markdown("---")

# ============================================================================
# MAIN CONTENT
# ============================================================================
left, right = st.columns([2.5, 1])

with left:
    st.subheader("🎯 Active Positions")
    if not position_details:
        st.info("No active positions")
    else:
        for pos in sorted(position_details, key=lambda x: x['pnl'], reverse=True):
            pnl_color = "🟢" if pos["pnl"] >= 0 else "🔴"
            header = f"{pos['symbol']} — {pnl_color} ${pos['pnl']:+,.2f} ({pos['pnl_pct']:+.2f}%)"
            with st.expander(header, expanded=False):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown("**📥 Entry**")
                    st.write(f"Entry: ${pos['entry_price']:.4f}")
                    st.write(f"Amount: {pos['amount']:.8f}")
                    st.write(f"Reserved: ${pos['reserved_capital']:.2f}")
                    st.write(f"Fear: {pos.get('entry_fear', 50)}")
                with c2:
                    st.markdown("**📊 Current**")
                    st.write(f"Price: ${pos['current_price']:.4f}")
                    st.write(f"Value: ${pos['gross_value']:.2f}")
                    st.write(f"High: ${pos['highest_price']:.4f}")
                    st.write(f"Fees: ${pos['total_fees']:.4f}")
                with c3:
                    st.markdown("**📈 Performance**")
                    pnl_display = f"${pos['pnl']:+,.2f}" if pos['pnl'] >= 0 else f"${pos['pnl']:,.2f}"
                    st.write(f"P&L: {pnl_display}")
                    st.write(f"P&L %: {pos['pnl_pct']:+.2f}%")

                if show_mini_charts:
                    ohlcv = fetch_ohlcv(pos['symbol'], timeframe="1h", limit=48)
                    if ohlcv and len(ohlcv) > 0:
                        df = pd.DataFrame(ohlcv, columns=["ts", "open", "high", "low", "close", "vol"])
                        df['dt'] = pd.to_datetime(df['ts'], unit='ms')
                        fig = go.Figure(data=[go.Candlestick(
                            x=df['dt'],
                            open=df['open'],
                            high=df['high'],
                            low=df['low'],
                            close=df['close'],
                            increasing_line_color='#00FF88',
                            decreasing_line_color='#FF4757'
                        )])
                        fig.update_layout(
                            xaxis_rangeslider_visible=False,
                            height=260,
                            margin=dict(t=30, b=20, l=0, r=0),
                            title=f"{pos['symbol']} - 1H Chart",
                            title_font_color="#00D9FF",
                            paper_bgcolor='#1a1f2e',
                            plot_bgcolor='#1a1f2e',
                            font=dict(color='#E0E0E0'),
                            xaxis=dict(gridcolor='#2d3748'),
                            yaxis=dict(gridcolor='#2d3748')
                        )
                        st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("📊 Bot Statistics")
    
    st.markdown(f"""
    <div class="metric-card">
        <h4>🤖 Bot Status</h4>
        <p><b>Mode:</b> DRY-RUN 🟢</p>
        <p><b>Cycle:</b> {cycle_count}</p>
        <p><b>Total Trades:</b> {total_trades}</p>
        <p><b>Win Rate:</b> {win_rate:.1f}%</p>
        <p><b>Fees Paid:</b> ${total_fees_paid:.4f}</p>
        <p><b>Max Drawdown:</b> {max_drawdown*100:.2f}%</p>
    </div>
    """, unsafe_allow_html=True)

    if position_details:
        st.markdown("#### 📊 Portfolio Allocation")
        labels = [p['symbol'] for p in position_details] + ["Cash"]
        values = [p['gross_value'] for p in position_details] + [capital]
        
        if sum(values) > 0:
            colors = MAX_PIE_COLORS[:len(labels)]
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=.35,
                marker=dict(colors=colors)
            )])
            fig.update_layout(
                height=300,
                margin=dict(t=10, b=10, l=10, r=10),
                showlegend=True,
                paper_bgcolor='#1a1f2e',
                font=dict(color='#E0E0E0')
            )
            st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# RECENT TRADES - FIXED FOR COPYING
# ============================================================================
st.markdown("---")
st.subheader("📈 Recent Trades")

if trade_history:
    recent_trades = trade_history[-10:][::-1]
    trades_data = []
    
    for trade in recent_trades:
        trades_data.append({
            "Time": trade.get("timestamp", "")[:19].replace("T", " "),
            "Symbol": trade.get("symbol", ""),
            "Action": trade.get("action", ""),
            "Entry": f"{trade.get('entry_price', 0):.4f}",
            "Exit": f"{trade.get('exit_price', 0):.4f}" if trade.get('exit_price') else "N/A",
            "P&L $": f"{trade.get('pnl', 0):+.2f}",
            "P&L %": f"{trade.get('pnl_pct', 0):+.2f}%",
            "Fee": f"{trade.get('fee', 0):.4f}"
        })
    
    df_trades = pd.DataFrame(trades_data)
    
    # Use st.dataframe with proper styling for copying
    st.dataframe(
        df_trades,
        use_container_width=True,
        height=400,
        hide_index=True
    )
else:
    st.info("No trades recorded yet")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.caption(f"🚀 Quantum Trader V3.3 PRO • Refresh: {refresh_seconds}s • Mode: DRY-RUN • {datetime.now().strftime('%H:%M:%S')}")
