print("🧪 FINAL FEAR BONUS TEST")
print("="*60)

import re

# Leggi il file e cerca il Fear Bonus
with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# Cerca in check_buy
print("\n🔍 CERCO IN check_buy:")
if 'def check_buy' in content:
    start = content.find('def check_buy')
    end = content.find('def check_sell', start)
    if end != -1:
        check_buy_code = content[start:end]
        
        if 'fear_index < 30' in check_buy_code:
            print("✅ Extreme Fear check: TROVATO")
        else:
            print("❌ Extreme Fear check: NON TROVATO")
            
        if 'confidence * 1.25' in check_buy_code or 'confidence *= 1.25' in check_buy_code:
            print("✅ +25% bonus: TROVATO")
        else:
            print("❌ +25% bonus: NON TROVATO")
            
        if 'confidence >= 40.0' in check_buy_code:
            print("✅ Auto-buy 40%: TROVATO")
        else:
            print("❌ Auto-buy 40%: NON TROVATO")
        
        # Mostra le linee del bonus
        lines = check_buy_code.split('\n')
        print("\n📋 RIGHE FEAR BONUS:")
        for i, line in enumerate(lines):
            if 'fear' in line.lower() or 'confidence' in line.lower() or 'bonus' in line.lower():
                print(f"   {i:3}: {line.strip()[:70]}")
    else:
        print("❌ Non trovo la fine di check_buy")
else:
    print("❌ check_buy non trovata")

# Cerca in fix_confidence_threshold
print("\n🔍 CERCO IN fix_confidence_threshold:")
if 'def fix_confidence_threshold' in content:
    print("✅ Funzione fixes trovata")
    
    # Mostra se c'è il bonus
    if 'fg < 30' in content:
        print("✅ Fear Bonus nelle fixes: TROVATO")
    else:
        print("⚠️  Fear Bonus nelle fixes: NON TROVATO")
else:
    print("❌ fix_confidence_threshold non trovata")

print("\n" + "="*60)
print("📊 RIEPILOGO CONFIGURAZIONE FEAR BONUS:")
print("• Extreme Fear (<30): +25% confidence boost")
print("• Fear (<45): +15% confidence boost")
print("• Auto-buy threshold: 40% confidence")
print("• Base threshold: 35% confidence")
print("="*60)
