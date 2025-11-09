import streamlit as st
import pandas as pd
import time
from datetime import datetime
import json
import os
from paper_trading_engine import PaperTradingEngine

st.set_page_config(
    page_title="QUANTUM PAPER TRADING LIVE",
    page_icon="🚀",
    layout="wide"
)

def load_trader_state():
    """Carica lo stato dal file salvato dal trader"""
    try:
        # Crea un engine temporaneo per caricare lo stato
        engine = PaperTradingEngine(150)
        if os.path.exists('paper_trading_state.json'):
            success = engine.load_from_json('paper_trading_state.json')
            if success:
                return engine
        return None
    except Exception as e:
        st.error(f"Errore caricamento stato: {e}")
        return None

st.title("🚀 QUANTUM PAPER TRADING - LIVE MONITOR")
st.markdown("📊 **LIVE DATA FROM RUNNING TRADER**")
st.markdown("---")

# Carica stato attuale
engine = load_trader_state()

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
    
    # PORTAFOGLIO REALE
    st.subheader("📦 LIVE PORTFOLIO")
    
    if hasattr(engine, 'portfolio') and engine.portfolio:
        portfolio_data = []
        
        for symbol, holding_data in engine.portfolio.items():
            try:
                current_price = engine.get_real_price(symbol)
                if not current_price:
                    continue
                    
                # Gestione diversi tipi di dati portfolio
                if hasattr(holding_data, 'as_tuple'):  # Decimal
                    quantity = float(holding_data)
                    profit_data = engine.get_asset_profit(symbol)
                    if profit_data:
                        avg_buy_price = profit_data['avg_buy_price']
                        current_value = profit_data['current_value']
                        profit_usd = profit_data['profit_usd']
                        profit_pct = profit_data['profit_pct']
                    else:
                        avg_buy_price = current_price
                        current_value = quantity * current_price
                        profit_usd = 0
                        profit_pct = 0
                else:  # Oggetto Holding
                    quantity = holding_data.quantity
                    avg_buy_price = holding_data.avg_buy_price
                    current_value = quantity * current_price
                    profit_usd = current_value - (quantity * avg_buy_price)
                    profit_pct = (profit_usd / (quantity * avg_buy_price)) * 100 if avg_buy_price > 0 else 0
                
                portfolio_data.append({
                    'symbol': symbol,
                    'quantity': quantity,
                    'avg_buy_price': avg_buy_price,
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
                    st.write(f"Qty: {item['quantity']:.6f}")
                with col3:
                    st.write(f"Avg: ${item['avg_buy_price']:.4f}")
                with col4:
                    st.write(f"Value: ${item['current_value']:.2f}")
                with col5:
                    color = "green" if item['profit_usd'] >= 0 else "red"
                    st.markdown(f"<span style='color: {color}'>P&L: ${item['profit_usd']:.2f} ({item['profit_pct']:+.2f}%)</span>", 
                               unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("🎯 Nessun asset in portafoglio")
    else:
        st.info("🎯 Nessun asset in portafoglio")
    
    # ULTIMI ORDINI
    st.subheader("⚡ ULTIMI ORDINI")
    
    if engine.orders_history:
        for order in reversed(engine.orders_history[-10:]):
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                if hasattr(order['timestamp'], 'strftime'):
                    st.write(order['timestamp'].strftime('%H:%M:%S'))
                else:
                    st.write(str(order['timestamp']))
            with col2:
                st.write(order['symbol'])
            with col3:
                emoji = "🟢" if order['side'] == 'BUY' else "🔴"
                st.write(f"{emoji} {order['side']}")
            with col4:
                if order['price'] > 1:
                    st.write(f"${order['price']:.2f}")
                else:
                    st.write(f"${order['price']:.4f}")
            with col5:
                st.write(f"Qty: {order['quantity']:.4f}")
    else:
        st.info("📭 Nessun ordine ancora")
    
    # STATISTICHE
    st.markdown("---")
    st.subheader("📊 LIVE STATISTICS")
    
    total_orders = len(engine.orders_history)
    buy_orders = len([o for o in engine.orders_history if o['side'] == 'BUY'])
    sell_orders = len([o for o in engine.orders_history if o['side'] == 'SELL'])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Ordini Totali", total_orders)
    with col2:
        st.metric("BUY Orders", buy_orders)
    with col3:
        st.metric("SELL Orders", sell_orders)
    with col4:
        st.metric("Assets in Portfolio", len(engine.portfolio) if hasattr(engine, 'portfolio') else 0)

else:
    st.error("❌ Impossibile caricare lo stato del trader")
    st.info("Assicurati che il trader sia in esecuzione e abbia salvato lo stato")

# Auto-refresh
st.markdown("---")
if st.button("🔄 Aggiorna Manualmente"):
    st.rerun()

auto_refresh = st.checkbox("🔄 Auto-aggiornamento ogni 15 secondi", value=True)
if auto_refresh:
    time.sleep(15)
    st.rerun()

st.markdown("---")
st.markdown("**🔗 Lettura dati da: paper_trading_state.json**")
