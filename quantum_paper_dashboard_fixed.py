import streamlit as st
import pandas as pd
import time
from datetime import datetime
import plotly.graph_objects as go
from paper_trading_engine import PaperTradingEngine
from quantum_trader_paper import QuantumTraderPaper

st.set_page_config(
    page_title="QUANTUM PAPER TRADING",
    page_icon="🚀",
    layout="wide"
)

# Inizializzazione Paper Trading
@st.cache_resource
def get_paper_trader():
    return QuantumTraderPaper(150)

trader = get_paper_trader()
engine = trader.engine

st.title("🚀 QUANTUM PAPER TRADING")
st.markdown("📊 **PAPER TRADING MODE** - $150 Virtual Balance")
st.markdown("---")

# HEADER PRINCIPALE
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("💰 CASH BALANCE", f"${engine.balance:.2f}")

with col2:
    portfolio_value = engine.get_portfolio_value()
    total_value = engine.balance + portfolio_value
    st.metric("📊 TOTAL VALUE", f"${total_value:.2f}")

with col3:
    profit, profit_pct = engine.calculate_profit()
    st.metric("📈 TOTAL P&L", f"${profit:.2f}", f"{profit_pct:.2f}%")

st.markdown("---")

# PREZZI LIVE REALI
st.subheader("💰 PREZZI BINANCE LIVE")

symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT']
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
        except Exception as e:
            st.metric(symbol, "N/A")

st.markdown("---")

# SEZIONE SISTEMA
st.subheader("🎛️ Sistema Paper Trading")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🟢 QUANTUM PAPER TRADER", "ATTIVO")

with col2:
    # Conta cicli dagli ordini
    cycles = len(engine.orders_history) // 2 if len(engine.orders_history) > 0 else 0
    st.metric("Cicli Completati", cycles)

with col3:
    portfolio_value = engine.get_portfolio_value()
    st.metric("Portfolio Value", f"${portfolio_value:.2f}")

with col4:
    st.metric("Stato Sistema", "READY")

st.markdown("---")

# STATISTICHE TRADING REALI
st.subheader("📊 Statistiche Trading")

total_orders = len(engine.orders_history)
buy_orders = len([o for o in engine.orders_history if o['side'] == 'BUY'])
sell_orders = len([o for o in engine.orders_history if o['side'] == 'SELL'])

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Ordini Totali", total_orders)

with col2:
    buy_pct = f"{buy_orders/total_orders*100:.1f}%" if total_orders > 0 else "0%"
    st.metric("BUY Orders", buy_orders, buy_pct)

with col3:
    sell_pct = f"{sell_orders/total_orders*100:.1f}%" if total_orders > 0 else "0%"
    st.metric("SELL Orders", sell_orders, sell_pct)

with col4:
    st.metric("Fee Totali", f"${float(engine.total_fees):.4f}")

st.markdown("---")

# PARAMETRI
st.subheader("⚙️ Parametri Paper Trading")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🎯 Strategia", "Multi-Factor")

with col2:
    st.metric("💰 Balance Iniziale", "$150.00")

with col3:
    st.metric("⚡ Fee Rate", "0.1%")

st.markdown("---")

# PORTAFOGLIO REALE
st.subheader("📦 PORTAFOGLIO ATTUALE")

if hasattr(engine, 'portfolio') and engine.portfolio:
    portfolio_data = []
    
    for symbol, holding_data in engine.portfolio.items():
        try:
            current_price = engine.get_real_price(symbol)
            if not current_price:
                continue
                
            # Se holding_data è un Decimal (quantità)
            if hasattr(holding_data, 'as_tuple'):
                quantity = float(holding_data)
                # Calcola dati profit
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
            else:
                # Se è un oggetto Holding
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
        st.info("🎯 Nessun asset in portafoglio - Pronto per il trading!")
else:
    st.info("🎯 Nessun asset in portafoglio - Pronto per il trading!")

# ULTIMI ORDINI REALI
st.subheader("⚡ ULTIMI ORDINI")

if engine.orders_history:
    for order in reversed(engine.orders_history[-6:]):
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
    st.info("📭 Nessun ordine ancora - Avvia il primo ciclo!")

st.markdown("---")

# AZIONI RAPIDE
st.subheader("⚡ AZIONI RAPIDE")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔄 RUN TRADING CYCLE", use_container_width=True):
        with st.spinner("Eseguendo ciclo trading..."):
            trader.run_cycle()
        st.success("Ciclo completato!")
        time.sleep(2)
        st.rerun()

with col2:
    if st.button("💰 BUY ADA TEST", use_container_width=True):
        result = engine.market_buy("ADAUSDT", 25)
        if result:
            st.success("Acquisto ADA eseguito!")
        else:
            st.error("Acquisto fallito!")
        time.sleep(2)
        st.rerun()

with col3:
    if st.button("💾 SALVA STATO", use_container_width=True):
        engine.save_to_json()
        st.success("Stato salvato!")

with col4:
    if st.button("🔄 AGGIORNA", use_container_width=True):
        st.rerun()

# FOOTER
st.markdown("---")
st.markdown("🔗 **Binance API: LIVE** | 📊 **Paper Trading** | 🚀 **Sistema Attivo**")

# Auto-refresh
auto_refresh = st.checkbox("🔄 Auto-aggiornamento ogni 30 secondi", value=False)
if auto_refresh:
    time.sleep(30)
    st.rerun()
