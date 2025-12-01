#!/usr/bin/env python3
"""
QUANTUM BOT - DAY TRADING OPTIMIZED V3
QuantumTraderV21 con strategia Fear & Greed + Smart Improvements
Ciclo: 5 minuti (invece di 10) per day trading
"""
from quantum_v3_enhanced import QuantumTraderV21
import time

trader = QuantumTraderV21(dry_run=True)

print("🚀 QUANTUM BOT V3 - DAY TRADING OPTIMIZED")
print("🎯 Timeframe: 5m, 15m, 1h - Ciclo: 5 minuti")
print("📊 Smart Improvements: ATTIVI")
print(f"💰 Cash: ${trader.cash_balance:.2f}")
print("🔄 LOOP START\n")

cycle = 0
while True:
    try:
        cycle += 1
        print(f"🎯 CYCLE {cycle} - {time.strftime('%H:%M:%S')}")

        trader.run_cycle()

        print(f"✅ Done\n")
        time.sleep(300)  # 5 MINUTI (300 secondi)

    except KeyboardInterrupt:
        print("\n🛑 STOP")
        break

# =============================================================================
# 🎯 TELEGRAM NOTIFICATIONS
# =============================================================================
try:
    from telegram_pro import telegram
    if telegram.enabled:
        print("✅ Telegram Notifications: ATTIVO")
        telegram.send("🤖 <b>Quantum Bot V3 Avviato</b>\n\n✅ Day Trading Mode\n🎯 Ciclo: 5 minuti\n📊 Smart Improvements: ON", important=False)
    else:
        print("⚠️  Telegram: Configura TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID")
except Exception as e:
    print("⚠️  Telegram: Errore -", str(e))
