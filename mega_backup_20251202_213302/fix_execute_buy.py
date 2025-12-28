#!/usr/bin/env python3

with open('quantum_v3_enhanced.py', 'r') as f:
    content = f.read()

# Trova execute_buy e verifica l'accesso al prezzo
import re

# Cerca il metodo execute_buy
pattern = r'def execute_buy\(self, symbol: str, market_data: Dict, reason: str\):.*?(?=\n    def |\Z)'
match = re.search(pattern, content, re.DOTALL)

if match:
    method = match.group(0)
    
    # Cerca come accede al prezzo
    if "market_data['price']" in method or 'market_data.get(\'price\')' in method:
        print("❌ BUG TROVATO: usa market_data['price'] invece di market_data['5m']['price']")
        
        # Fix: sostituisci l'accesso
        fixed_method = method.replace(
            "price = market_data['price']",
            "price = market_data['5m']['price']"
        ).replace(
            "price = market_data.get('price'",
            "price = market_data.get('5m', {}).get('price'"
        )
        
        content = content.replace(method, fixed_method)
        
        with open('quantum_v3_enhanced.py', 'w') as f:
            f.write(content)
        
        print("✅ FIX applicato!")
    else:
        print("🤔 execute_buy non trovato o già corretto")
else:
    print("⚠️  Metodo execute_buy non trovato")

# Test sintassi
import py_compile
try:
    py_compile.compile('quantum_v3_enhanced.py', doraise=True)
    print("✅ Sintassi OK")
except Exception as e:
    print(f"❌ Errore: {e}")

