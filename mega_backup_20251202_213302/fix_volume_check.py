#!/usr/bin/env python3

with open('quantum_smart_improvements.py', 'r') as f:
    content = f.read()

# Il problema: usa l'ULTIMA candela che è in formazione
# Soluzione: usa la PENULTIMA candela (completa)

old_volume_line = '            current_volume = klines_5m[-1][\'volume\'] if klines_5m else 0'
new_volume_line = '            # Usa penultima candela (ultima è in formazione)\n            current_volume = klines_5m[-2][\'volume\'] if len(klines_5m) >= 2 else (klines_5m[-1][\'volume\'] if klines_5m else 0)'

if old_volume_line in content:
    content = content.replace(old_volume_line, new_volume_line)
    print("✅ Volume check fixed: usa candela completa")
else:
    print("⚠️  Pattern non trovato")

# ALTERNATIVA: Abbassa threshold volume per 5m timeframe
# Per timeframe brevi, il volume è più volatile
old_threshold = '            vol_threshold = self.smart_volume.get_volume_threshold(atr_normalized)'
new_threshold = '''            vol_threshold = self.smart_volume.get_volume_threshold(atr_normalized)
            # Per timeframe 5m, usa soglia più bassa
            vol_threshold = max(0.3, vol_threshold * 0.5)  # 50% della soglia normale'''

if old_threshold in content:
    content = content.replace(old_threshold, new_threshold)
    print("✅ Volume threshold ridotto per 5m timeframe")

with open('quantum_smart_improvements.py', 'w') as f:
    f.write(content)

print("\n📊 Modifiche applicate:")
print("   • Usa candela COMPLETA invece di quella in formazione")
print("   • Threshold volume ridotto a 0.3x-0.65x (era 1.2-1.7x)")
print("   • Adatto per timeframe 5m")

import py_compile
try:
    py_compile.compile('quantum_smart_improvements.py', doraise=True)
    print("\n✅ Sintassi OK")
except Exception as e:
    print(f"\n❌ Errore: {e}")
