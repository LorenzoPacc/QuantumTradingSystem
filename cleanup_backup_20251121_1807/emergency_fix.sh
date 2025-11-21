#!/bin/bash
cd ~/trading_project/QuantumTradingSystem
pkill -9 -f "quantum_trader_ultimate_final.py"
pkill -9 -f "streamlit run"
sleep 3
source venv/bin/activate
nohup python3 quantum_trader_ultimate_final.py > trader.log 2>&1 &
nohup streamlit run dashboard_finale.py --server.port=8502 > dashboard.log 2>&1 &
sleep 8
echo "✅ Emergency restart completo!"
pgrep -f "quantum_trader_ultimate_final.py" && echo "🤖 Trader: ✅" || echo "🤖 Trader: ❌"
pgrep -f "streamlit run" && echo "📊 Dashboard: ✅" || echo "📊 Dashboard: ❌"
echo "🌐 Dashboard: http://localhost:8502"
