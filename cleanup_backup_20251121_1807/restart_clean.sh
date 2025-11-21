#!/bin/bash
cd ~/trading_project/QuantumTradingSystem
pkill -f "quantum_trader_ultimate_final.py"
pkill -f "streamlit run"
sleep 3
source venv/bin/activate
nohup python3 quantum_trader_ultimate_final.py > trader.log 2>&1 &
nohup streamlit run dashboard_finale.py --server.port=8502 > dashboard.log 2>&1 &
sleep 5
echo "✅ Sistema riavviato!"
pgrep -f "quantum_trader_ultimate_final.py" && echo "🤖 Trader: ✅" || echo "🤖 Trader: ❌"
pgrep -f "streamlit run" && echo "📊 Dashboard: ✅" || echo "📊 Dashboard: ❌"
