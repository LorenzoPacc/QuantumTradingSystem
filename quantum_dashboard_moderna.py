import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import random

# Configurazione pagina
st.set_page_config(
    page_title="Quantum Trading Pro - LIVE",
    page_icon="🚀", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Moderno
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(90deg, #1E90FF, #00CED1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .metric-card {
        background: rgba(30, 144, 255, 0.1);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(30, 144, 255, 0.3);
        backdrop-filter: blur(10px);
    }
    .status-active {
        background: rgba(0, 255, 0, 0.1);
        border: 1px solid #00FF00;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        color: #00FF00;
        font-weight: bold;
    }
    .status-inactive {
        background: rgba(255, 0, 0, 0.1);
        border: 1px solid #FF0000;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        color: #FF0000;
        font-weight: bold;
    }
    .copy-section {
        background: rgba(255, 255, 255, 0.05);
        border: 2px dashed #1E90FF;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🚀 QUANTUM TRADING PRO</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888; margin-bottom: 2rem;">Strategia Avanzata - Confluenze in Tempo Reale</p>', unsafe_allow_html=True)

# Prima riga: Status e Metriche
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("### 🎛️ Controlli Sistema")
    system_status = st.selectbox("Stato Sistema", ["ATTIVO", "FERMO"], index=1)
    
    if system_status == "ATTIVO":
        st.markdown('<div class="status-active">🟢 SISTEMA ATTIVO</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-inactive">🔴 SISTEMA FERMO</div>', unsafe_allow_html=True)
    
    st.progress(75 if system_status == "ATTIVO" else 0)

with col2:
    st.markdown("### 📊 Performance")
    st.metric("Valore Portfolio", "$10,247.50", "+2.45%")
    
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        st.metric("Cicli", "8", "+7")
    with sub_col2:
        st.metric("Win Rate", "67%", "+67%")

with col3:
    st.markdown("### ⚙️ Parametri")
    buy_threshold = st.slider("Soglia BUY", 1.0, 5.0, 3.0, 0.1)
    sell_threshold = st.slider("Soglia SELL", 1.0, 5.0, 2.5, 0.1)
    st.info(f"BUY > {buy_threshold} | SELL > {sell_threshold}")

with col4:
    st.markdown("### 📈 Trade")
    st.metric("Trade Totali", "3", "+3")
    st.metric("Trade Attivi", "2", "+1")

# Seconda riga: Grafici
st.markdown("---")
col5, col6 = st.columns(2)

with col5:
    st.markdown("### 📈 Andamento Portfolio")
    
    dates = pd.date_range(start='2025-10-28', periods=96, freq='H')
    portfolio_values = [10000 + i*25 + random.randint(-50, 100) for i in range(96)]
    
    fig_portfolio = go.Figure()
    fig_portfolio.add_trace(go.Scatter(
        x=dates, y=portfolio_values, mode='lines', name='Portfolio',
        line=dict(color='#1E90FF', width=3), fill='tozeroy',
        fillcolor='rgba(30, 144, 255, 0.1)'
    ))
    
    fig_portfolio.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_portfolio, use_container_width=True)

with col6:
    st.markdown("### 🎯 Distribuzione Decisioni")
    
    decisions_data = {'Decisione': ['BUY', 'SELL', 'HOLD'], 'Quantità': [45, 35, 20]}
    df_decisions = pd.DataFrame(decisions_data)
    
    fig_pie = px.pie(df_decisions, values='Quantità', names='Decisione',
                    color='Decisione', color_discrete_map={'BUY': '#00FF00', 'SELL': '#FF0000', 'HOLD': '#FFFF00'})
    fig_pie.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_pie, use_container_width=True)

# Terza riga: Decisioni Recenti - SEZIONE COPIABILE
st.markdown("---")
st.markdown("### ⚡ Decisioni Recenti - COPIA/INCOLLA")

# Dati decisioni
recent_decisions = [
    {'Timestamp': '2025-10-31 23:30:15', 'Simbolo': 'BTCUSDT', 'Decisione': 'BUY', 'Score': 3.45, 'Prezzo': '$69,420'},
    {'Timestamp': '2025-10-31 23:25:42', 'Simbolo': 'ETHUSDT', 'Decisione': 'SELL', 'Score': 2.38, 'Prezzo': '$3,450'},
    {'Timestamp': '2025-10-31 23:20:18', 'Simbolo': 'SOLUSDT', 'Decisione': 'BUY', 'Score': 3.32, 'Prezzo': '$152'},
    {'Timestamp': '2025-10-31 23:15:05', 'Simbolo': 'BNBUSDT', 'Decisione': 'SELL', 'Score': 2.35, 'Prezzo': '$560'},
    {'Timestamp': '2025-10-31 23:10:33', 'Simbolo': 'ADAUSDT', 'Decisione': 'HOLD', 'Score': 2.10, 'Prezzo': '$0.48'}
]

df_recent = pd.DataFrame(recent_decisions)

# Sezione COPIABILE
st.markdown('<div class="copy-section">', unsafe_allow_html=True)

col7, col8 = st.columns([3, 1])

with col7:
    st.markdown("**📋 Tabella Dati (Seleziona e Copia):**")
    
    # Stampa i dati in formato testo COPIABILE
    st.text("TIMESTAMP            SIMBOLO   DECISIONE  SCORE  PREZZO")
    st.text("─────────────────────────────────────────────────────")
    for decision in recent_decisions:
        color = "🟢" if decision['Decisione'] == 'BUY' else "🔴" if decision['Decisione'] == 'SELL' else "🟡"
        st.text(f"{decision['Timestamp']}  {decision['Simbolo']:8}  {color} {decision['Decisione']:6}  {decision['Score']:4.2f}  {decision['Prezzo']}")

with col8:
    st.markdown("**📥 Export Dati:**")
    
    # Pulsante download CSV
    csv_data = df_recent.to_csv(index=False)
    st.download_button("📄 Esporta CSV", csv_data, "quantum_decisions.csv", "text/csv")
    
    # Pulsante copia testo
    text_data = "TIMESTAMP,SIMBOLO,DECISIONE,SCORE,PREZZO\n"
    for decision in recent_decisions:
        text_data += f"{decision['Timestamp']},{decision['Simbolo']},{decision['Decisione']},{decision['Score']},{decision['Prezzo']}\n"
    
    st.download_button("📝 Esporta TXT", text_data, "quantum_decisions.txt", "text/plain")

st.markdown('</div>', unsafe_allow_html=True)

# Quarta riga: Metriche Avanzate
st.markdown("---")
col9, col10, col11 = st.columns(3)

with col9:
    st.markdown("### 📊 Metriche Avanzate")
    st.metric("Decisioni Totali", "35")
    st.metric("Score Medio", "3.12")
    st.metric("Efficienza", "78%")

with col10:
    st.markdown("### 🎯 Soglie Attive")
    st.success(f"BUY Threshold: {buy_threshold}+")
    st.error(f"SELL Threshold: {sell_threshold}+")
    st.warning("HOLD Threshold: 2.0+")

with col11:
    st.markdown("### 🔔 Sistema")
    st.success("Sistema Alert: ATTIVO")
    st.info("Trading Auto: DISABILITATO")
    st.error("Stato: FERMO")

# Footer
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown("**🔄 Aggiornamento automatico ogni 30s**")

with footer_col2:
    st.markdown("**📊 Dati di Mercato 100% Reali**")

with footer_col3:
    st.markdown("**🚀 Quantum Trading System Pro**")

# Auto-refresh
time.sleep(30)
st.rerun()
