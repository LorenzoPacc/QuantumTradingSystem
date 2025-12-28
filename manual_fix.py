with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# Sostituisci il blocco problematico
old_code = '''        # ✅ Check confidence threshold
        if confidence < 40.0:  # self.MIN_CONFIDENCE
            return 0.0
        else:
            logging.debug(f"{symbol}: Conf={confidence:.0f}%, RSI={rsi:.1f}, F&G={fear_index}, Price24h={price_change_24h:+.1f}%")
            return False, f"Low confidence ({confidence:.0f}% < 40%)"'''

new_code = '''        # ✅ Check confidence threshold
        if confidence < 40.0:  # self.MIN_CONFIDENCE
            logging.debug(f"{symbol}: Conf={confidence:.0f}%, RSI={rsi:.1f}, F&G={fear_index}, Price24h={price_change_24h:+.1f}%")
            return False, f"Low confidence ({confidence:.0f}% < 40%)"'''

if old_code in content:
    content = content.replace(old_code, new_code)
    with open('quantum_v33_ultimate_final.py', 'w') as f:
        f.write(content)
    print("✅ Correzione applicata con successo!")
else:
    print("❌ Codice non trovato. Forse le righe sono diverse?")
    print("Cercando pattern alternativo...")
    # Prova pattern più semplice
    import re
    pattern = r'if confidence < 40\.0.*?\n\s+return 0\.0'
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, 'if confidence < 40.0:  # self.MIN_CONFIDENCE\n            logging.debug(f"{symbol}: Conf={confidence:.0f}%, RSI={rsi:.1f}, F&G={fear_index}, Price24h={price_change_24h:+.1f}%")\n            return False, f"Low confidence ({confidence:.0f}% < 40%)"', content)
        with open('quantum_v33_ultimate_final.py', 'w') as f:
            f.write(content)
        print("✅ Correzione con regex applicata!")
