from quantum_ultimate_fixed import QuantumTraderUltimateFixed
import json
import time

print("🚀 QUANTUM BOT - AVVIO CON PORTFOLIO")

try:
    # Prova a caricare il portfolio salvato
    with open('portfolio_backup.json', 'r') as f:
        saved_data = json.load(f)
    
    # Crea trader e ripristina stato
    trader = QuantumTraderUltimateFixed(200)
    trader.cash_balance = saved_data['cash_balance']
    trader.portfolio = saved_data['portfolio']
    trader.cycle_count = saved_data.get('cycle_count', 0)
    
    print("✅ PORTFOLIO CARICATO!")
    print(f"💰 Valore: ${trader.get_portfolio_value():.2f}")
    print(f"💸 Cash: ${trader.cash_balance:.2f}")
    print(f"📈 Posizioni: {len(trader.portfolio)}")
    print(f"🔄 Riprendo dal ciclo: {trader.cycle_count + 1}")
    
except FileNotFoundError:
    print("❌ Backup non trovato, nuovo trader")
    trader = QuantumTraderUltimateFixed(200)

print("\n🎯 STOP LOSS ATTIVO: -4%")
print("🎯 TAKE PROFIT ATTIVO: +8%")
print("⏰ Intervallo: 600 secondi")
print("=" * 50)

# Avvia trading
trader.run_continuous_trading(cycles=1000, delay=600)
