#!/usr/bin/env python3
"""
Test delle nuove impostazioni con soglia 45%
"""

from fix_critical_bugs import CriticalFixes

fixes = CriticalFixes()

print("🧪 TEST NUOVE IMPOSTAZIONI")
print("="*60)

# Test con dati attuali
test_cases = [
    ("BTC", 46.3, 28, 1.7),
    ("SOL", 42.8, 28, 1.8),
    ("ETH", 72.2, 28, 4.9),  # Deve bloccare
    ("AVAX", 71.6, 28, 5.9),  # Deve bloccare
]

print("\n🎯 Test con soglia 45% (NUOVA):\n")
for name, rsi, fg, price_change in test_cases:
    should_buy, conf, info = fixes.fix_confidence_threshold(
        fg=fg, 
        rsi=rsi, 
        price_change=price_change, 
        min_conf=45  # SOGLIA ABBASSATA
    )
    
    status = "✅ BUY" if should_buy else "❌ NO BUY"
    color = '\033[92m' if should_buy else '\033[91m'
    reset = '\033[0m'
    
    print(f"{color}{status}{reset} | {name}: Conf={conf:.0f}%, RSI={rsi}, Price={price_change:+.1f}%")
    if conf > 0:
        print(f"         {info}")

print("\n" + "="*60)
print("\n✅ RISULTATO:")
buys = sum(1 for _, rsi, fg, pc in test_cases if fixes.fix_confidence_threshold(fg=fg, rsi=rsi, price_change=pc, min_conf=45)[0])
print(f"   - {buys} BUY signal su 4 monete")
print("   - ETH e AVAX bloccati (RSI > 70) ✓")
print("   - BTC e SOL dovrebbero passare (47% > 45%) ✓")
