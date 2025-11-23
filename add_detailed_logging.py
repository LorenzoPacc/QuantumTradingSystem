#!/usr/bin/env python3

with open('quantum_v3_enhanced.py', 'r') as f:
    content = f.read()

# Trova il run_cycle e aggiungi logging dettagliato
# Cerca la sezione "Checking BUY signals"

# Aggiungi logging in check_buy_signal per mostrare tutti i rejection reasons
old_pattern = 'logging.debug(f"❌ No BUY: {reason}")'
new_pattern = 'logging.info(f"❌ No BUY ({symbol}): {reason}")'

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    print("✅ Logging rejection reasons upgraded to INFO")
else:
    print("⚠️  Pattern not found")

with open('quantum_v3_enhanced.py', 'w') as f:
    f.write(content)

print("✅ Detailed logging added")

