import threading
import time
from quantum_ultimate_fixed import QuantumTraderUltimateFixed
from quantum_dashboard_compatible import start_compatible_dashboard
import json

print("🚀 QUANTUM SYSTEM - AVVIO COMPLETO")

# Carica portfolio esistente
try:
    with open('portfolio_backup.json', 'r') as f:
        saved_data = json.load(f)
    
    trader = QuantumTraderUltimateFixed(200)
    trader.cash_balance = saved_data['cash_balance']
    trader.portfolio = saved_data['portfolio']
    trader.cycle_count = saved_data.get('cycle_count', 115)
    
    print("✅ PORTFOLIO CARICATO")
    print(f"💰 Valore: ${trader.get_portfolio_value():.2f}")
    print(f"💸 Cash: ${trader.cash_balance:.2f}")
    print(f"📈 Posizioni: {len(trader.portfolio)}")
    
except FileNotFoundError:
    print("🆕 NUOVO TRADER")
    trader = QuantumTraderUltimateFixed(200)

# Avvia dashboard IN UN THREAD con il trader connesso
def start_dashboard():
    print("📊 AVVIO DASHBOARD...")
    dashboard = start_compatible_dashboard(trading_engine=trader, port=8081)

dashboard_thread = threading.Thread(target=start_dashboard)
dashboard_thread.daemon = True
dashboard_thread.start()

print("⏳ Attendere avvio dashboard...")
time.sleep(5)

print("✅ DASHBOARD PRONTA: http://localhost:8081")
print("🎯 BOT ATTIVO con Stop Loss -4% e Take Profit +8%")
print("=" * 60)

# Avvia trading
trader.run_continuous_trading(cycles=1000, delay=600)
