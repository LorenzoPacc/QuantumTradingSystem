import streamlit as st
import pandas as pd
import time
from datetime import datetime
import plotly.graph_objects as go
from paper_trading_engine import PaperTradingEngine
from quantum_trader_paper import QuantumTraderPaper

st.set_page_config(
    page_title="QUANTUM PAPER TRADING DASHBOARD",
    page_icon="🚀", 
    layout="wide"
)

# Inizializzazione Paper Trading
@st.cache_resource
def get_paper_trader():
    return QuantumTraderPaper(150)

trader = get_paper_trader()
engine = trader.engine

st.title("🚀 QUANTUM PAPER TRADING - LIVE DASHBOARD")
st.markdown("📊 **PAPER TRADING MODE** - $150 Virtual Balance")
st.markdown("---")

# HEADER PRINCIPALE
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    balance = engine.balance
    st.metric("💰 CASH BALANCE", f"${balance:.2f}")

with col2:
    portfolio_value = engine.get_portfolio_value()
    st.metric("📊 PORTFOLIO VALUE", f"${portfolio_value:.2f}")

with col3:
    total_value = balance + portfolio_value
    st.metric("💎 TOTAL VALUE", f"${total_value:.2f}")

with col4:
    profit, profit_pct = engine.calculate_profit()
    st.metric("📈 TOTAL P&L", f"${profit:.2f}", f"{profit_pct:.2f}%")

with col5:
    st.metric("💸 TOTAL FEES", f"${engine.total_fees:.2f}")

st.markdown("---")

# SEZIONE PREZZI LIVE
st.subheader("📈 LIVE PRICES - BINANCE")

# Prezzi in tempo reale
symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'MATICUSDT', 'AVAXUSDT', 'LINKUSDT']
cols = st.columns(len(symbols))

for i, symbol in enumerate(symbols):
    with cols[i]:
        try:
            price = engine.get_real_price(symbol)
            st.metric(symbol, f"${price:.2f}" if price > 1 else f"${price:.4f}")
        except:
            st.metric(symbol, "N/A")

st.markdown("---")

# SEZIONE PORTFOLIO
st.subheader("🎯 PAPER TRADING PORTFOLIO")

if engine.portfolio:
    portfolio_data = []
    for symbol, holding in engine.portfolio.items():
        current_price = engine.get_real_price(symbol)
        value = holding.quantity * current_price
        buy_price = holding.avg_buy_price
        profit_loss = value - (holding.quantity * buy_price)
        profit_pct = (profit_loss / (holding.quantity * buy_price)) * 100 if buy_price > 0 else 0
        
        portfolio_data.append({
            'Asset': symbol,
            'Quantity': holding.quantity,
            'Avg Buy Price': f"${buy_price:.4f}",
            'Current Price': f"${current_price:.4f}",
            'Value': f"${value:.2f}",
            'P&L': f"${profit_loss:.2f}",
            'P&L %': f"{profit_pct:.2f}%"
        })
    
    df_portfolio = pd.DataFrame(portfolio_data)
    st.dataframe(df_portfolio, use_container_width=True)
else:
    st.info("📭 No assets in portfolio - Ready for trading!")

# SEZIONE ORDINI E STATISTICHE
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📋 ORDER HISTORY")
    if engine.orders_history:
        orders_data = []
        for order in engine.orders_history[-10:]:  # Ultimi 10 ordini
            orders_data.append({
                'Time': order['timestamp'],
                'Symbol': order['symbol'],
                'Side': order['side'],
                'Quantity': order['quantity'],
                'Price': f"${order['price']:.4f}",
                'Total': f"${order['total']:.2f}"
            })
        df_orders = pd.DataFrame(orders_data)
        st.dataframe(df_orders, use_container_width=True)
    else:
        st.info("No orders yet")

with col_right:
    st.subheader("📊 TRADING STATS")
    
    stats_data = {
        'Metric': ['Total Orders', 'Buy Orders', 'Sell Orders', 'Assets Held', 'Total Trades'],
        'Value': [
            len(engine.orders_history),
            len([o for o in engine.orders_history if o['side'] == 'BUY']),
            len([o for o in engine.orders_history if o['side'] == 'SELL']),
            len(engine.portfolio),
            len(engine.orders_history)
        ]
    }
    st.dataframe(pd.DataFrame(stats_data), use_container_width=True)

# SEZIONE AZIONI RAPIDE
st.markdown("---")
st.subheader("⚡ QUICK ACTIONS")

action_col1, action_col2, action_col3, action_col4 = st.columns(4)

with action_col1:
    if st.button("🔄 RUN TRADING CYCLE", use_container_width=True):
        with st.spinner("Running trading cycle..."):
            trader.run_cycle()
        st.success("Trading cycle completed!")
        st.rerun()

with action_col2:
    if st.button("📊 REFRESH DATA", use_container_width=True):
        st.rerun()

with action_col3:
    if st.button("💾 SAVE STATE", use_container_width=True):
        engine.save_to_json()
        st.success("State saved!")

with action_col4:
    if st.button("🔄 RELOAD ENGINE", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()

# AUTO-REFRESH
st.markdown("---")
auto_refresh = st.checkbox("🔄 Auto-refresh every 30 seconds", value=True)
if auto_refresh:
    time.sleep(30)
    st.rerun()

st.markdown("---")
st.markdown("**🚀 QUANTUM PAPER TRADING SYSTEM** - Monitor your virtual trading in real-time!")
