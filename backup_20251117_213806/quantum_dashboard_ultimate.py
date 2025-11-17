import streamlit as st
import pandas as pd
import time
from datetime import datetime
import json
import os
from paper_trading_engine import PaperTradingEngine

st.set_page_config(
    page_title="QUANTUM TRADING DASHBOARD",
    page_icon="🚀",
    layout="wide"
)

def safe_load_trader_state():
    """Carica stato con gestione errori robusta"""
    try:
        # Verifica che il file esista e non sia vuoto
        if not os.path.exists('paper_trading_state.json'):
            return None
            
        file_size = os.path.getsize('paper_trading_state.json')
        if file_size == 0:
            return None
            
        # Leggi il file
        with open('paper_trading_state.json', 'r') as f:
            content = f.read().strip()
            if not content:
                return None
                
        # Crea engine e carica
        engine = PaperTradingEngine(150)
        success = engine.load_from_json('paper_trading_state.json')
        
        return engine if success else None
        
    except Exception as e:
        st.error(f"❌ Errore caricamento stato: {str(e)}")
        return None

st.title("🚀 QUANTUM PAPER TRADING DASHBOARD")
st.markdown("📊 **Live Monitoring - Paper Trading System**")
st.markdown("---")

# Carica stato
engine = safe_load_trader_state()

if engine:
    # HEADER PRINCIPALE
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 CASH BALANCE", f"${float(engine.balance):.2f}")
    
    with col2:
        portfolio_value = engine.get_portfolio_value()
        total_value = float(engine.balance) + float(portfolio_value)
        st.metric("📊 TOTAL VALUE", f"${total_value:.2f}")
    
    with col3:
        profit, profit_pct = engine.calculate_profit()
        st.metric("📈 TOTAL P&L", f"${float(profit):.2f}", f"{float(profit_pct):.2f}%")
    
    with col4:
        st.metric("💸 TOTAL FEES", f"${float(engine.total_fees):.2f}")
    
    st.markdown("---")
    
    # PREZZI LIVE
    st.subheader("💰 LIVE PRICES - BINANCE")
    
    symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'MATICUSDT', 'AVAXUSDT', 'LINKUSDT']
    cols = st.columns(6)
    
    for i, symbol in enumerate(symbols):
        with cols[i]:
            try:
                price = engine.get_real_price(symbol)
                if price > 1000:
                    display_price = f"${price:,.2f}"
                elif price > 1:
                    display_price = f"${price:.2f}"
                else:
                    display_price = f"${price:.4f}"
                st.metric(symbol, display_price)
            except:
                st.metric(symbol, "N/A")
    
    st.markdown("---")
    
    # PORTAFOGLIO
    st.subheader("📦 LIVE PORTFOLIO")
    
    if hasattr(engine, 'portfolio') and engine.portfolio:
        portfolio_data = []
        
        for symbol, quantity in engine.portfolio.items():
            try:
                current_price = engine.get_real_price(symbol)
                if not current_price:
                    continue
                    
                current_value = float(quantity) * current_price
                
                # Calcola P&L
                profit_data = engine.get_asset_profit(symbol)
                if profit_data:
                    avg_buy_price = profit_data['avg_buy_price']
                    profit_usd = profit_data['profit_usd']
                    profit_pct = profit_data['profit_pct']
                else:
                    avg_buy_price = current_price
                    profit_usd = 0
                    profit_pct = 0
                
                portfolio_data.append({
                    'symbol': symbol,
                    'quantity': float(quantity),
                    'current_price': current_price,
                    'current_value': current_value,
                    'profit_usd': profit_usd,
                    'profit_pct': profit_pct
                })
                
            except Exception as e:
                continue
        
        if portfolio_data:
            for item in portfolio_data:
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.write(f"**{item['symbol']}**")
                with col2:
                    st.write(f"Qty: {item['quantity']:.4f}")
                with col3:
                    st.write(f"Price: ${item['current_price']:.4f}")
                with col4:
                    st.write(f"Value: ${item['current_value']:.2f}")
                with col5:
                    color = "green" if item['profit_usd'] >= 0 else "red"
                    st.markdown(f"P&L: <span style='color: {color}'>${item['profit_usd']:.2f} ({item['profit_pct']:+.2f}%)</span>", 
                               unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("📭 Nessun asset in portafoglio")
    else:
        st.info("📭 Nessun asset in portafoglio")
    
    # ULTIMI ORDINI
    st.subheader("⚡ RECENT ORDERS")
    
    if engine.orders_history:
        # Mostra ultimi 5 ordini
        recent_orders = engine.orders_history[-5:]
        for order in reversed(recent_orders):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.write(order['symbol'])
            with col2:
                emoji = "🟢" if order['side'] == 'BUY' else "🔴"
                st.write(f"{emoji} {order['side']}")
            with col3:
                st.write(f"${order.get('usdt_spent', order.get('total', 0)):.2f}")
            with col4:
                if hasattr(order['timestamp'], 'strftime'):
                    st.write(order['timestamp'].strftime('%H:%M:%S'))
                else:
                    st.write(str(order['timestamp'])[11:19])
    else:
        st.info("📋 No orders yet")
    
    # STATISTICHE
    st.markdown("---")
    st.subheader("📊 TRADING STATISTICS")
    
    total_orders = len(engine.orders_history)
    buy_orders = len([o for o in engine.orders_history if o['side'] == 'BUY'])
    sell_orders = len([o for o in engine.orders_history if o['side'] == 'SELL'])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Orders", total_orders)
    with col2:
        st.metric("BUY Orders", buy_orders)
    with col3:
        st.metric("SELL Orders", sell_orders)
    with col4:
        st.metric("Assets Held", len(engine.portfolio))

else:
    st.error("⚠️ Cannot load trading state")
    st.info("Please ensure the trader is running and has saved its state")
    st.info("The system will auto-refresh when data is available")

# Auto-refresh
st.markdown("---")
if st.button("🔄 Refresh Now"):
    st.rerun()

auto_refresh = st.checkbox("🔄 Auto-refresh every 10 seconds", value=True)
if auto_refresh:
    time.sleep(10)
    st.rerun()

st.markdown("---")
st.markdown("**🔗 Connected to: paper_trading_state.json**")
st.markdown("**🚀 Quantum Trading System - Live Monitoring**")
