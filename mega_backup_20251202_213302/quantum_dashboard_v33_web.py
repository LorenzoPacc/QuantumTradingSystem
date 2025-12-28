#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QUANTUM TRADER V3.3 - WEB DASHBOARD
Dashboard web professionale con Streamlit
"""

import streamlit as st
import json
import os
from datetime import datetime
import time
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page config
st.set_page_config(
    page_title="Quantum Trader V3.3 Ultimate",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .profit {
        color: #28a745;
        font-weight: bold;
    }
    .loss {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Functions
@st.cache_data(ttl=5)
def load_state():
    """Load bot state"""
    state_file = "qv33_ultimate_final_state.json"
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading state: {e}")
            return None
    return None

def get_current_prices():
    """Get current prices (mock for now, will integrate with CCXT)"""
    import ccxt
    try:
        exchange = ccxt.binance()
        prices = {}
        symbols = ["BTC/USDT", "ETH/USDT", "DOT/USDT", "AVAX/USDT", "LINK/USDT", "SOL/USDT"]
        for symbol in symbols:
            ticker = exchange.fetch_ticker(symbol)
            prices[symbol] = ticker['last']
        return prices
    except:
        return {}

def calculate_position_value(position, current_price):
    """Calculate current position value"""
    amount = position.get('amount', 0)
    return amount * current_price

def format_pnl(pnl, pnl_pct):
    """Format P&L with color"""
    if pnl >= 0:
        return f'<span class="profit">+${pnl:.2f} (+{pnl_pct:.2f}%)</span>'
    else:
        return f'<span class="loss">${pnl:.2f} ({pnl_pct:.2f}%)</span>'

# Header
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown('<p class="big-font">🚀 QUANTUM TRADER V3.3 ULTIMATE</p>', unsafe_allow_html=True)

st.markdown("---")

# Load data
state = load_state()
current_prices = get_current_prices()

if state is None:
    st.error("⚠️ State file not found! Make sure the bot is running.")
    st.stop()

# Calculate metrics
capital = state.get('capital', 0)
positions = state.get('positions', {})
total_invested = state.get('total_invested', 200)
total_trades = state.get('total_trades', 0)
winning_trades = state.get('winning_trades', 0)
losing_trades = state.get('losing_trades', 0)
total_fees = state.get('total_fees_paid', 0)
max_drawdown = state.get('max_drawdown', 0)
cycle_count = state.get('cycle_count', 0)

# Calculate portfolio value
invested_value = 0
total_pnl = 0
position_details = []

for symbol, pos in positions.items():
    entry_price = pos.get('entry_price', 0)
    amount = pos.get('amount', 0)
    reserved_capital = pos.get('reserved_capital', entry_price * amount)
    
    current_price = current_prices.get(symbol, entry_price)
    current_value = amount * current_price
    invested_value += current_value
    
    pnl = current_value - reserved_capital
    pnl_pct = ((current_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
    total_pnl += pnl
    
    position_details.append({
        'symbol': symbol,
        'amount': amount,
        'entry_price': entry_price,
        'current_price': current_price,
        'current_value': current_value,
        'reserved_capital': reserved_capital,
        'pnl': pnl,
        'pnl_pct': pnl_pct,
        'highest_price': pos.get('highest_price', entry_price),
        'entry_fear': pos.get('entry_fear', 50)
    })

total_value = capital + invested_value
total_pnl_pct = ((total_value - total_invested) / total_invested * 100) if total_invested > 0 else 0
win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

# Main metrics
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="💎 Total Value",
        value=f"${total_value:.2f}",
        delta=f"{total_pnl_pct:+.2f}%"
    )

with col2:
    st.metric(
        label="💵 Cash",
        value=f"${capital:.2f}",
        delta=f"{(capital/total_value*100):.1f}%"
    )

with col3:
    st.metric(
        label="📊 Invested",
        value=f"${invested_value:.2f}",
        delta=f"{len(positions)} positions"
    )

with col4:
    st.metric(
        label="📈 Total P&L",
        value=f"${total_pnl:.2f}",
        delta=f"{total_pnl_pct:+.2f}%"
    )

with col5:
    st.metric(
        label="🎯 Win Rate",
        value=f"{win_rate:.1f}%",
        delta=f"{winning_trades}W / {losing_trades}L"
    )

st.markdown("---")

# Two columns layout
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🎯 Active Positions")
    
    if not positions:
        st.info("No active positions")
    else:
        for pos in position_details:
            with st.expander(f"{pos['symbol']} - {pos['pnl_pct']:+.2f}%", expanded=True):
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    st.markdown("**Entry Info**")
                    st.write(f"Entry: ${pos['entry_price']:.2f}")
                    st.write(f"Amount: {pos['amount']:.8f}")
                    st.write(f"Invested: ${pos['reserved_capital']:.2f}")
                
                with col_b:
                    st.markdown("**Current Status**")
                    st.write(f"Price: ${pos['current_price']:.2f}")
                    st.write(f"Value: ${pos['current_value']:.2f}")
                    st.write(f"High: ${pos['highest_price']:.2f}")
                
                with col_c:
                    st.markdown("**Performance**")
                    pnl_color = "🟢" if pos['pnl'] >= 0 else "🔴"
                    st.write(f"{pnl_color} P&L: ${pos['pnl']:.2f}")
                    st.write(f"P&L %: {pos['pnl_pct']:+.2f}%")
                    st.write(f"Fear: {pos['entry_fear']}")
                
                # Progress bar for P&L
                progress_val = min(max(pos['pnl_pct'] / 10, -1), 1)
                st.progress((progress_val + 1) / 2)

with col_right:
    st.subheader("📊 Bot Statistics")
    
    # Stats box
    st.markdown(f"""
    <div class="metric-card">
        <h4>🤖 Bot Status</h4>
        <p>🟢 <b>ACTIVE</b> (DRY-RUN)</p>
        <p>🔄 Cycle: <b>{cycle_count}</b></p>
        <p>⏱️ Running since startup</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="metric-card">
        <h4>💰 Performance</h4>
        <p>💸 Total Fees: <b>${total_fees:.4f}</b></p>
        <p>📉 Max Drawdown: <b>{max_drawdown*100:.2f}%</b></p>
        <p>📊 Trades: <b>{total_trades}</b></p>
        <p>✅ Win Rate: <b>{win_rate:.1f}%</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Portfolio allocation pie chart
    if positions:
        fig = go.Figure(data=[go.Pie(
            labels=[p['symbol'] for p in position_details] + ['Cash'],
            values=[p['current_value'] for p in position_details] + [capital],
            hole=.3
        )])
        fig.update_layout(
            title="Portfolio Allocation",
            height=300,
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Recent trades
st.subheader("📈 Recent Trades")
trade_history = state.get('trade_history', [])

if trade_history:
    recent_trades = trade_history[-10:][::-1]  # Last 10, reversed
    
    trades_data = []
    for trade in recent_trades:
        trades_data.append({
            'Time': trade.get('timestamp', 'N/A')[:19],
            'Symbol': trade.get('symbol', 'N/A'),
            'Action': trade.get('action', 'N/A'),
            'Entry': f"${trade.get('entry_price', 0):.2f}",
            'Exit': f"${trade.get('exit_price', 0):.2f}",
            'P&L': f"${trade.get('pnl', 0):.2f}",
            'P&L %': f"{trade.get('pnl_pct', 0):+.2f}%",
            'Fee': f"${trade.get('fee', 0):.4f}"
        })
    
    df_trades = pd.DataFrame(trades_data)
    st.dataframe(df_trades, use_container_width=True)
else:
    st.info("No trades yet")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("🔄 **Auto-refresh**: 5 seconds")
with col2:
    st.markdown(f"⏰ **Last Update**: {datetime.now().strftime('%H:%M:%S')}")
with col3:
    st.markdown("🛡️ **Mode**: DRY-RUN")

# Auto-refresh
time.sleep(5)
st.rerun()
