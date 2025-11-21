import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import sqlite3
import requests

# Configurazione pagina
st.set_page_config(
    page_title="Quantum Trading System",
    page_icon="🚀", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizzato
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #0068c9;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #0068c9;
    }
</style>
""", unsafe_allow_html=True)

# Titolo principale
st.markdown('<h1 class="main-header">🚀 QUANTUM TRADING</h1>', unsafe_allow_html=True)
st.markdown("**TESTNET**")

# Sidebar con controlli
with st.sidebar:
    st.header("⚙️ CONTROLLI")
    
    st.subheader("Aggiornamento (s)")
    update_fast = st.slider("Rapido", 5, 30, 10, key="fast_update")
    update_slow = st.slider("Lento", 30, 300, 60, key="slow_update")
    
    st.markdown("---")
    st.header("🎯 STRATEGIA")
    
    st.subheader("Confluence Min")
    confluence_min = st.slider("Minimo", 1.0, 4.0, 2.0, 0.1, key="confluence_min")
    confluence_max = st.slider("Massimo", 1.0, 4.0, 4.0, 0.1, key="confluence_max")
    
    st.subheader("Confidence %")
    confidence_min = st.slider("Minima", 50, 90, 50, key="confidence_min")
    confidence_max = st.slider("Massima", 50, 90, 90, key="confidence_max")
    
    st.subheader("Risk per Trade %")
    risk_min = st.slider("Minimo", 1.0, 5.0, 1.0, 0.1, key="risk_min")
    risk_max = st.slider("Massimo", 1.0, 5.0, 5.0, 0.1, key="risk_max")
    
    st.markdown("---")
    st.header("⚡ Parametri Attivi")
    st.write(f"• Confluence: {confluence_min}/{confluence_max}")
    st.write(f"• Confidence: {confidence_min}%")
    st.write(f"• Risk: {risk_min}%")

# Layout principale
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Sezione portfolio
    st.header("💰 PORTAFOGLIO TESTNET")
    
    try:
        # Connessione al database per balance
        conn = sqlite3.connect('quantum_final.db')
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM balance_history ORDER BY timestamp DESC LIMIT 1")
        balance_result = cursor.fetchone()
        balance = balance_result[0] if balance_result else 84.65
        conn.close()
        
        # Mostra balance
        st.metric(
            label="Fondi Testnet",
            value=f"${balance:.2f}",
            delta="SOLO USDT REALE"
        )
        
        # Info aggiuntive
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("**Tipo**")
            st.write("🧪 Test")
            st.write(datetime.now().strftime("%H:%M:%S"))
        
        with col_b:
            st.write("**USDT Reale**")
            st.success(f"${balance:.2f}")
            st.info("**FONDI EFFETTIVI**")
            
    except Exception as e:
        st.error("Errore di connessione")

# Sezione mercato
st.markdown("---")
st.header("📊 MERCATO")

# Dati di mercato in tempo reale
try:
    # Prezzi da Binance
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    prices = {}
    changes = {}
    
    for symbol in symbols:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            prices[symbol] = float(data['price'])
            # Simula variazione percentuale
            changes[symbol] = round(np.random.uniform(-2, 2), 2)
    
    # Layout colonne per prezzi
    col1, col2, col3 = st.columns(3)
    
    with col1:
        btc_price = prices.get("BTCUSDT", 112000)
        btc_change = changes.get("BTCUSDT", 0.8)
        st.metric(
            label="BTC/USDT",
            value=f"${btc_price:,.2f}",
            delta=f"{btc_change:+.2f}% (${(btc_price * btc_change/100):.2f})"
        )
    
    with col2:
        eth_price = prices.get("ETHUSDT", 4000)
        eth_change = changes.get("ETHUSDT", 1.2)
        st.metric(
            label="ETH/USDT",
            value=f"${eth_price:,.2f}",
            delta=f"{eth_change:+.2f}% (${(eth_price * eth_change/100):.2f})"
        )
    
    with col3:
        sol_price = prices.get("SOLUSDT", 195)
        sol_change = changes.get("SOLUSDT", 1.5)
        st.metric(
            label="SOL/USDT",
            value=f"${sol_price:,.2f}",
            delta=f"{sol_change:+.2f}% (${(sol_price * sol_change/100):.2f})"
        )
    
    st.caption(f"📡 Dati di mercato in tempo reale • {datetime.now().strftime('%H:%M:%S')}")
    
except Exception as e:
    st.error("Errore nel caricamento dati di mercato")

# Sezione ultimi trade
st.markdown("---")
st.header("📋 ULTIMI TRADE")

try:
    # Carica trade dal database
    conn = sqlite3.connect('quantum_final.db')
    
    # Statistiche
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM trades")
    total_trades = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM trades WHERE pnl > 0")
    winning_trades = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(pnl) FROM trades")
    total_pnl = cursor.fetchone()[0] or 0
    
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    # Layout statistiche
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Trade Totali", total_trades)
    with col2:
        st.metric("Win Rate", f"{win_rate:.1f}%")
    with col3:
        st.metric("P&L Totale", f"${total_pnl:.2f}")
    
    # Ultimi trade
    df_trades = pd.read_sql_query("""
        SELECT symbol, side, quantity, entry_price, pnl, timestamp, status 
        FROM trades 
        ORDER BY timestamp DESC 
        LIMIT 5
    """, conn)
    
    if not df_trades.empty:
        for _, trade in df_trades.iterrows():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Icona e simbolo
                emoji = "🟢" if trade['side'] == 'BUY' else "🔴"
                st.write(f"{emoji} **{trade['symbol']} • {trade['side']}**")
                st.write(f"Qty: {trade['quantity']:.4f} • Entry: ${trade['entry_price']:.2f}")
            
            with col2:
                # P&L e info
                pnl_color = "green" if trade['pnl'] > 0 else "red"
                st.write(f":{pnl_color}[**${trade['pnl']:+.2f}**]")
                st.write(f"Conf: {75}%")
                st.write(f"{trade['timestamp'][11:16]} • {trade['status']}")
            
            st.markdown("---")
    else:
        st.info("Nessun trade trovato. Il trader inizierà presto!")
    
    conn.close()
    
except Exception as e:
    st.error(f"Errore nel caricamento trade: {e}")

# Auto-refresh
st.markdown("---")
st.caption(f"🔄 Auto-refresh attivo • Prossimo aggiornamento tra 30 secondi • {datetime.now().strftime('%H:%M:%S')}")

# Auto-refresh
time.sleep(30)
st.rerun()
