import streamlit as st
import pandas as pd
import time
from datetime import datetime
from paper_trading_engine import PaperTradingEngine

st.set_page_config(
    page_title="QUANTUM TRADING - WORKING DASHBOARD",
    page_icon="🚀",
    layout="wide"
)

def load_engine():
    """Carica engine semplice e funzionante"""
    try:
        engine = PaperTradingEngine(200)
        engine.load_from_json('paper_trading_state.json')
        return engine
    except:
        return None

st.title("🚀 QUANTUM PAPER TRADING - WORKING DASHBOARD")
st.markdown("📊 **Live Monitoring - FIXED PORTFOLIO**")
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
    
    # PORTAFOGLIO - VISUALIZZAZIONE CORRETTA
    st.subheader("📦 LIVE PORTFOLIO")
    
    if hasattr(engine, 'portfolio') and engine.portfolio:
        st.success(f"✅ {len(engine.portfolio)} ASSETS IN PORTFOLIO")
        
        # Crea tabella portfolio
        portfolio_data = []
        for symbol, quantity in engine.portfolio.items():
            try:
                current_price = engine.get_real_price(symbol)
                current_value = float(quantity) * current_price
                
                # Calcola P&L
                profit_data = engine.get_asset_profit(symbol)
                if profit_data:
                    profit_usd = profit_data['profit_usd']
                    profit_pct = profit_data['profit_pct']
                    avg_price = profit_data['avg_buy_price']
                else:
                    profit_usd = 0
                    profit_pct = 0
                    avg_price = current_price
                
                portfolio_data.append({
                    'Asset': symbol,
                    'Quantity': float(quantity),
                    'Avg Price': f"${avg_price:.4f}",
                    'Current Price': f"${current_price:.4f}",
                    'Current Value': f"${current_value:.2f}",
                    'P&L USD': f"${profit_usd:.2f}",
                    'P&L %': f"{profit_pct:.2f}%"
                })
            except Exception as e:
                continue
        
        if portfolio_data:
            # Mostra come tabella
            df = pd.DataFrame(portfolio_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("📭 Error calculating portfolio values")
    else:
        st.info("📭 No assets in portfolio")
    
    st.markdown("---")
    
    # ULTIMI ORDINI
    st.subheader("⚡ RECENT ORDERS")
    
    if engine.orders_history:
        orders_data = []
        for order in engine.orders_history[-6:]:
            orders_data.append({
                'Time': order['timestamp'].strftime('%H:%M:%S') if hasattr(order['timestamp'], 'strftime') else str(order['timestamp'])[11:19],
                'Symbol': order['symbol'],
                'Side': order['side'],
                'Amount': f"${order.get('usdt_spent', order.get('total', 0)):.2f}",
                'Price': f"${order['price']:.4f}"
            })
        
        df_orders = pd.DataFrame(orders_data)
        st.dataframe(df_orders, use_container_width=True)
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
    st.error("❌ Cannot load trading engine")
    st.info("Please ensure the trader is running")

# Auto-refresh
st.markdown("---")
if st.button("🔄 Refresh Now"):
    st.rerun()

auto_refresh = st.checkbox("🔄 Auto-refresh every 15 seconds", value=True)
if auto_refresh:
    time.sleep(15)
    st.rerun()

st.markdown("---")
st.markdown("**🚀 Quantum Trading System - Portfolio FIXED**")
