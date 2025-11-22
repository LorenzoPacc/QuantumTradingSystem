#!/usr/bin/env python3
"""
QUANTUM BOT - VERSIONE STABILE E TESTATA
QuantumTraderV21 con strategia Fear & Greed 16-28
"""
from quantum_v3_enhanced import QuantumTraderV21
import time

trader = QuantumTraderV21(dry_run=True)

print("🚀 QUANTUM BOT V2.1 - STRATEGIA 16-28 ATTIVA")
print("🎯 Compra SOLO quando Fear & Greed è tra 16-28")
print(f"💰 Cash: ${trader.cash_balance:.2f}")
print("🔄 LOOP START\n")

cycle = 0
while True:
    try:
        cycle += 1
        print(f"🎯 CYCLE {cycle} - {time.strftime('%H:%M:%S')}")

        trader.run_cycle()

        print(f"✅ Done\n")
        time.sleep(600)

    except KeyboardInterrupt:
        print("\n🛑 STOP")
        break
