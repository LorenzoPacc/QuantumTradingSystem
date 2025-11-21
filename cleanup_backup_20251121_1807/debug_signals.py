import re

with open('quantum_trader_ultimate_final.py', 'r') as f:
    content = f.read()

# Trova la sezione dei segnali e aggiungi debug
debug_code = '''
            # DEBUG: Stampa i segnali per troubleshooting
            print(f"🔍 DEBUG SIGNALS: {signals}")
            print(f"🔍 DEBUG BUY: {len(buy_signals)}, SELL: {len(sell_signals)}")
            print(f"🔍 DEBUG Confluence: {total_confluence:.2f} >= {min_conf_with_tolerance:.2f}? {total_confluence >= min_conf_with_tolerance}")
            print(f"🔍 DEBUG Confidence: {total_confidence:.1f} >= {min_confidence_with_tolerance:.1f}? {total_confidence >= min_confidence_with_tolerance}")
'''

# Inserisci il debug dopo la creazione dei segnali
content = content.replace(
    '            sell_signals = [s for s in signals if s == "SELL"]',
    '            sell_signals = [s for s in signals if s == "SELL"]' + debug_code
)

with open('quantum_trader_ultimate_final.py', 'w') as f:
    f.write(content)

print("✅ Debug segnali aggiunto!")
