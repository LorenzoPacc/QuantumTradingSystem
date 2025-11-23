#!/usr/bin/env python3

with open('quantum_v3_enhanced.py', 'r') as f:
    content = f.read()

# Trova __init__ e verifica se positions è inizializzato
if 'self.positions = {}' not in content:
    # Trova dove inizializzare positions
    # Dovrebbe essere dopo self.cash_balance = initial_capital
    
    content = content.replace(
        'self.cash_balance = initial_capital',
        'self.cash_balance = initial_capital\n        self.positions = {}'
    )
    
    print("✅ self.positions = {} aggiunto")
    
    # Salva
    with open('quantum_v3_enhanced.py', 'w') as f:
        f.write(content)
    
    print("✅ Fix applicato")
else:
    print("✅ self.positions già presente")

# Test sintassi
import py_compile
try:
    py_compile.compile('quantum_v3_enhanced.py', doraise=True)
    print("✅ Sintassi OK")
except Exception as e:
    print(f"❌ Errore: {e}")

