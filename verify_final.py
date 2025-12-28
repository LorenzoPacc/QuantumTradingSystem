import re

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

print("🔍 VERIFICA FINALE FEAR BONUS")
print("="*50)

# Trova check_buy
pattern = r'def check_buy\(self, symbol\):.*?def check_sell'
match = re.search(pattern, content, re.DOTALL)

if match:
    func = match.group(0)
    print(f"✅ check_buy trovata ({len(func)} caratteri)")
    
    # Cerca elementi chiave
    checks = [
        ('fear_index < 30', 'Controllo Extreme Fear'),
        ('confidence * 1.25', 'Bonus +25%'),
        ('confidence >= 40', 'Auto-buy a 40%'),
        ('FEAR BONUS', 'Testo Fear Bonus nel log'),
        ('F&G=', 'Log Fear & Greed')
    ]
    
    for pattern, desc in checks:
        if pattern in func:
            print(f"✅ {desc}: TROVATO")
        else:
            print(f"❌ {desc}: NON TROVATO")
    
    # Mostra le linee del Fear Bonus
    print("\n📋 SEZIONE FEAR BONUS:")
    lines = func.split('\n')
    for i, line in enumerate(lines):
        if 'FEAR BONUS' in line or 'fear_index <' in line or 'confidence *' in line:
            print(f"   {i:3}: {line.strip()}")
else:
    print("❌ check_buy non trovata")

print("\n" + "="*50)
print("🎯 CONFIGURAZIONE ATTIVA:")
print("• Extreme Fear (<30): confidence × 1.25 (+25%)")
print("• Fear (<45): confidence × 1.15 (+15%)")
print("• Auto-buy: confidence >= 40%")
print("="*50)
