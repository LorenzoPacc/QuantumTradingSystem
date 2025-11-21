import streamlit as st
import pandas as pd
import time
from datetime import datetime
from paper_trading_engine import PaperTradingEngine

st.set_page_config(
    page_title="QUANTUM TRADING - PERFECT DASHBOARD",
    page_icon="🚀",
    layout="wide"
)

def load_engine():
    """Carica engine con gestione errori robusta"""
    try:
        engine = PaperTradingEngine(200)
        success = engine.load_from_json('paper_trading_state.json')
        return engine if success else None
    except Exception as e:
        st.error(f"Load error: {e}")
        return None

st.title("🚀 QUANTUM PAPER TRADING - PERFECT DASHBOARD")
st.markdown("📊 **Live Monitoring - PORTFOLIO VISIBLE**")
st.markdown("---")

# Carica engine
engine = load_engine()

if engine:
    # HEADER
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 CASH BALANCE", f"${float(engine.balance):.2f}")
    
    with col2:
        portfolio_value = float(engine.get_portfolio_value())
        total_value = float(engine.balance) + portfolio_value
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
    
    # PORTAFOGLIO - VERSIONE SEMPLIFICATA E SICURA
    st.subheader("📦 LIVE PORTFOLIO")
    
    portfolio_count = len(engine.portfolio) if hasattr(engine, 'portfolio') else 0
    
    if portfolio_count > 0:
        st.success(f"✅ {portfolio_count} ASSETS IN PORTFOLIO")
        
        # Visualizzazione semplificata ma funzionante
        for symbol in list(engine.portfolio.keys())[:6]:  # Max 6 assets
            try:
                quantity = float(engine.portfolio[symbol])
                current_price = engine.get_real_price(symbol)
                current_value = quantity * current_price
                
                # Calcolo P&L semplificato
                profit_data = engine.get_asset_profit(symbol)
                if profit_data and 'profit_pct' in profit_data:
                    pnl_pct = profit_data['profit_pct']
                    pnl_usd = profit_data['profit_usd']
                    color = "🟢" if pnl_usd >= 0 else "🔴"
                else:
                    pnl_pct = 0
                    pnl_usd = 0
                    color = "⚪"
                
                # Mostra ogni asset
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(f"**{symbol}**")
                with col2:
                    st.write(f"Qty: {quantity:.4f}")
                with col3:
                    st.write(f"Value: ${current_value:.2f}")
                with col4:
                    st.write(f"{color} P&L: {pnl_pct:+.2f}%")
                
                st.markdown("---")
                
            except Exception as e:
                st.write(f"❌ Error with {symbol}: {str(e)}")
                continue
    else:
        st.info("📭 No assets in portfolio")
    
    st.markdown("---")
    
    # ULTIMI ORDINI - VERSIONE SICURA
    st.subheader("⚡ RECENT ORDERS")
    
    if hasattr(engine, 'orders_history') and engine.orders_history:
        recent_orders = engine.orders_history[-5:]  # Ultimi 5 ordini
        
        for order in reversed(recent_orders):
            try:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(order['symbol'])
                with col2:
                    emoji = "🟢" if order['side'] == 'BUY' else "🔴"
                    st.write(f"{emoji} {order['side']}")
                with col3:
                    amount = order.get('usdt_spent', order.get('total', 0))
                    st.write(f"${amount:.2f}")
                with col4:
                    timestamp = order['timestamp']
                    if hasattr(timestamp, 'strftime'):
                        st.write(timestamp.strftime('%H:%M:%S'))
                    else:
                        st.write(str(timestamp)[11:19])
            except:
                continue
    else:
        st.info("📋 No orders yet")
    
    # STATISTICHE
    st.markdown("---")
    st.subheader("📊 TRADING STATISTICS")
    
    total_orders = len(engine.orders_history) if hasattr(engine, 'orders_history') else 0
    buy_orders = len([o for o in engine.orders_history if o['side'] == 'BUY']) if engine.orders_history else 0
    sell_orders = len([o for o in engine.orders_history if o['side'] == 'SELL']) if engine.orders_history else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Orders", total_orders)
    with col2:
        st.metric("BUY Orders", buy_orders)
    with col3:
        st.metric("SELL Orders", sell_orders)
    with col4:
        st.metric("Assets Held", portfolio_count)

else:
    st.error("❌ Cannot load trading data")
    st.info("Ensure trader is running and paper_trading_state.json exists")

# Auto-refresh
st.markdown("---")
if st.button("🔄 Refresh Now"):
    st.rerun()

if st.checkbox("🔄 Auto-refresh every 20 seconds", value=True):
    time.sleep(20)
    st.rerun()

st.markdown("---")
st.markdown("**🎯 Quantum Advanced Strategy - Portfolio VISIBLE**")
