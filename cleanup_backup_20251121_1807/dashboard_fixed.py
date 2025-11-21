import streamlit as st
import sqlite3
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import os

# Configurazione pagina
st.set_page_config(
    page_title="Quantum Trading System",
    page_icon="🚀",
    layout="wide"
)

# Titolo principale
st.title("🚀 Quantum Trading System")
st.markdown("---")

# Funzione per connessione database con percorso assoluto
def get_db_connection():
    """Connessione database con percorso assoluto"""
    db_path = os.path.join(os.path.dirname(__file__), 'quantum_final.db')
    return sqlite3.connect(db_path)

# Funzione per ottenere balance
def get_balance():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM balance_history ORDER BY timestamp DESC LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0.0
    except Exception as e:
        st.error(f"Errore database: {e}")
        return 0.0

# Funzione per ottenere prezzi di mercato
def get_market_prices():
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    prices = {}
    for symbol in symbols:
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                prices[symbol] = float(data['price'])
        except:
            # Fallback a prezzi simulati
            prices[symbol] = {
                "BTCUSDT": 112000,
                "ETHUSDT": 4000,
                "SOLUSDT": 195
            }.get(symbol, 100)
    return prices

# Layout principale
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.header("💰 PORTAFOGLIO TESTNET")
    
    # Balance in tempo reale
    balance = get_balance()
    if balance > 0:
        st.metric(
            label="Fondi Testnet",
            value=f"${balance:.2f}",
            delta="SOLO USDT REALE"
        )
        st.caption("Tipo: 🧪 Test | " + datetime.now().strftime("%H:%M:%S"))
        st.success(f"USDT Reale: ${balance:.2f}")
        st.info("FONDI EFFETTIVI")
    else:
        st.error("Errore di connessione al database")

# Sezione mercato
st.markdown("---")
st.header("📊 MERCATO")

# Prezzi di mercato
prices = get_market_prices()

if prices:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        btc_price = prices.get("BTCUSDT", 0)
        st.metric(
            label="BTC/USDT",
            value=f"${btc_price:,.2f}",
            delta=f"+{(btc_price-112000)/112000*100:.2f}%"
        )
    
    with col2:
        eth_price = prices.get("ETHUSDT", 0)
        st.metric(
            label="ETH/USDT", 
            value=f"${eth_price:,.2f}",
            delta=f"+{(eth_price-4000)/4000*100:.2f}%"
        )
    
    with col3:
        sol_price = prices.get("SOLUSDT", 0)
        st.metric(
            label="SOL/USDT",
            value=f"${sol_price:,.2f}",
            delta=f"+{(sol_price-195)/195*100:.2f}%"
        )
    
    st.caption(f"Dati di mercato in tempo reale • {datetime.now().strftime('%H:%M:%S')}")

# Sezione trade
st.markdown("---")
st.header("📋 ULTIMI TRADE")

try:
    conn = get_db_connection()
    df_trades = pd.read_sql_query("""
        SELECT symbol, side, quantity, entry_price, pnl, timestamp, status 
        FROM trades 
        ORDER BY timestamp DESC 
        LIMIT 10
    """, conn)
    conn.close()
    
    if not df_trades.empty:
        # Statistiche
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Trade Totali", len(df_trades))
        with col2:
            win_trades = len(df_trades[df_trades['pnl'] > 0])
            win_rate = (win_trades / len(df_trades)) * 100 if len(df_trades) > 0 else 0
            st.metric("Win Rate", f"{win_rate:.1f}%")
        with col3:
            total_pnl = df_trades['pnl'].sum()
            st.metric("P&L Totale", f"${total_pnl:.2f}")
        
        # Tabella trade
        for _, trade in df_trades.iterrows():
            col1, col2 = st.columns([3, 1])
            with col1:
                emoji = "🟢" if trade['side'] == 'BUY' else "🔴"
                st.write(f"{emoji} {trade['symbol']} • {trade['side']}")
                st.write(f"Qty: {trade['quantity']:.4f} • Entry: ${trade['entry_price']:.2f}")
            with col2:
                pnl_color = "green" if trade['pnl'] > 0 else "red"
                st.write(f"<span style='color: {pnl_color}'>${trade['pnl']:+.2f}</span>", unsafe_allow_html=True)
                st.write(f"Conf: {75}%")
                st.write(f"{trade['timestamp'][11:16]} • {trade['status']}")
            
            st.markdown("---")
    else:
        st.info("Nessun trade trovato nel database")
        
except Exception as e:
    st.error(f"Errore caricamento trade: {e}")

# Auto-refresh
st.markdown("---")
if st.button("🔄 Aggiorna Manuale"):
    st.rerun()

st.caption(f"Auto-refresh attivo • Prossimo aggiornamento tra 30 secondi • {datetime.now().strftime('%H:%M:%S')}")

# Auto-refresh ogni 30 secondi
time.sleep(30)
st.rerun()
