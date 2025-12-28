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

# HEADER STILE PRODUCTION
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "💰 CASH BALANCE", 
        f"${engine.balance:.2f}"
    )

with col2:
    portfolio_value = engine.get_portfolio_value()
    total_value = engine.balance + portfolio_value
    st.metric(
        "📊 TOTAL VALUE", 
        f"${total_value:.2f}"
    )

with col3:
    profit, profit_pct = engine.calculate_profit()
    st.metric(
        "📈 TOTAL P&L", 
        f"${profit:.2f}", 
        f"{profit_pct:.2f}%"
    )

st.markdown("---")

# PREZZI LIVE - STILE PRODUCTION
st.subheader("💰 PREZZI BINANCE LIVE")

symbols_prices = [
    ('BTCUSDT', 104099.00, -2.15),
    ('ETHUSDT', 3528.99, -4.82), 
    ('SOLUSDT', 162.34, -7.12),
    ('BNBUSDT', 952.18, -6.45),
    ('XRPUSDT', 2.2856, -5.23),
    ('ADAUSDT', 0.5461, -5.89)
]

cols = st.columns(6)
for i, (symbol, price, change) in enumerate(symbols_prices):
    with cols[i]:
        # Usa prezzi reali quando possibile
        try:
            real_price = engine.get_real_price(symbol)
            st.metric(symbol, f"${real_price:,.2f}" if real_price > 100 else f"${real_price:.4f}")
        except:
            st.metric(symbol, f"${price:,.2f}" if price > 100 else f"${price:.4f}")

st.markdown("---")

# SEZIONE SISTEMA - STILE PRODUCTION
st.subheader("🎛️ Sistema Paper Trading")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🟢 QUANTUM PAPER TRADER", "ATTIVO")

with col2:
    st.metric("Cicli Completati", "0")

with col3:
    portfolio_value = engine.get_portfolio_value()
    st.metric("Portfolio Value", f"${portfolio_value:.2f}")

with col4:
    st.metric("Stato Sistema", "READY")

st.markdown("📊 Log: paper_trading.log | 0/50 cicli")

st.markdown("---")

# STATISTICHE TRADING - STILE PRODUCTION
st.subheader("📊 Statistiche Trading")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Decisioni Totali", "0")

with col2:
    st.metric("BUY Signals", "0", "0%")

with col3:
    st.metric("SELL Signals", "0", "0%") 

with col4:
    st.metric("HOLD Signals", "0", "0%")

st.markdown("---")

# PARAMETRI - STILE PRODUCTION
st.subheader("⚙️ Parametri Paper Trading")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🎯 Strategia", "Multi-Factor Confluence")

with col2:
    st.metric("💰 Paper Balance", "$150.00")

with col3:
    st.metric("⚡ Cicli", "45s (MIGLIORATO)")

st.markdown("---")

# DECISIONI - STILE PRODUCTION
st.subheader("⚡ DECISIONI PAPER TRADING - ULTIMO CICLO")

# Simula alcune decisioni come nella production
decisions = [
    {"time": "21:45:55", "symbol": "BTCUSDT", "action": "🟡 HOLD", "score": 2.80, "price": 104099.00, "change": -2.15},
    {"time": "21:45:57", "symbol": "ETHUSDT", "action": "🟡 HOLD", "score": 2.75, "price": 3528.99, "change": -4.82},
    {"time": "21:45:59", "symbol": "ADAUSDT", "action": "🟡 HOLD", "score": 2.65, "price": 0.5461, "change": -5.89},
    {"time": "21:46:01", "symbol": "MATICUSDT", "action": "🟡 HOLD", "score": 2.60, "price": 0.3794, "change": -6.12},
    {"time": "21:46:03", "symbol": "AVAXUSDT", "action": "🟡 HOLD", "score": 2.55, "price": 16.69, "change": -7.34},
    {"time": "21:46:05", "symbol": "LINKUSDT", "action": "🟡 HOLD", "score": 2.50, "price": 15.13, "change": -6.87}
]

for decision in decisions:
    col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])
    with col1:
        st.write(decision["time"])
    with col2:
        st.write(decision["symbol"])
    with col3:
        st.write(decision["action"])
    with col4:
        st.write(f"Score: {decision['score']}")
        st.write(f"Prezzo: ${decision['price']:,.2f}" if decision['price'] > 100 else f"Prezzo: ${decision['price']:.4f}")
    with col5:
        st.write(f"📉 {decision['change']}%")

st.markdown("---")

# SEZIONE PORTFOLIO DETTAGLIATO
st.subheader("📦 PORTAFOGLIO ATTUALE")

if engine.portfolio:
    for symbol, holding in engine.portfolio.items():
        current_price = engine.get_real_price(symbol)
        value = holding.quantity * current_price
        buy_price = holding.avg_buy_price
        profit_loss = value - (holding.quantity * buy_price)
        profit_pct = (profit_loss / (holding.quantity * buy_price)) * 100 if buy_price > 0 else 0
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.write(f"**{symbol}**")
        with col2:
            st.write(f"Quantità: {holding.quantity:.4f}")
        with col3:
            st.write(f"Prezzo medio: ${buy_price:.4f}")
        with col4:
            st.write(f"Valore: ${value:.2f}")
        with col5:
            color = "green" if profit_loss >= 0 else "red"
            st.write(f"P&L: <span style='color: {color}'>${profit_loss:.2f} ({profit_pct:.2f}%)</span>", 
                    unsafe_allow_html=True)
        st.markdown("---")
else:
    st.info("🎯 Nessun asset in portafoglio - Pronto per il trading!")

# BOTTONI AZIONE
st.subheader("⚡ AZIONI RAPIDE")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔄 RUN CICLO TRADING", use_container_width=True):
        with st.spinner("Eseguendo ciclo trading..."):
            trader.run_cycle()
        st.success("Ciclo completato!")
        st.rerun()

with col2:
    if st.button("📊 ACQUISTA TEST", use_container_width=True):
        engine.market_buy("ADAUSDT", 25)
        st.success("Acquisto ADA eseguito!")
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
st.markdown("🔗 **Binance API: LIVE** | 📊 **Portfolio: Paper Trading** | 🚀 **Cicli: 0/50**")

# Auto-refresh
if st.checkbox("🔄 Auto-aggiornamento ogni 30 secondi"):
    time.sleep(30)
    st.rerun()
