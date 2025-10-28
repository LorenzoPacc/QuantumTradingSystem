import re

with open('quantum_trader_ultimate_final.py', 'r') as f:
    content = f.read()

# Aggiungi arrotondamento quantità per LOT_SIZE
old_code = 'quantity = round(risk_amount / current_price, 6)'
new_code = '''# Arrotonda per LOT_SIZE requirements
from binance.client import Client
try:
    symbol_info = self.client.get_symbol_info(symbol)
    for filt in symbol_info['filters']:
        if filt['filterType'] == 'LOT_SIZE':
            step_size = float(filt['stepSize'])
            quantity = round(risk_amount / current_price / step_size) * step_size
            quantity = round(quantity, 8)
            break
    else:
        quantity = round(risk_amount / current_price, 6)
except:
    quantity = round(risk_amount / current_price, 6)'''

content = content.replace(old_code, new_code)

with open('quantum_trader_ultimate_final.py', 'w') as f:
    f.write(content)

print("✅ Fix LOT_SIZE applicato!")
