#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quantum Dashboard V3.3 - SIMPLE WORKING VERSION
Versione semplificata che funziona sicuramente
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
DEFAULT_SYMBOLS = ["BTC/USDT", "ETH/USDT", "DOT/USDT", "AVAX/USDT", "LINK/USDT", "SOL/USDT"]
DEFAULT_REFRESH = 30

# ============================================================================
# STREAMLIT PAGE CONFIG - FORZA TEMA CHIARO
# ============================================================================
st.set_page_config(
    page_title="Quantum Trader V3.3",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS SEMPLICE CHE FUNZIONA
# ============================================================================
st.markdown("""
<style>
    /* Solo le correzioni essenziali */
    .main {
        background-color: white !important;
    }
    
    .big-title { 
        font-size: 32px; 
        font-weight: 700; 
        color: #1f77b4;
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
    
    .dataframe tbody td {
        user-select: text !important;
        -webkit-user-select: text !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================
st.sidebar.title("🎛️ Controls")
auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)
refresh_seconds = st.sidebar.slider("Refresh (seconds)", 10, 120, 30)

# ============================================================================
# AUTO-REFRESH
# ============================================================================
if auto_refresh:
    time.sleep(refresh_seconds)
    st.rerun()

# ============================================================================
# HEADER - VISIBILE
# ============================================================================
st.markdown('<div class="big-title">🚀 QUANTUM TRADER V3.3</div>', unsafe_allow_html=True)
st.markdown(f"**Last Update:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown("---")

# ============================================================================
# FUNZIONI BASE
# ============================================================================
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except:
            return None
    return None

@st.cache_resource
def get_exchange():
    return ccxt.binance({"enableRateLimit": True})

def fetch_prices(symbols):
    exchange = get_exchange()
    prices = {}
    for sym in symbols:
        try:
            ticker = exchange.fetch_ticker(sym)
            prices[sym] = ticker.get('last', 0)
        except:
            prices[sym] = 0
    return prices

# ============================================================================
# CARICA DATI
# ============================================================================
state = load_state()
if not state:
    st.error("❌ State file not found. Make sure the bot is running.")
    st.stop()

# Dati base
capital = float(state.get("capital", 0))
positions = state.get("positions", {})
total_trades = state.get("total_trades", 0)
winning_trades = state.get("winning_trades", 0)
losing_trades = state.get("losing_trades", 0)
cycle_count = state.get("cycle_count", 0)
trade_history = state.get("trade_history", [])

# ============================================================================
# CALCOLA METRICHE
# ============================================================================
prices = fetch_prices(DEFAULT_SYMBOLS)
invested_value = 0
position_details = []

for sym, pos in positions.items():
    current_price = prices.get(sym, pos.get("entry_price", 0))
    amount = pos.get("amount", 0)
    entry_price = pos.get("entry_price", 0)
    value = current_price * amount
    invested_value += value
    
    pnl = value - (entry_price * amount)
    pnl_pct = ((current_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
    
    position_details.append({
        "symbol": sym,
        "current_price": current_price,
        "value": value,
        "pnl": pnl,
        "pnl_pct": pnl_pct
    })

total_value = capital + invested_value
win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

# ============================================================================
# METRICHE PRINCIPALI - VISIBILI
# ============================================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💎 Total Value", f"${total_value:,.2f}")

with col2:
    st.metric("💵 Cash", f"${capital:,.2f}")

with col3:
    st.metric("📊 Invested", f"${invested_value:,.2f}")

with col4:
    st.metric("🎯 Win Rate", f"{win_rate:.1f}%")

st.markdown("---")

# ============================================================================
# POSIZIONI
# ============================================================================
st.subheader("🎯 Active Positions")

if not position_details:
    st.info("No active positions")
else:
    for pos in position_details:
        with st.expander(f"{pos['symbol']} - {pos['pnl_pct']:+.2f}%"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Price:** ${pos['current_price']:.4f}")
                st.write(f"**Value:** ${pos['value']:.2f}")
            with col2:
                color = "green" if pos['pnl'] >= 0 else "red"
                st.write(f"**P&L:** ${pos['pnl']:+,.2f}")
                st.write(f"**P&L %:** {pos['pnl_pct']:+.2f}%")

# ============================================================================
# STATISTICHE BOT
# ============================================================================
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Bot Stats")
st.sidebar.write(f"**Cycle:** {cycle_count}")
st.sidebar.write(f"**Trades:** {total_trades}")
st.sidebar.write(f"**W/L:** {winning_trades}/{losing_trades}")

# ============================================================================
# TRADES RECENTI - COPIABILI
# ============================================================================
st.markdown("---")
st.subheader("📈 Recent Trades")

if trade_history:
    recent = trade_history[-10:][::-1]
    data = []
    for trade in recent:
        data.append({
            "Time": trade.get("timestamp", "")[:19],
            "Symbol": trade.get("symbol", ""),
            "Action": trade.get("action", ""),
            "P&L": f"${trade.get('pnl', 0):+.2f}"
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No trades yet")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.caption(f"Quantum Trader V3.3 • Auto-refresh: {refresh_seconds}s")
