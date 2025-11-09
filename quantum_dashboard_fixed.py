import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json
import os
import requests

st.set_page_config(
    page_title="Quantum Trader Final Real",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .profit-positive { color: #00ff00; font-weight: bold; }
    .profit-negative { color: #ff0000; font-weight: bold; }
    .copy-section {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #dee2e6;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

class QuantumDashboard:
    def __init__(self):
        self.data = self.load_trading_data()
    
    def load_trading_data(self):
        """Carica i dati di trading"""
        try:
            if os.path.exists('paper_trading_state.json'):
                with open('paper_trading_state.json', 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            st.error(f"Errore caricamento dati: {e}")
            return None
    
    def get_current_prices(self, symbols):
        """Ottieni prezzi correnti"""
        prices = {}
        for symbol in symbols:
            try:
                url = "https://api.binance.com/api/v3/ticker/price"
                params = {'symbol': symbol}
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
                prices[symbol] = float(data['price'])
            except:
                prices[symbol] = 0.0
        return prices
    
    def get_fear_greed_index(self):
        """Ottieni Fear & Greed Index"""
        try:
            url = "https://api.alternative.me/fng/"
            response = requests.get(url, timeout=10)
            data = response.json()
            return int(data['data'][0]['value'])
        except:
            return 50

def main():
    st.markdown('<h1 class="main-header">🚀 Quantum Trader Final Real</h1>', 
                unsafe_allow_html=True)
    
    dashboard = QuantumDashboard()
    data = dashboard.data
    
    if not data:
        st.error("❌ Nessun dato di trading trovato. Avvia prima il trader.")
        st.info("Esegui: `python3 quantum_trader_final_real.py`")
        return
    
    # Sidebar con controlli
    st.sidebar.title("🔧 Controlli")
    
    if st.sidebar.button("🔄 Aggiorna Dati"):
        st.rerun()
    
    if st.sidebar.button("🗑️ Reset a $200"):
        if os.path.exists('paper_trading_state.json'):
            os.remove('paper_trading_state.json')
        st.rerun()
    
    # Fear & Greed Index in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 😨 Fear & Greed Index")
    fgi = dashboard.get_fear_greed_index()
    
    if fgi < 25:
        st.sidebar.error(f"**EXTREME FEAR**: {fgi}")
        st.sidebar.info("🎯 Opportunità di acquisto")
    elif fgi < 45:
        st.sidebar.warning(f"**FEAR**: {fgi}")
    elif fgi < 55:
        st.sidebar.info(f"**NEUTRAL**: {fgi}")
    elif fgi < 75:
        st.sidebar.warning(f"**GREED**: {fgi}")
    else:
        st.sidebar.error(f"**EXTREME GREED**: {fgi}")
        st.sidebar.warning("⚠️ Attenzione al mercato")
    
    # Calcola metriche
    balance = data.get('balance', 0)
    portfolio = data.get('portfolio', {})
    
    # Calcola valore portfolio corrente
    symbols = list(portfolio.keys())
    current_prices = dashboard.get_current_prices(symbols)
    
    portfolio_value = 0
    portfolio_details = []
    
    for symbol, asset in portfolio.items():
        current_price = current_prices.get(symbol, asset.get('entry_price', 0))
        quantity = asset.get('quantity', 0)
        current_value = quantity * current_price
        total_cost = asset.get('total_cost', 0)
        profit = current_value - total_cost
        profit_pct = (profit / total_cost * 100) if total_cost > 0 else 0
        
        portfolio_value += current_value
        portfolio_details.append({
            'symbol': symbol,
            'quantity': quantity,
            'current_price': current_price,
            'current_value': current_value,
            'total_cost': total_cost,
            'profit': profit,
            'profit_pct': profit_pct
        })
    
    total_value = balance + portfolio_value
    initial_balance = 200.0
    total_profit = total_value - initial_balance
    total_profit_pct = (total_profit / initial_balance) * 100
    
    # Layout principale - Metriche
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("💰 Cash Disponibile", f"${balance:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📦 Valore Portfolio", f"${portfolio_value:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        profit_class = "profit-positive" if total_profit >= 0 else "profit-negative"
        st.metric(
            "💎 Totale Account", 
            f"${total_value:.2f}",
            delta=f"{total_profit:+.2f} ({total_profit_pct:+.1f}%)"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📋 Asset in Portfolio", len(portfolio))
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Dettaglio Portfolio - ORIGINALE + COPIA
    st.markdown("### 📊 Dettaglio Portfolio")
    
    if portfolio_details:
        # TABELLA ORIGINALE (non copiabile)
        portfolio_df_data = []
        for item in portfolio_details:
            profit_color = "🟢" if item['profit'] >= 0 else "🔴"
            portfolio_df_data.append({
                'Asset': item['symbol'],
                'Quantità': f"{item['quantity']:.4f}",
                'Prezzo Corrente': f"${item['current_price']:.4f}",
                'Valore Corrente': f"${item['current_value']:.2f}",
                'Costo Totale': f"${item['total_cost']:.2f}",
                'P&L $': f"{profit_color} ${item['profit']:+.2f}",
                'P&L %': f"{item['profit_pct']:+.2f}%"
            })
        
        portfolio_df = pd.DataFrame(portfolio_df_data)
        st.dataframe(portfolio_df, use_container_width=True)
        
        # 📋 SEZIONE COPIA DATI (SOTTO la tabella)
        st.markdown("### 📋 Copia Dati Portfolio")
        st.markdown('<div class="copy-section">', unsafe_allow_html=True)
        
        # Crea testo formattato per copia
        portfolio_text = "ASSET | QUANTITÀ | PREZZO CORRENTE | VALORE CORRENTE | COSTO TOTALE | P&L %\n"
        portfolio_text += "------|----------|----------------|-----------------|-------------|-------\n"
        for item in portfolio_details:
            portfolio_text += f"{item['symbol']} | {item['quantity']:.6f} | ${item['current_price']:.4f} | ${item['current_value']:.2f} | ${item['total_cost']:.2f} | {item['profit_pct']:+.2f}%\n"
        
        st.code(portfolio_text, language="text")
        st.info("💡 **Clicca nel box sopra → Premi Ctrl+A (seleziona tutto) → Premi Ctrl+C (copia)**")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Grafico a torta portfolio
        if len(portfolio_details) > 0:
            fig_pie = go.Figure(data=[go.Pie(
                labels=[item['symbol'] for item in portfolio_details],
                values=[item['current_value'] for item in portfolio_details],
                hole=.3,
                marker_colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
            )])
            fig_pie.update_layout(title="Distribuzione Portfolio")
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("💼 Nessun asset nel portfolio")
    
    # Storico Trade - ORIGINALE + COPIA
    st.markdown("### 📋 Storico Trade")
    
    trade_history = data.get('trade_history', [])
    if trade_history:
        # Prendi ultimi 15 trade
        recent_trades = trade_history[-15:]
        
        # TABELLA ORIGINALE (non copiabile)
        trade_df_data = []
        for trade in recent_trades:
            action_emoji = "🟢" if trade.get('action') == 'BUY' else "🔴"
            trade_df_data.append({
                'Data': trade.get('timestamp', '')[:16],
                'Asset': trade.get('symbol', ''),
                'Azione': f"{action_emoji} {trade.get('action', '')}",
                'Quantità': f"{trade.get('quantity', 0):.4f}",
                'Prezzo': f"${trade.get('price', 0):.4f}",
                'Importo': f"${trade.get('amount', 0):.2f}",
                'Profitto': f"${trade.get('profit', 0):+.2f}" if 'profit' in trade else '-'
            })
        
        trade_df = pd.DataFrame(trade_df_data)
        st.dataframe(trade_df, use_container_width=True)
        
        # 📋 SEZIONE COPIA DATI (SOTTO la tabella)
        st.markdown("### 📋 Copia Storico Trade")
        st.markdown('<div class="copy-section">', unsafe_allow_html=True)
        
        # Crea testo formattato per copia
        trades_text = "DATA | ASSET | AZIONE | QUANTITÀ | PREZZO | IMPORTO | PROFITTO\n"
        trades_text += "-----|-------|--------|----------|--------|---------|----------\n"
        for trade in recent_trades:
            action = trade.get('action', '')
            action_display = "🟢 BUY" if action == 'BUY' else "🔴 SELL"
            trades_text += f"{trade.get('timestamp', '')[:16]} | {trade.get('symbol', '')} | {action_display} | {trade.get('quantity', 0):.6f} | ${trade.get('price', 0):.4f} | ${trade.get('amount', 0):.2f} | ${trade.get('profit', 0):.2f}\n"
        
        st.code(trades_text, language="text")
        st.info("💡 **Clicca nel box sopra → Premi Ctrl+A (seleziona tutto) → Premi Ctrl+C (copia)**")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Grafico performance
        if len(trade_history) > 1:
            try:
                cumulative_profit = 0
                dates = []
                profits = []
                
                for trade in trade_history:
                    if 'profit' in trade and trade['profit']:
                        cumulative_profit += trade['profit']
                        dates.append(trade.get('timestamp', '')[:10])
                        profits.append(cumulative_profit)
                
                if profits:
                    fig_profit = go.Figure()
                    fig_profit.add_trace(go.Scatter(
                        x=dates, y=profits,
                        mode='lines+markers',
                        name='Profitto Cumulativo',
                        line=dict(color='#00ff00', width=3)
                    ))
                    fig_profit.update_layout(
                        title='Performance Trading - Profitto Cumulativo',
                        xaxis_title='Data',
                        yaxis_title='Profitto ($)'
                    )
                    st.plotly_chart(fig_profit, use_container_width=True)
            except Exception as e:
                st.warning(f"Impossibile generare grafico performance: {e}")
    else:
        st.info("📝 Nessun trade ancora eseguito")
    
    # Informazioni di sistema
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Info Sistema")
    st.sidebar.info(f"**Ultimo aggiornamento**: {datetime.now().strftime('%H:%M:%S')}")
    
    if os.path.exists('quantum_trader.log'):
        log_size = os.path.getsize('quantum_trader.log') / 1024
        st.sidebar.info(f"**Dimensione log**: {log_size:.1f} KB")

if __name__ == "__main__":
    main()
