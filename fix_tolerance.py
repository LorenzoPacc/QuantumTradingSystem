import re

# Leggi il file
with open('quantum_trader_ultimate_final.py', 'r') as f:
    content = f.read()

# Codice da inserire PRIMA della condizione
tolerance_code = '''            # Tolleranza per ingresso trade (95% della soglia)
            TOLERANCE_CONFLUENCE = 0.95
            TOLERANCE_CONFIDENCE = 2
            min_conf_with_tolerance = self.config.TRADING_CONFIG["min_confluence"] * TOLERANCE_CONFLUENCE
            min_confidence_with_tolerance = self.config.TRADING_CONFIG["min_confidence"] - TOLERANCE_CONFIDENCE
            
'''

# Trova la sezione da modificare
pattern = r'(buy_signals = \[s for s in signals if s == "BUY"\].*?sell_signals = \[s for s in signals if s == "SELL"\])'

# Inserisci il codice dopo questa sezione
new_content = re.sub(pattern, r'\1\n\n' + tolerance_code, content, flags=re.DOTALL)

# Modifica la condizione if
new_content = new_content.replace(
    'if (total_confluence >= self.config.TRADING_CONFIG["min_confluence"] and\n                total_confidence >= self.config.TRADING_CONFIG["min_confidence"]):',
    'if (total_confluence >= min_conf_with_tolerance and\n                total_confidence >= min_confidence_with_tolerance):'
)

# Scrivi il file modificato
with open('quantum_trader_ultimate_final.py', 'w') as f:
    f.write(new_content)

print("✅ Patch applicata con successo!")
print("📊 Tolleranza: 95% per confluence, -2% per confidence")
