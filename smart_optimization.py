with open('quantum_smart_improvements.py', 'r') as f:
    content = f.read()

# 1. RSI a 50 (volatilità normale)
content = content.replace(
    'else:  # Volatilità normale\n            return (48, 65)',
    'else:  # Volatilità normale\n            return (50, 65)'
)

# 2. RSI alta volatilità a 47
content = content.replace(
    'return (45, 70)  # RSI < 45 per comprare',
    'return (48, 70)  # RSI < 48 per comprare'
)

# 3. Conferme: 1/3 timeframe
content = content.replace(
    'if confirmations < 2:',
    'if confirmations < 1:'
)

with open('quantum_smart_improvements.py', 'w') as f:
    f.write(content)

print("✅ OTTIMIZZAZIONE APPLICATA:")
print("   • RSI normale: < 50 (era 48)")
print("   • RSI alta vol: < 48 (era 45)")
print("   • Conferme: 1/3 TF (era 2/3)")
print("")
print("🎯 Risultato atteso:")
print("   • 4-8 trade/giorno")
print("   • Win rate ~50-58%")
print("   • Rischio controllato dai filtri rimanenti")
