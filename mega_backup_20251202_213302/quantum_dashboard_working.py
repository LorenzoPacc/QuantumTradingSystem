#!/usr/bin/env python3
import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import time

# Configurazione BASE
st.set_page_config(page_title="Quantum Trader", layout="wide")

# NESSUN CSS - usa solo Streamlit nativo
st.title("🚀 QUANTUM TRADER V3.3")
st.write(f"**Last Update:** {datetime.now().strftime('%H:%M:%S')}")
st.markdown("---")

# Controlli sidebar
with st.sidebar:
    st.header("🎛️ Controls")
    auto_refresh = st.checkbox("Auto-refresh", True)
    refresh_time = st.slider("Seconds", 10, 60, 30)

# Funzione caricamento stato
def load_state():
    try:
        with open("qv33_ultimate_final_state.json", "r") as f:
            return json.load(f)
    except:
        return None

# Carica dati
state = load_state()
if not state:
    st.error("❌ Bot non running o state file missing")
    st.stop()

# Calcola metriche BASE
capital = state.get("capital", 0)
positions = state.get("positions", {})
total_trades = state.get("total_trades", 0)
winning_trades = state.get("winning_trades", 0)

# Metriche principali
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("💰 Cash", f"${capital:,.2f}")
with col2:
    st.metric("📊 Positions", len(positions))
with col3:
    st.metric("🎯 Trades", total_trades)
with col4:
    win_rate = (winning_trades/total_trades*100) if total_trades > 0 else 0
    st.metric("📈 Win Rate", f"{win_rate:.1f}%")

st.markdown("---")

# Posizioni attive
st.subheader("🎯 Active Positions")
if positions:
    for symbol, pos in positions.items():
        with st.expander(f"{symbol}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Entry:** ${pos.get('entry_price', 0):.2f}")
                st.write(f"**Amount:** {pos.get('amount', 0):.6f}")
            with col2:
                st.write(f"**Current Value:** ${pos.get('entry_price', 0) * pos.get('amount', 0):.2f}")
else:
    st.info("No active positions")

# Trade history
st.markdown("---")
st.subheader("📈 Recent Trades")
trades = state.get("trade_history", [])[-5:]
if trades:
    for trade in reversed(trades):
        st.write(f"**{trade.get('symbol', '')}** - {trade.get('action', '')} - P&L: ${trade.get('pnl', 0):+.2f}")
else:
    st.info("No trades yet")

# Footer
st.markdown("---")
st.write(f"🔄 Auto-refresh: {refresh_time}s | Cycle: {state.get('cycle_count', 0)}")

# Auto-refresh
if auto_refresh:
    time.sleep(refresh_time)
    st.rerun()
