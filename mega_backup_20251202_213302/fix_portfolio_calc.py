#!/usr/bin/env python3

with open('quantum_v3_enhanced.py', 'r') as f:
    content = f.read()

# Il problema è nel calcolo totale portfolio
# Cerca pattern: total_value = self.cash_balance + sum(...)

# Fix 1: Nel run_cycle, dopo check BUY/SELL
old_calc = """total_value = self.cash_balance + sum(
                p['quantity'] * market_data['5m']['price']
                for p in self.positions.values()
            )"""

new_calc = """# Calcola valore totale portfolio
            total_value = self.cash_balance
            for symbol, pos in self.positions.items():
                try:
                    md = self.get_market_data(symbol)
                    if md and '5m' in md:
                        total_value += pos['quantity'] * md['5m']['price']
                except Exception as e:
                    logging.error(f"Error calculating position value for {symbol}: {e}")"""

if old_calc in content:
    content = content.replace(old_calc, new_calc)
    print("✅ Fix portfolio calculation")
else:
    # Trova run_cycle e cerca il problema
    import re
    pattern = r'(def run_cycle.*?)(total_value.*?self\.cash_balance.*?\))'
    
    matches = re.findall(pattern, content, re.DOTALL)
    if matches:
        print(f"⚠️  Trovate {len(matches)} occorrenze da fixare manualmente")
        print("Pattern trovato - fix alternativo...")
        
        # Fix alternativo: sostituisci qualsiasi accesso market_data['price'] in run_cycle
        content = re.sub(
            r"market_data\['price'\]",
            "market_data.get('5m', {}).get('price', 0)",
            content
        )
        print("✅ Fix applicato (metodo alternativo)")

with open('quantum_v3_enhanced.py', 'w') as f:
    f.write(content)

print("✅ File aggiornato!")

import py_compile
try:
    py_compile.compile('quantum_v3_enhanced.py', doraise=True)
    print("✅ Sintassi OK")
except Exception as e:
    print(f"❌ Errore sintassi: {e}")

