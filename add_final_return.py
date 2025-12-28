import re

with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

# Trova la riga di def check_sell
check_sell_line = -1
for i, line in enumerate(lines):
    if 'def check_sell' in line:
        check_sell_line = i
        break

if check_sell_line != -1:
    print(f"✅ Trovato 'def check_sell' a riga {check_sell_line + 1}")
    
    # Inserisci return finale 2 righe prima di def check_sell
    insert_line = check_sell_line - 1
    
    return_code = '''        # Default return if no conditions met
        logging.debug(f"{symbol}: No BUY conditions met, confidence={confidence:.1f}%")
        return False, f"No BUY signal (confidence={confidence:.0f}%)"
'''
    
    lines.insert(insert_line, return_code)
    
    with open('quantum_v33_ultimate_final.py', 'w') as f:
        f.writelines(lines)
    
    print(f"✅ Inserito return finale a riga {insert_line + 1}")
    print("🎉 La funzione check_buy ora ha sempre un return!")
else:
    print("❌ 'def check_sell' non trovato")
