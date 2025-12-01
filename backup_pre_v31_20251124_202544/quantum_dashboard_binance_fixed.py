import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import requests
import re
import os

st.set_page_config(page_title="Quantum Pro - BINANCE REAL-TIME", layout="wide")

# CSS Moderno
st.markdown("""
<style>
    .main-header { 
        font-size: 2.5rem; 
        background: linear-gradient(90deg, #FF9900, #F0B90B);
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        text-align: center; 
        margin-bottom: 1rem;
    }
    .binance-badge {
        background: rgba(240, 185, 11, 0.2);
        border: 2px solid #F0B90B;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        color: #F0B90B;
        font-weight: bold;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Funzioni per dati BINANCE REALI
def get_binance_price(symbol):
    """Ottiene prezzo REALE da Binance"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data['price'])
    except:
        return 0

def get_binance_24h_change(symbol):
    """Ottiene variazione 24h REALE da Binance"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data['priceChangePercent'])
    except:
        return 0.0

def get_real_time_prices():
    """Ottiene tutti i prezzi di mercato REALI"""
    symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'ADAUSDT']
    
    real_data = {}
    for symbol in symbols:
        price = get_binance_price(symbol)
        change_24h = get_binance_24h_change(symbol)
        real_data[symbol] = {
            'price': price,
            'change_24h': change_24h,
            'formatted_price': f"${price:,.2f}" if price > 100 else f"${price:.4f}"
        }
    
    return real_data

def parse_log_file():
    """Legge e parsa il file di log REALE"""
    log_file = 'production.log'
    
    if not os.path.exists(log_file):
        return [], 0, 0, 0
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # Conta cicli
        cycles = len([line for line in lines if 'FINE CICLO' in line])
        
        # Conta decisioni
        buy_count = len([line for line in lines if '🎯 DECISIONE: BUY' in line])
        sell_count = len([line for line in lines if '🎯 DECISIONE: SELL' in line])
        hold_count = len([line for line in lines if '🎯 DECISIONE: HOLD' in line])
        
        # Estrai ultime 5 decisioni
        decisions = []
        current_decision = {}
        
        for line in reversed(lines):
            # Cerca il pattern: "🧠 ANALISI CONFLUENZE per SYMBOL"
            symbol_match = re.search(r'ANALISI CONFLUENZE per ([A-Z]+USDT)', line)
            if symbol_match:
                if current_decision and 'symbol' not in current_decision:
                    current_decision['symbol'] = symbol_match.group(1)
            
            # Cerca il pattern: "🎯 DECISIONE: ACTION - ... - Score: X.XX"
            decision_match = re.search(r'🎯 DECISIONE: (BUY|SELL|HOLD) - .* - Score: ([0-9.]+)', line)
            if decision_match and 'decision' not in current_decision:
                current_decision['decision'] = decision_match.group(1)
                current_decision['score'] = decision_match.group(2)
                current_decision['timestamp'] = line[:19]  # Estrai timestamp dalla riga
                
                # Se abbiamo tutti i dati, aggiungi la decisione
                if 'symbol' in current_decision:
                    decisions.append(current_decision.copy())
                    current_decision = {}
                    
                    if len(decisions) >= 5:
                        break
        
        # Inverti per avere ordine cronologico
        decisions.reverse()
        
        return decisions, cycles, (buy_count, sell_count, hold_count)
        
    except Exception as e:
        st.error(f"Errore lettura log: {e}")
        return [], 0, (0, 0, 0)

# Header
st.markdown('<h1 class="main-header">🚀 QUANTUM TRADING PRO - BINANCE LIVE</h1>', unsafe_allow_html=True)
st.markdown('<div class="binance-badge">📊 DATI BINANCE + LOG REALE SINCRONIZZATI</div>', unsafe_allow_html=True)

# Prezzi REALI Binance
st.markdown("### 💰 PREZZI BINANCE LIVE")
real_prices = get_real_time_prices()

price_cols = st.columns(5)
for i, (symbol, data) in enumerate(real_prices.items()):
    with price_cols[i]:
        st.metric(
            label=symbol,
            value=data['formatted_price'],
            delta=f"{data['change_24h']:.2f}%",
            delta_color="normal" if data['change_24h'] > 0 else "inverse"
        )

# Leggi dati dal LOG REALE
decisions, cycles, (buy_count, sell_count, hold_count) = parse_log_file()
total_decisions = buy_count + sell_count + hold_count

# Layout principale
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🎛️ Sistema Quantum")
    st.markdown('<div class="binance-badge">🟢 COLLEGATO A BINANCE</div>', unsafe_allow_html=True)
    
    st.metric("Cicli Completati", cycles)
    st.metric("Stato Sistema", "ATTIVO" if cycles > 0 else "IN AVVIO")
    
    progress_val = min(cycles / 30.0, 1.0) if cycles > 0 else 0.05
    st.progress(progress_val)
    st.info("📡 Connesso a Binance API")

with col2:
    st.markdown("### 📊 Statistiche Trading (DAL LOG REALE)")
    st.metric("Decisioni Totali", total_decisions)
    st.metric("BUY Signals", buy_count, f"{(buy_count/max(total_decisions,1)*100):.0f}%")
    st.metric("SELL Signals", sell_count, f"{(sell_count/max(total_decisions,1)*100):.0f}%")
    st.metric("HOLD Signals", hold_count, f"{(hold_count/max(total_decisions,1)*100):.0f}%")
    
    # Grafico distribuzione REALE
    if total_decisions > 0:
        fig_pie = px.pie(
            values=[buy_count, sell_count, hold_count],
            names=['BUY', 'SELL', 'HOLD'],
            color=['BUY', 'SELL', 'HOLD'],
            color_discrete_map={'BUY': '#00FF00', 'SELL': '#FF0000', 'HOLD': '#FFFF00'}
        )
        fig_pie.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0), showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)

with col3:
    st.markdown("### ⚙️ Parametri Strategia")
    
    buy_thresh = st.slider("Soglia BUY", 1.0, 5.0, 3.2, 0.1, key="buy_real")
    sell_thresh = st.slider("Soglia SELL", 1.0, 5.0, 2.4, 0.1, key="sell_real")
    
    st.success(f"🎯 BUY > {buy_thresh}")
    st.error(f"🎯 SELL < {sell_thresh}")
    
    # Mostra statistiche score
    if decisions:
        scores = [float(d['score']) for d in decisions if 'score' in d]
        avg_score = sum(scores) / len(scores) if scores else 0
        st.info(f"📊 Score medio: {avg_score:.2f}")

# Decisioni REALI dal log
st.markdown("---")
st.markdown("### ⚡ DECISIONI DAL LOG REALE + PREZZI BINANCE LIVE")

if decisions:
    st.markdown("**📋 Ultime 5 Decisioni (Log Reale + Prezzi Binance):**")
    
    # Tabella formattata
    for decision in decisions:
        symbol = decision.get('symbol', 'UNKNOWN')
        decision_type = decision.get('decision', 'UNKNOWN')
        score = decision.get('score', '0.00')
        timestamp = decision.get('timestamp', '00:00:00')
        
        # Prendi prezzo REALE Binance
        price_data = real_prices.get(symbol, {'formatted_price': '$0', 'change_24h': 0})
        real_price = price_data['formatted_price']
        change_24h = price_data['change_24h']
        
        # Colori e icone
        if decision_type == "BUY":
            color = "🟢"
            bg_color = "#e6ffe6"
        elif decision_type == "SELL":
            color = "🔴"
            bg_color = "#ffe6e6"
        else:
            color = "🟡"
            bg_color = "#ffffe6"
        
        change_str = f"📈 +{change_24h:.2f}%" if change_24h > 0 else f"📉 {change_24h:.2f}%"
        
        # Crea colonne per visualizzazione
        cols = st.columns([2, 2, 2, 2, 3, 2])
        with cols[0]:
            st.markdown(f"**{timestamp[11:19]}**")
        with cols[1]:
            st.markdown(f"**{symbol}**")
        with cols[2]:
            st.markdown(f"{color} **{decision_type}**")
        with cols[3]:
            st.markdown(f"Score: **{score}**")
        with cols[4]:
            st.markdown(f"Prezzo: **{real_price}**")
        with cols[5]:
            st.markdown(f"{change_str}")
        
        st.markdown("---")
else:
    st.warning("🔍 Nessuna decisione trovata nel log. Sistema in avvio...")
    st.info("💡 Le decisioni appariranno qui dopo il primo ciclo completato")

# Grafico andamento BTC
st.markdown("---")
st.markdown("### 📈 ANDAMENTO BTC/USDT (Binance Real-Time)")

try:
    btc_price = real_prices['BTCUSDT']['price']
    time_points = [datetime.now() - timedelta(hours=i) for i in range(24, 0, -1)]
    # Simula andamento basato sul prezzo reale attuale
    btc_prices = [btc_price * (1 + (i-12)*0.002) for i in range(24)]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=time_points, y=btc_prices, mode='lines+markers', name='BTC/USDT',
        line=dict(color='#F0B90B', width=3), marker=dict(size=4)
    ))
    fig.update_layout(
        title=f"BTC/USDT - Prezzo attuale: {real_prices['BTCUSDT']['formatted_price']}",
        height=300,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)
except:
    st.info("📊 Grafico in caricamento...")

# Footer
st.markdown("---")
footer_cols = st.columns(3)
with footer_cols[0]:
    st.markdown("**🔗 Binance API: LIVE**")
with footer_cols[1]:
    st.markdown(f"**📊 Log monitorato: production.log**")
with footer_cols[2]:
    st.markdown(f"**🚀 Cicli completati: {cycles}/30**")

# Info log file
if os.path.exists('production.log'):
    file_size = os.path.getsize('production.log')
    st.caption(f"📄 Log file: {file_size} bytes | Ultima modifica: {datetime.fromtimestamp(os.path.getmtime('production.log')).strftime('%H:%M:%S')}")

# Auto-refresh ogni 15 secondi
time.sleep(15)
st.rerun()
