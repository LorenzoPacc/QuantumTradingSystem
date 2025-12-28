#!/usr/bin/env python3
"""Script per applicare tutte le enhancement al codice V3"""

import re

# Leggi il file originale
with open('quantum_v3_perfect.py', 'r') as f:
    content = f.read()

# 1. Aggiungi check_lock all'__init__
init_pattern = r'(def __init__\(self, dry_run=True\):\s*\n\s*""".*?"""\s*\n)'
init_replacement = r'\1        check_lock()\n'

content = re.sub(init_pattern, init_replacement, content, flags=re.DOTALL)

# 2. Modifica __init__ per caricare portfolio
init_portfolio_pattern = r'(self\.cash = 200\.0\s*\n\s*self\.portfolio = \{\}\s*\n\s*self\.cycle_count = 0)'
init_portfolio_replacement = '''# Prova a caricare portfolio esistente
        if not self.load_portfolio():
            # Setup nuovo portfolio
            self.cash = 200.0
            self.portfolio = {}
            self.cycle_count = 0'''

content = re.sub(init_portfolio_pattern, init_portfolio_replacement, content)

# 3. Aggiungi save_portfolio dopo execute_buy e execute_sell
# execute_buy
buy_pattern = r'(def execute_buy\(self, symbol, price, position_size, signal_strength\):.*?logger\.info\(f"\[DRY-RUN\] 🟢 BUY.*?"\))'
buy_replacement = r'\1\n        self.save_portfolio()'

content = re.sub(buy_pattern, buy_replacement, content, flags=re.DOTALL)

# execute_sell  
sell_pattern = r'(def execute_sell\(self, symbol, price, signal_strength\):.*?logger\.info\(f"\[DRY-RUN\] 🔴 SELL.*?"\))'
sell_replacement = r'\1\n        self.save_portfolio()'

content = re.sub(sell_pattern, sell_replacement, content, flags=re.DOTALL)

# 4. Applica decoratori retry
# calculate_rsi
rsi_pattern = r'(def calculate_rsi\(self, symbol, timeframe=\'15m\', limit=100\):)'
rsi_replacement = r'    @retry_on_error(max_retries=3, delay=2)\n    \1'

content = re.sub(rsi_pattern, rsi_replacement, content)

# get_current_price
price_pattern = r'(def get_current_price\(self, symbol\):)'
price_replacement = r'    @retry_on_error(max_retries=3, delay=2)\n    \1'

content = re.sub(price_pattern, price_replacement, content)

# get_fear_greed_index
fear_pattern = r'(def get_fear_greed_index\(self\):)'
fear_replacement = r'    @retry_on_error(max_retries=5, delay=1)\n    \1'

content = re.sub(fear_pattern, fear_replacement, content)

# Scrivi il file modificato
with open('quantum_v3_perfect.py', 'w') as f:
    f.write(content)

print("✅ Tutte le enhancement applicate con successo!")
