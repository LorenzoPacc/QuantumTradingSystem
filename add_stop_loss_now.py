#!/usr/bin/env python3
"""
Aggiunge stop-loss e take-profit alla funzione check_sell_conditions
"""

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# Trova la funzione check_sell_conditions
if 'def check_sell_conditions' in content:
    print("✅ Funzione check_sell_conditions trovata")
    
    # Cerca il punto dove aggiungere lo stop-loss
    # Dobbiamo aggiungere PRIMA di altri controlli
    
    stop_loss_code = '''
        # ⚠️ STOP-LOSS E TAKE-PROFIT AUTOMATICI
        pnl_percent = ((current_price - entry_price) / entry_price) * 100
        
        # Stop-Loss: -3%
        if pnl_percent <= -3.0:
            return True, f"STOP-LOSS triggered at {pnl_percent:.2f}%"
        
        # Take-Profit: +4%
        if pnl_percent >= 4.0:
            return True, f"TAKE-PROFIT triggered at {pnl_percent:.2f}%"
        
        # Trailing Stop: Se profit > 2%, proteggi con stop a +1%
        if pnl_percent >= 2.0:
            trailing_stop = ((current_price - (entry_price * 1.01)) / entry_price) * 100
            if trailing_stop <= 0:
                return True, f"TRAILING-STOP triggered (was at +{pnl_percent:.2f}%)"
'''
    
    # Inserisci dopo la definizione della funzione
    insert_pos = content.find('def check_sell_conditions(')
    if insert_pos != -1:
        # Trova la fine della docstring o prima riga di codice
        next_line = content.find('\n', insert_pos)
        next_line = content.find('\n', next_line + 1)  # Salta la def line
        
        # Se c'è una docstring, skippa
        if '"""' in content[next_line:next_line+100]:
            # Trova la fine della docstring
            doc_end = content.find('"""', next_line + 10)
            insert_pos = content.find('\n', doc_end) + 1
        else:
            insert_pos = next_line + 1
        
        new_content = content[:insert_pos] + stop_loss_code + content[insert_pos:]
        
        with open('quantum_v33_ultimate_final.py', 'w') as f:
            f.write(new_content)
        
        print("✅ Stop-Loss aggiunto!")
        print("   - Stop-Loss: -3%")
        print("   - Take-Profit: +4%")
        print("   - Trailing-Stop: Protegge profitti > +2%")
    else:
        print("❌ Funzione non trovata nel formato atteso")
else:
    print("❌ Funzione check_sell_conditions non trovata!")
    print("\n📍 Mostra funzioni disponibili:")
    for line in content.split('\n'):
        if 'def check' in line or 'def sell' in line:
            print(f"   {line.strip()}")

