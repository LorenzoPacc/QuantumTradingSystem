#!/bin/bash
echo "🔄 Sincronizzazione Sistema Quantum Trading..."

# Assicurati che bot e dashboard usino stesso DB
export QUANTUM_DB="quantum_unified.db"

# Avvia il bot
echo "🚀 Avvio Quantum Trader..."
python3 scripts/quantum_trader_macro_confluence.py --db $QUANTUM_DB &

# Aspetta che il database sia pronto
sleep 3

# Avvia la dashboard
echo "📊 Avvio Dashboard..."
streamlit run scripts/dashboard_with_trades.py --server.port=8501

