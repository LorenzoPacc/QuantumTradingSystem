#!/usr/bin/env python3
from quantum_v31_wrapper import QuantumTraderV31
import time

trader = QuantumTraderV31(dry_run=True)

print("🚀 QUANTUM SIMPLE FIXED")
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
