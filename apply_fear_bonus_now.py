import re

with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

print("🔧 APPLICAZIONE FEAR BONUS...")

# Trova la riga dopo il calcolo confidence
found = False
for i, line in enumerate(lines):
    if 'should_trade, confidence, score_info = self.fixes.fix_confidence_threshold' in line:
        print(f"✅ Trovato calcolo confidence a riga {i+1}")
        
        # Inserisci fear bonus 2 righe dopo
        fear_bonus = '''        # DYNAMIC FEAR & GREED BOOST - APPLIED NOW
        original_confidence = confidence
        if fear_index < 30:  # EXTREME FEAR
            confidence = min(confidence * 1.25, 95.0)  # +25% bonus, max 95%
            logging.debug(f"🚀 EXTREME_FEAR BOOST: {symbol} {original_confidence:.1f}% → {confidence:.1f}%")
        elif fear_index < 45:  # FEAR
            confidence = min(confidence * 1.15, 90.0)  # +15% bonus, max 90%
            logging.debug(f"📈 FEAR BOOST: {symbol} {original_confidence:.1f}% → {confidence:.1f}%")
        
'''
        lines.insert(i + 2, fear_bonus)
        found = True
        print(f"✅ Fear bonus inserito a riga {i+3}")
        break

if found:
    with open('quantum_v33_ultimate_final.py', 'w') as f:
        f.writelines(lines)
    
    print("🎉 FEAR BONUS APPLICATO!")
    print("   Extreme Fear (<30): +25% confidence")
    print("   Fear (<45): +15% confidence")
    print("   Max confidence: 95%")
else:
    print("❌ Calcolo confidence non trovato")
    
# Verifica
print("\n📝 VERIFICA APPLICAZIONE:")
with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()
    if 'DYNAMIC FEAR & GREED BOOST' in content:
        print("✅ Fear bonus trovato nel file")
    else:
        print("❌ Fear bonus non trovato")
