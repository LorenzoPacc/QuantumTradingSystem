#!/usr/bin/env python3

with open('quantum_smart_improvements.py', 'r') as f:
    content = f.read()

# Trova e sostituisci le soglie RSI in AdaptiveRSI
old_thresholds = '''        if volatility_ratio > 1.5:  # Alta volatilità (+50%)
            self.logger.debug(f"High volatility ({volatility_ratio:.2f}x), using aggressive RSI")
            return (30, 70)
            
        elif volatility_ratio < 0.7:  # Bassa volatilità (-30%)
            self.logger.debug(f"Low volatility ({volatility_ratio:.2f}x), using conservative RSI")
            return (40, 60)
            
        else:  # Volatilità normale
            return (35, 65)'''

# NUOVE SOGLIE ottimizzate per day trading
new_thresholds = '''        if volatility_ratio > 1.5:  # Alta volatilità (+50%)
            self.logger.debug(f"High volatility ({volatility_ratio:.2f}x), using aggressive RSI")
            return (45, 70)  # RSI < 45 per comprare
            
        elif volatility_ratio < 0.7:  # Bassa volatilità (-30%)
            self.logger.debug(f"Low volatility ({volatility_ratio:.2f}x), using conservative RSI")
            return (50, 60)  # RSI < 50 (più opportunità)
            
        else:  # Volatilità normale
            return (48, 65)  # RSI < 48 (bilanciato)'''

if old_thresholds in content:
    content = content.replace(old_thresholds, new_thresholds)
    print("✅ Soglie RSI aggiornate per day trading:")
    print("   • Volatilità alta:    RSI < 45 (era 30)")
    print("   • Volatilità normale: RSI < 48 (era 35)")
    print("   • Volatilità bassa:   RSI < 50 (era 40)")
    print("")
    
    with open('quantum_smart_improvements.py', 'w') as f:
        f.write(content)
    
    print("✅ File aggiornato")
else:
    print("⚠️  Pattern non trovato - modifica manuale necessaria")

# Test sintassi
import py_compile
try:
    py_compile.compile('quantum_smart_improvements.py', doraise=True)
    print("✅ Sintassi OK")
except Exception as e:
    print(f"❌ Errore sintassi: {e}")
    exit(1)

