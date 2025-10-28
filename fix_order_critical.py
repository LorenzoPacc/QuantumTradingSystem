with open('quantum_trader_ultimate_final.py', 'r') as f:
    content = f.read()

# Definisci l'ordine CORRETTO
correct_order = '''            buy_signals = [s for s in signals if s == "BUY"]
            sell_signals = [s for s in signals if s == "SELL"]

            # Tolleranza per ingresso trade (70% = molto aggressivo)
            TOLERANCE_CONFLUENCE = 0.70
            TOLERANCE_CONFIDENCE = 10
            min_conf_with_tolerance = self.config.TRADING_CONFIG["min_confluence"] * TOLERANCE_CONFLUENCE
            min_confidence_with_tolerance = self.config.TRADING_CONFIG["min_confidence"] - TOLERANCE_CONFIDENCE

            # DEBUG: Stampa i segnali per troubleshooting
            print(f"🔍 DEBUG SIGNALS: {signals}")
            print(f"🔍 DEBUG BUY: {len(buy_signals)}, SELL: {len(sell_signals)}")
            print(f"🔍 DEBUG Confluence: {total_confluence:.2f} >= {min_conf_with_tolerance:.2f}? {total_confluence >= min_conf_with_tolerance}")
            print(f"🔍 DEBUG Confidence: {total_confidence:.1f} >= {min_confidence_with_tolerance:.1f}? {total_confidence >= min_confidence_with_tolerance}")

'''

# Trova e sostituisci la sezione completa
import re
pattern = r'buy_signals = \[s for s in signals if s == "BUY"\].*?if \(total_confluence >= min_conf_with_tolerance and'
content = re.sub(pattern, correct_order + '            if (total_confluence >= min_conf_with_tolerance and', content, flags=re.DOTALL)

with open('quantum_trader_ultimate_final.py', 'w') as f:
    f.write(content)

print("✅ ORDINE CORRETTO APPLICATO!")
print("📋 Sequenza corretta:")
print("   1. buy_signals")
print("   2. sell_signals") 
print("   3. Calcolo tolleranza")
print("   4. Debug (usa variabili già calcolate)")
print("   5. Controllo if con tolleranza")
