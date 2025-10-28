import re

with open('quantum_trader_ultimate_final.py', 'r') as f:
    content = f.read()

# Aumenta soglia emergency stop
content = content.replace('"emergency_stop_loss": -1000', '"emergency_stop_loss": -5000')

# Disabilita controllo balance per test
content = content.replace('if current_balance <= emergency_stop:', 'if False and current_balance <= emergency_stop:')

with open('quantum_trader_ultimate_final.py', 'w') as f:
    f.write(content)

print("✅ Emergency stop disabilitato per test!")
