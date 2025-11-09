from quantum_ultimate_fixed import QuantumTraderUltimateFixed
import time

print("🧪 TEST STOP LOSS CON $50...")
trader = QuantumTraderUltimateFixed(50)

print("🎯 Avvio 3 cicli di test...")
for i in range(3):
    print(f"\\n🔁 Ciclo {i+1}")
    trader.execute_trading_cycle()
    time.sleep(2)

print("\\n✅ TEST COMPLETATO")
print(f"💰 Cash finale: \${trader.cash_balance:.2f}")
print(f"📈 Posizioni: {len(trader.portfolio)}")
