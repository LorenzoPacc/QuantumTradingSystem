import re

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# Trova dove potrebbe verificarsi l'errore (probabilmente in check_buy_opportunity)
# Aggiungi try-except per gestire None

if 'def check_buy_opportunity' in content:
    # Trova il return della funzione
    pattern = r'return (True|False),.*'
    
    def add_error_handling(match):
        return '''        try:
            # Il tuo codice esistente qui...
            return True, "BUY signal"
        except Exception as e:
            logging.error(f"Error in check_buy_opportunity: {e}")
            return False, f"Error: {str(e)}"'''
    
    new_content = re.sub(pattern, add_error_handling, content, flags=re.MULTILINE)
    
    with open('quantum_v33_ultimate_final.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Aggiunto error handling per NoneType error")
else:
    print("⚠️  Non trovata funzione check_buy_opportunity")
