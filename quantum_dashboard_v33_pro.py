#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quantum Dashboard V3.3 Ultimate PRO - FIXED
Versione semplificata e funzionante
"""

import streamlit as st
import json
import os
import logging
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import ccxt
import time
import math

# ---------------------------
# CONFIGURATION
# ---------------------------
STATE_FILE = "qv33_ultimate_final_state.json"
STATE_BACKUP = STATE_FILE + ".backup"
DEFAULT_SYMBOLS = ["BTC/USDT", "ETH/USDT", "DOT/USDT", "AVAX/USDT", "LINK/USDT", "SOL/USDT", "BNB/USDT", "MATIC/USDT"]
REFRESH_SECONDS = 30
PRICE_CACHE_TTL = 15
OHLCV_CACHE_TTL = 60
MAX_PIE_COLORS = ['#FF9999', '#66B2FF', '#99FF99', '#FFD700', '#FFA07A', '#C9A0DC', '#8DD3C7', '#B3DE69']

# ---------------------------
# STREAMLIT PAGE
# ---------------------------
st.set_page_config(
    page_title="Quantum Trader V3.3 PRO",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .big-title { 
        font-size: 28px; 
        font-weight: 700; 
        color: #0b5564; 
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .last-update {
        color: #6c757d; 
        font-size: 14px;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
    }
    .profit { color: #28a745; font-weight: bold; }
    .loss { color: #dc3545; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# SIDEBAR CONTROLS
# ---------------------------
st.sidebar.title("🎛️ Dashboard Controls")
auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh", value=True)
refresh_seconds = st.sidebar.slider("Refresh seconds", 5, 300, 30, 5)
show_mini_charts = st.sidebar.checkbox("📊 Show mini charts", value=True)
include_fees = st.sidebar.checkbox("💰 Include fees in P&L", value=True)

# ---------------------------
# AUTO-REFRESH SEMPLICE E FUNZIONANTE
# ---------------------------
if auto_refresh:
    time.sleep(refresh_seconds)
    st.rerun()

# ---------------------------
# HEADER
# ---------------------------
st.markdown('<div class="big-title">🚀 Quantum Trader V3.3 — Dashboard PRO</div>', unsafe_allow_html=True)
st.markdown(f'<div class="last-update">Last update: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>', unsafe_allow_html=True)
st.markdown("---")

# ---------------------------
# FUNZIONI HELPER
# ---------------------------
def load_state_atomic(path=STATE_FILE, backup_path=STATE_BACKUP):
    """Load state with backup fallback"""
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            if os.path.exists(backup_path):
                try:
                    with open(backup_path, "r") as fb:
                        return json.load(fb)
                except Exception:
                    return None
    return None

def get_exchange():
    """Singleton exchange instance"""
    if "exchange_instance" not in st.session_state:
        api_key = os.getenv("BINANCE_API_KEY", "")
        api_secret = os.getenv("BINANCE_SECRET", "")
        exchange = ccxt.binance({
            "apiKey": api_key,
            "secret": api_secret,
            "enableRateLimit": True,
            "options": {"defaultType": "spot"},
        })
        st.session_state["exchange_instance"] = exchange
    return st.session_state["exchange_instance"]

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
    except Exception as e:
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

# ---------------------------
# LOAD STATE DATA
# ---------------------------
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
fear_greed_history = state.get("fear_greed_history", [])

bot_fee = float(state.get("trading_fee_pct", 0.001))

# ---------------------------
# FETCH CURRENT PRICES
# ---------------------------
prices = fetch_prices(DEFAULT_SYMBOLS)

# ---------------------------
# CALCULATE PORTFOLIO METRICS
# ---------------------------
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
total_pnl_pct = ((total_value - total_invested) / total_invested * 100.0) if total_invested and total_invested > 0 else 0.0
win_rate = (winning_trades / total_trades * 100.0) if total_trades > 0 else 0.0

# ---------------------------
# TOP METRICS
# ---------------------------
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("💎 Total Value", f"${total_value:,.2f}", delta=f"{total_pnl_pct:+.2f}%")

with col2:
    cash_pct = (capital / total_value * 100.0) if total_value > 0 else 0.0
    st.metric("💵 Cash", f"${capital:,.2f}", delta=f"{cash_pct:.1f}%")

with col3:
    st.metric("📊 Invested", f"${invested_value:,.2f}", delta=f"{len(position_details)} positions")

with col4:
    st.metric("📈 Net P&L", f"${total_net_pnl:,.2f}", delta=f"{total_pnl_pct:+.2f}%")

with col5:
    st.metric("🎯 Win Rate", f"{win_rate:.1f}%", delta=f"{winning_trades}W / {losing_trades}L")

st.markdown("---")

# ---------------------------
# MAIN CONTENT - TWO COLUMNS
# ---------------------------
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
                    st.write(f"Gross Value: ${pos['gross_value']:.2f}")
                    st.write(f"Net Value: ${pos['net_value']:.2f}")
                    st.write(f"Fees: ${pos['total_fees']:.4f}")
                with c3:
                    st.markdown("**📈 Performance**")
                    st.write(f"P&L: ${pos['pnl']:+,.2f}")
                    st.write(f"P&L %: {pos['pnl_pct']:+.2f}%")
                    st.write(f"High: ${pos['highest_price']:.4f}")

                # Mini OHLCV chart
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
                            increasing_line_color='#2ca02c', 
                            decreasing_line_color='#d62728'
                        )])
                        fig.update_layout(
                            xaxis_rangeslider_visible=False, 
                            height=260, 
                            margin=dict(t=10, b=20, l=0, r=0),
                            title=f"{pos['symbol']} - 1H Chart"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Chart data not available")

with right:
    st.subheader("📊 Bot Statistics")
    
    # Status Card
    st.markdown(f"""
    <div class="metric-card">
        <h4>🤖 Bot Status</h4>
        <p><b>Mode:</b> DRY-RUN</p>
        <p><b>Cycle:</b> {cycle_count}</p>
        <p><b>Total Trades:</b> {total_trades}</p>
        <p><b>Win Rate:</b> {win_rate:.1f}%</p>
        <p><b>Fees Paid:</b> ${total_fees_paid:.4f}</p>
        <p><b>Max Drawdown:</b> {max_drawdown*100:.2f}%</p>
    </div>
    """, unsafe_allow_html=True)

    # Portfolio Allocation Pie Chart
    if position_details:
        st.markdown("#### 📊 Portfolio Allocation")
        labels = [p['symbol'] for p in position_details] + ["Cash"]
        values = [p['gross_value'] for p in position_details] + [capital]
        
        if sum(values) > 0:
            colors = (MAX_PIE_COLORS * ((len(labels) // len(MAX_PIE_COLORS)) + 1))[:len(labels)]
            fig = go.Figure(data=[go.Pie(
                labels=labels, 
                values=values, 
                hole=.35, 
                marker=dict(colors=colors)
            )])
            fig.update_layout(
                height=300, 
                margin=dict(t=10, b=10, l=10, r=10),
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# RECENT TRADES TABLE
# ---------------------------
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
            "Entry": f"${trade.get('entry_price', 0):.4f}",
            "Exit": f"${trade.get('exit_price', 0):.4f}" if trade.get('exit_price') else "N/A",
            "P&L $": f"${trade.get('pnl', 0):+,.2f}",
            "P&L %": f"{trade.get('pnl_pct', 0):+.2f}%",
            "Fee": f"${trade.get('fee', 0):.4f}"
        })
    
    df_trades = pd.DataFrame(trades_data)
    st.dataframe(df_trades, use_container_width=True, height=400)
else:
    st.info("No trades recorded yet")

# ---------------------------
# ALERTS SECTION
# ---------------------------
st.markdown("---")
st.subheader("⚠️ Alerts & Notifications")

alerts = []

# Check for alerts
if capital < 20:
    alerts.append(("❌", f"Low capital: ${capital:.2f}"))

if max_drawdown > 0.10:
    alerts.append(("⚠️", f"High drawdown: {max_drawdown*100:.1f}%"))

if len(position_details) >= 4:
    alerts.append(("ℹ️", f"Many positions: {len(position_details)}/5"))

if fear_greed_history:
    last_fear = fear_greed_history[-1].get("value", 50)
    if last_fear < 25:
        alerts.append(("📉", f"Extreme Fear: {last_fear}"))
    elif last_fear > 75:
        alerts.append(("📈", f"Extreme Greed: {last_fear}"))

# Display alerts
if alerts:
    for icon, message in alerts:
        st.write(f"{icon} {message}")
else:
    st.success("✅ No critical alerts")

# ---------------------------
# FOOTER
# ---------------------------
st.markdown("---")
st.markdown("""
**📝 Dashboard Info**
- **Auto-refresh**: Every {} seconds
- **Data source**: Binance API + Bot state file
- **Fees**: {} in P&L calculations
- **Charts**: {} mini OHLCV charts
""".format(
    refresh_seconds, 
    "Included" if include_fees else "Excluded",
    "Enabled" if show_mini_charts else "Disabled"
))

st.caption(f"Quantum Trader V3.3 PRO Dashboard • Last refresh: {datetime.now().strftime('%H:%M:%S')}")
