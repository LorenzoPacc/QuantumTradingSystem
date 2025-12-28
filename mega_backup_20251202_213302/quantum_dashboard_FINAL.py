#!/usr/bin/env python3
import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import time
import ccxt

# --------------------------------------------------
# CONFIGURAZIONE DASHBOARD
# --------------------------------------------------
st.set_page_config(page_title="Quantum Trader", layout="wide")

st.title("🚀 QUANTUM TRADER V3.3 — ULTIMATE EDITION")
st.write(f"⏳ Last update: {datetime.now().strftime('%H:%M:%S')}")
st.markdown("---")

# --------------------------------------------------
# SIDEBAR CONTROLLI
# --------------------------------------------------
with st.sidebar:
    st.header("🎛️ Controls")
    auto_refresh = st.checkbox("Auto-refresh", True)
    refresh_seconds = st.slider("Seconds", 5, 60, 20)

    st.markdown("---")
    st.header("🤖 Bot Info")
    st.write("**Status:** 🟢 Running")
    st.write("**Mode:** LIVE / REAL-PRICE")
    st.write("**Exchange:** Binance")

# --------------------------------------------------
# FUNZIONI OTTIMIZZATE
# --------------------------------------------------
@st.cache_data(ttl=10)
def load_state():
    """Carica lo stato del bot."""
    try:
        with open("qv33_ultimate_final_state.json", "r") as f:
            return json.load(f)
    except Exception:
        return None


@st.cache_data(ttl=5)
def get_current_price(symbol):
    """Ottiene il prezzo reale da Binance."""
    try:
        ex = ccxt.binance()
        ticker = ex.fetch_ticker(symbol)
        return ticker["last"]
    except:
        return None


# --------------------------------------------------
# CARICAMENTO DATI
# --------------------------------------------------
state = load_state()
if not state:
    st.error("❌ Bot not running or state file missing")
    st.stop()

capital = state.get("capital", 0)
positions = state.get("positions", {})
total_trades = state.get("total_trades", 0)
winning_trades = state.get("winning_trades", 0)
cycle_count = state.get("cycle_count", 0)
total_fees = state.get("total_fees_paid", 0)

# --------------------------------------------------
# CALCOLO PORTAFOGLIO
# --------------------------------------------------
portfolio_value = capital
position_details = []

for symbol, pos in positions.items():
    amount = pos.get("amount", 0)
    entry_price = pos.get("entry_price", 0)

    current_price = get_current_price(symbol)
    if current_price is None:
        current_price = entry_price  # fallback

    current_value = amount * current_price
    entry_value = amount * entry_price
    pnl = current_value - entry_value

    portfolio_value += current_value

    position_details.append({
        "symbol": symbol,
        "amount": amount,
        "entry": entry_price,
        "price": current_price,
        "value": current_value,
        "pnl": pnl,
    })

total_pnl = sum(p["pnl"] for p in position_details)

# --------------------------------------------------
# METRICHE
# --------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("💎 Total Value", f"${portfolio_value:,.2f}")

with col2:
    st.metric("💰 Cash", f"${capital:,.2f}")

with col3:
    st.metric("📊 Positions", len(positions))

with col4:
    st.metric("📈 P&L", f"${total_pnl:+,.2f}")

with col5:
    win_rate = (winning_trades / total_trades * 100) if total_trades else 0
    st.metric("🎯 Win Rate", f"{win_rate:.1f}%")

st.markdown("---")

# --------------------------------------------------
# POSIZIONI ATTIVE
# --------------------------------------------------
st.subheader("🎯 Active Positions")

if position_details:
    for p in position_details:
        color = "🟢" if p["pnl"] >= 0 else "🔴"
        with st.expander(f"{p['symbol']} — {color} ${p['pnl']:+,.2f}"):

            st.write(f"**Amount:** {p['amount']}")
            st.write(f"**Entry Price:** ${p['entry']}")
            st.write(f"**Current Price:** ${p['price']}")
            st.write(f"**Value:** ${p['value']:,.2f}")
            st.write(f"**PnL:** {color} ${p['pnl']:+,.2f}")

else:
    st.info("No active positions")

# --------------------------------------------------
# STORICO TRADES
# --------------------------------------------------
st.markdown("---")
st.subheader("📈 Recent Trades")

trades = state.get("trade_history", [])[-10:]

if trades:
    df = pd.DataFrame([
        {
            "Time": t.get("timestamp", "")[:19],
            "Symbol": t.get("symbol", ""),
            "Action": t.get("action", ""),
            "P&L": f"${t.get('pnl', 0):+.2f}",
            "Fee": f"${t.get('fee', 0):.4f}"
        }
        for t in reversed(trades)
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No trades yet")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.write(f"🔄 Auto-refresh: {refresh_seconds}s")

with col2:
    st.write(f"📊 Cycle: {cycle_count}")

with col3:
    st.write(f"💸 Fees: ${total_fees:.4f}")

# --------------------------------------------------
# AUTO REFRESH FIXATO
# --------------------------------------------------
if auto_refresh:
    time.sleep(refresh_seconds)
    st.rerun()
