import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json
import os
import requests
import io

st.set_page_config(
    page_title="Quantum Trader Live + Export",
    page_icon="🚀",
    layout="wide"
)

# Auto-refresh ogni 30 secondi
st.markdown("""
<meta http-equiv="refresh" content="30">
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
    .export-section {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #4caf50;
        margin: 1rem 0;
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

def convert_df_to_csv(df):
    """Converti DataFrame in CSV per download"""
    return df.to_csv(index=False).encode('utf-8')

def main():
    st.markdown('<h1 class="main-header">🚀 Quantum Trader Live + Data Export</h1>', 
                unsafe_allow_html=True)
    
    dashboard = QuantumDashboard()
    data = dashboard.data
    
    if not data:
        st.error("❌ Nessun dato di trading trovato")
        st.info("Esegui prima: `python3 quantum_trader_top7.py`")
        return
    
    # Sidebar con Fear & Greed
    st.sidebar.title("🔧 Controlli & Export")
    
    current_time = datetime.now().strftime("%H:%M:%S")
    st.sidebar.info(f"🕐 Ultimo aggiornamento: {current_time}")
    st.sidebar.info("🔄 Auto-refresh ogni 30 secondi")
    
    if st.sidebar.button("🔄 Aggiorna Manualmente"):
        st.rerun()
    
    # Calcola metriche
    balance = data.get('balance', 0)
    portfolio = data.get('portfolio', {})
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
            'Asset': symbol,
            'Quantità': quantity,
            'Prezzo_Corrente': current_price,
            'Valore_Corrente': current_value,
            'Costo_Totale': total_cost,
            'Profitto_USD': profit,
            'Profitto_Percentuale': profit_pct
        })
    
    total_value = balance + portfolio_value
    initial_balance = data.get('initial_balance', 200)
    total_profit = total_value - initial_balance
    total_profit_pct = (total_profit / initial_balance) * 100
    
    # Layout principale
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("💰 Cash", f"${balance:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📦 Portfolio", f"${portfolio_value:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            "💎 Totale", 
            f"${total_value:.2f}",
            delta=f"{total_profit:+.2f} ({total_profit_pct:+.1f}%)"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📋 Asset", len(portfolio))
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 📊 SEZIONE PORTFOLIO CON EXPORT
    st.markdown("### 📊 Dettaglio Portfolio")
    
    if portfolio_details:
        # Crea DataFrame per visualizzazione
        portfolio_df_display = pd.DataFrame([
            {
                'Asset': item['Asset'],
                'Quantità': f"{item['Quantità']:.4f}",
                'Prezzo Corrente': f"${item['Prezzo_Corrente']:.4f}",
                'Valore Corrente': f"${item['Valore_Corrente']:.2f}",
                'Costo Totale': f"${item['Costo_Totale']:.2f}",
                'P&L $': f"${item['Profitto_USD']:+.2f}",
                'P&L %': f"{item['Profitto_Percentuale']:+.2f}%"
            }
            for item in portfolio_details
        ])
        
        st.dataframe(portfolio_df_display, use_container_width=True)
        
        # 📥 SEZIONE ESPORTAZIONE PORTFOLIO
        st.markdown('<div class="export-section">', unsafe_allow_html=True)
        st.markdown("### 📥 Esporta Dati Portfolio")
        
        # Crea DataFrame per export (valori numerici puri)
        portfolio_df_export = pd.DataFrame(portfolio_details)
        
        col_export1, col_export2, col_export3 = st.columns(3)
        
        with col_export1:
            # Mostra dati in formato testo copiabile
            st.text_area(
                "📋 Portfolio (Copia & Incolla)",
                portfolio_df_export.to_string(index=False),
                height=200
            )
        
        with col_export2:
            # Download come CSV
            csv_export = convert_df_to_csv(portfolio_df_export)
            st.download_button(
                label="💾 Scarica CSV",
                data=csv_export,
                file_name=f"quantum_portfolio_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
            
            # Mostra dati JSON
            st.download_button(
                label="📊 Scarica JSON",
                data=json.dumps(portfolio_details, indent=2),
                file_name=f"quantum_portfolio_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json"
            )
        
        with col_export3:
            # Statistiche rapide
            st.markdown("**📈 Statistiche Portfolio:**")
            total_invested = sum(item['Costo_Totale'] for item in portfolio_details)
            total_current = sum(item['Valore_Corrente'] for item in portfolio_details)
            avg_profit_pct = sum(item['Profitto_Percentuale'] for item in portfolio_details) / len(portfolio_details)
            
            st.write(f"💰 Investito: ${total_invested:.2f}")
            st.write(f"📊 Valore Attuale: ${total_current:.2f}")
            st.write(f"🎯 Profitto Medio: {avg_profit_pct:+.2f}%")
            st.write(f"📦 Numero Asset: {len(portfolio_details)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        st.info("💼 Nessun asset nel portfolio")
    
    # 📋 SEZIONE STORICO TRADE CON EXPORT
    st.markdown("### 📋 Storico Trade")
    
    trade_history = data.get('trade_history', [])
    if trade_history:
        # Prendi ultimi 15 trade
        recent_trades = trade_history[-15:]
        
        # Crea DataFrame per visualizzazione
        trade_df_display = pd.DataFrame([
            {
                'Data': trade.get('timestamp', '')[:16],
                'Asset': trade.get('symbol', ''),
                'Azione': f"{'🟢' if trade.get('action') == 'BUY' else '🔴'} {trade.get('action', '')}",
                'Quantità': f"{trade.get('quantity', 0):.4f}",
                'Prezzo': f"${trade.get('price', 0):.4f}",
                'Importo': f"${trade.get('amount', 0):.2f}",
                'Profitto': f"${trade.get('profit', 0):+.2f}" if 'profit' in trade else '-'
            }
            for trade in recent_trades
        ])
        
        st.dataframe(trade_df_display, use_container_width=True)
        
        # 📥 SEZIONE ESPORTAZIONE STORICO
        st.markdown('<div class="export-section">', unsafe_allow_html=True)
        st.markdown("### 📥 Esporta Storico Trade")
        
        # Crea DataFrame per export (valori puri)
        trade_df_export = pd.DataFrame([
            {
                'timestamp': trade.get('timestamp', ''),
                'symbol': trade.get('symbol', ''),
                'action': trade.get('action', ''),
                'quantity': trade.get('quantity', 0),
                'price': trade.get('price', 0),
                'amount': trade.get('amount', 0),
                'profit': trade.get('profit', 0) if 'profit' in trade else 0,
                'profit_pct': trade.get('profit_pct', 0) if 'profit_pct' in trade else 0
            }
            for trade in recent_trades
        ])
        
        col_trade1, col_trade2, col_trade3 = st.columns(3)
        
        with col_trade1:
            # Mostra dati in formato testo copiabile
            st.text_area(
                "📋 Storico Trade (Copia & Incolla)",
                trade_df_export.to_string(index=False),
                height=200
            )
        
        with col_trade2:
            # Download come CSV
            csv_trades = convert_df_to_csv(trade_df_export)
            st.download_button(
                label="💾 Scarica CSV Trade",
                data=csv_trades,
                file_name=f"quantum_trades_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
            
            # Download JSON
            st.download_button(
                label="📊 Scarica JSON Trade",
                data=json.dumps(recent_trades, indent=2),
                file_name=f"quantum_trades_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json"
            )
        
        with col_trade3:
            # Statistiche trade
            st.markdown("**📈 Statistiche Trade:**")
            total_trades = len(recent_trades)
            buy_trades = len([t for t in recent_trades if t.get('action') == 'BUY'])
            sell_trades = len([t for t in recent_trades if t.get('action') == 'SELL'])
            total_profit = sum(t.get('profit', 0) for t in recent_trades if 'profit' in t)
            
            st.write(f"📊 Trade Totali: {total_trades}")
            st.write(f"🟢 Acquisti: {buy_trades}")
            st.write(f"🔴 Vendite: {sell_trades}")
            st.write(f"💰 Profitto Trade: ${total_profit:+.2f}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        st.info("📝 Nessun trade ancora eseguito")
    
    # 📄 SEZIONE ESPORTAZIONE COMPLETA STATO
    st.markdown("### 📄 Esportazione Completa Sistema")
    
    col_full1, col_full2 = st.columns(2)
    
    with col_full1:
        if st.button("📋 Copia Stato Completo (JSON)"):
            full_state = json.dumps(data, indent=2)
            st.text_area("Stato Completo Sistema", full_state, height=300)
    
    with col_full2:
        if st.button("💾 Scarica Backup Completo"):
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'portfolio': portfolio_details,
                'trade_history': trade_history,
                'summary': {
                    'balance': balance,
                    'portfolio_value': portfolio_value,
                    'total_value': total_value,
                    'total_profit': total_profit,
                    'total_profit_pct': total_profit_pct,
                    'assets_count': len(portfolio)
                }
            }
            
            st.download_button(
                label="📦 Scarica Backup JSON",
                data=json.dumps(backup_data, indent=2),
                file_name=f"quantum_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()
