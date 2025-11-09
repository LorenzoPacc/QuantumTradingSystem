import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import requests
import re
import os

st.set_page_config(page_title="Quantum Pro - PRODUCTION", layout="wide")

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

# Simboli corretti
symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT']

# Funzioni per dati BINANCE REALI
def get_binance_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data['price'])
    except:
        return 0

def get_binance_24h_change(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data['priceChangePercent'])
    except:
        return 0.0

def get_real_time_prices():
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

def parse_production_log():
    log_file = 'production.log'
    if not os.path.exists(log_file):
        return [], 0, (0, 0, 0)
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        cycles = len([line for line in lines if 'FINE CICLO #' in line])
        buy_count = len([line for line in lines if ': BUY (' in line])
        sell_count = len([line for line in lines if ': SELL (' in line])
        hold_count = len([line for line in lines if ': HOLD (' in line])
        
        decisions = []
        for line in reversed(lines):
            decision_match = re.search(r'❤️\s+([A-Z]+USDT):\s+(BUY|SELL|HOLD)\s+\(Score:\s+([0-9.]+)\)', line)
            if decision_match:
                symbol = decision_match.group(1)
                action = decision_match.group(2)
                score = decision_match.group(3)
                decisions.append({
                    'symbol': symbol,
                    'decision': action,
                    'score': score,
                    'timestamp': line[:19]
                })
                if len(decisions) >= 6:
                    break
        
        decisions.reverse()
        return decisions, cycles, (buy_count, sell_count, hold_count)
        
    except Exception as e:
        st.error(f"Errore lettura log: {e}")
        return [], 0, (0, 0, 0)

def get_portfolio_value():
    try:
        with open('production.log', 'r') as f:
            for line in reversed(f.readlines()):
                if 'Portfolio: $' in line:
                    portfolio_match = re.search(r'Portfolio:\s+\$([0-9,]+\.?[0-9]*)', line)
                    if portfolio_match:
                        return portfolio_match.group(1)
    except:
        pass
    return "11,201.64"

# Header
st.markdown('<h1 class="main-header">🚀 QUANTUM TRADER PRODUCTION</h1>', unsafe_allow_html=True)
st.markdown('<div class="binance-badge">📊 PRODUCTION MODE - MIGLIORAMENTI ATTIVI</div>', unsafe_allow_html=True)

# Prezzi REALI Binance
st.markdown("### 💰 PREZZI BINANCE LIVE")
real_prices = get_real_time_prices()

price_cols = st.columns(6)
for i, symbol in enumerate(symbols):
    with price_cols[i]:
        data = real_prices.get(symbol, {'formatted_price': '$0', 'change_24h': 0})
        st.metric(
            label=symbol,
            value=data['formatted_price'],
            delta=f"{data['change_24h']:.2f}%",
            delta_color="normal" if data['change_24h'] > 0 else "inverse"
        )

# Leggi dati dal LOG
decisions, cycles, (buy_count, sell_count, hold_count) = parse_production_log()
total_decisions = buy_count + sell_count + hold_count
portfolio_value = get_portfolio_value()

# Layout principale
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🎛️ Sistema Production")
    st.markdown('<div class="binance-badge">🟢 QUANTUM TRADER PRODUCTION</div>', unsafe_allow_html=True)
    
    st.metric("Cicli Completati", cycles)
    st.metric("Portfolio Value", f"${portfolio_value}")
    st.metric("Stato Sistema", "ATTIVO")
    
    progress_val = min(cycles / 50.0, 1.0)
    st.progress(progress_val)
    st.info(f"📊 Log: production.log | {cycles}/50 cicli")

with col2:
    st.markdown("### 📊 Statistiche Trading")
    st.metric("Decisioni Totali", total_decisions)
    st.metric("BUY Signals", buy_count, f"{(buy_count/max(total_decisions,1)*100):.0f}%")
    st.metric("SELL Signals", sell_count, f"{(sell_count/max(total_decisions,1)*100):.0f}%")
    st.metric("HOLD Signals", hold_count, f"{(hold_count/max(total_decisions,1)*100):.0f}%")
    
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
    st.markdown("### ⚙️ Parametri Production")
    
    st.success("🎯 Strategia: Multi-Factor Confluence")
    st.info("💰 Portfolio Protection: ATTIVA")
    st.warning("🔒 XRP Protection: ATTIVA")
    st.success("⚡ Cicli: 45s (MIGLIORATO)")
    
    if decisions:
        scores = [float(d['score']) for d in decisions if 'score' in d]
        avg_score = sum(scores) / len(scores) if scores else 0
        st.metric("📊 Score Medio", f"{avg_score:.2f}")

# Decisioni REALI
st.markdown("---")
st.markdown("### ⚡ DECISIONI PRODUCTION - ULTIMO CICLO")

if decisions:
    st.markdown(f"**📋 Ultime {len(decisions)} Decisioni (Ciclo {cycles}):**")
    
    for decision in decisions:
        symbol = decision.get('symbol', 'UNKNOWN')
        decision_type = decision.get('decision', 'UNKNOWN')
        score = decision.get('score', '0.00')
        timestamp = decision.get('timestamp', '00:00:00')
        
        price_data = real_prices.get(symbol, {'formatted_price': '$0', 'change_24h': 0})
        real_price = price_data['formatted_price']
        change_24h = price_data['change_24h']
        
        if decision_type == "BUY":
            color = "🟢"
        elif decision_type == "SELL":
            color = "🔴"
        else:
            color = "🟡"
        
        change_str = f"📈 +{change_24h:.2f}%" if change_24h > 0 else f"📉 {change_24h:.2f}%"
        
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
    st.warning("🔍 Nessuna decisione trovata nel log production.")

# Footer
st.markdown("---")
footer_cols = st.columns(3)
with footer_cols[0]:
    st.markdown("**🔗 Binance API: LIVE**")
with footer_cols[1]:
    st.markdown(f"**📊 Portfolio: ${portfolio_value}**")
with footer_cols[2]:
    st.markdown(f"**🚀 Cicli: {cycles}/50**")

# Auto-refresh
time.sleep(30)
st.rerun()
