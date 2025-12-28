#!/usr/bin/env python3
import time
import sys
from datetime import datetime
from quantum_v31_wrapper import QuantumTraderV31

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

print("=" * 60)
print(f"🚀 QUANTUM BOT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

trader = QuantumTraderV31(dry_run=True)
print(f"💰 Cash: ${trader.cash_balance:.2f}")
print(f"📊 Positions: {len(trader.portfolio)}")
print("🔄 MAIN LOOP STARTED")

cycle = 0
while True:
    try:
        cycle += 1
        print(f"\n🎯 CYCLE {cycle} - {datetime.now().strftime('%H:%M:%S')}")
        trader.run_cycle()
        print(f"✅ Cycle {cycle} done | Next: {datetime.fromtimestamp(time.time() + 600).strftime('%H:%M:%S')}")
        time.sleep(600)
    except KeyboardInterrupt:
        print("\n🛑 SHUTDOWN")
        break
    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(60)
