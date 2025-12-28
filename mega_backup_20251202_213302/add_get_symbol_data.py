#!/usr/bin/env python3
"""
Aggiunge il metodo get_symbol_data mancante
"""

import re

# Leggi il file originale
with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# Metodo da aggiungere
new_method = '''
    def get_symbol_data(self, symbol, timeframe=None, limit=100):
        """
        Ottiene dati OHLCV per un simbolo
        Wrapper per fetch_ohlcv con gestione errori
        """
        try:
            if timeframe is None:
                timeframe = self.interval
            
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            import pandas as pd
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}")
            return None

'''

# Trova dove inserire (prima del metodo calculate_rsi che è alla riga ~480)
# Cerchiamo "def calculate_rsi"
pattern = r'(\n    def calculate_rsi\()'
replacement = new_method + r'\1'

if re.search(pattern, content):
    content = re.sub(pattern, replacement, content, count=1)
    print("✅ Metodo inserito prima di calculate_rsi")
else:
    # Fallback: inserisci dopo check_min_notional
    pattern_fallback = r'(\n    def check_min_notional\([^}]+}\n)'
    if re.search(pattern_fallback, content):
        content = re.sub(pattern_fallback, r'\1' + new_method, content, count=1)
        print("✅ Metodo inserito dopo check_min_notional")
    else:
        print("❌ Pattern non trovato, provo inserimento manuale...")
        # Inserisci dopo riga 450 circa
        lines = content.split('\n')
        lines.insert(450, new_method)
        content = '\n'.join(lines)
        print("✅ Metodo inserito alla riga 450")

# Salva il file modificato
with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.write(content)

print("\n🎯 File quantum_v33_ultimate_final.py aggiornato!")
print("✅ Metodo get_symbol_data() aggiunto")
