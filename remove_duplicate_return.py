import re

with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

# Trova la funzione check_buy
start_line = -1
for i, line in enumerate(lines):
    if 'def check_buy(self, symbol):' in line:
        start_line = i
        break

if start_line != -1:
    # Trova "def check_sell"
    check_sell_line = -1
    for i in range(start_line, len(lines)):
        if 'def check_sell' in lines[i]:
            check_sell_line = i
            break
    
    if check_sell_line != -1:
        print(f"✅ Funzione check_buy: righe {start_line+1} - {check_sell_line}")
        
        # Cerca "Default return if no conditions met" DUPLICATI
        default_returns = []
        for i in range(start_line, check_sell_line):
            if 'Default return if no conditions met' in lines[i]:
                default_returns.append(i)
        
        if len(default_returns) > 1:
            print(f"⚠️  Trovati {len(default_returns)} return duplicati")
            print(f"   Righe: {[r+1 for r in default_returns]}")
            
            # Mantieni solo il PRIMO, rimuovi i successivi
            for i in range(len(default_returns)-1, 0, -1):  # Dall'ultimo al secondo
                line_to_remove = default_returns[i]
                # Rimuovi la riga del commento e la successiva (logging + return)
                if line_to_remove < len(lines):
                    # Rimuovi 3 righe: commento, logging.debug, return
                    del lines[line_to_remove:line_to_remove+3]
                    print(f"   ✅ Rimosso return duplicato a riga {line_to_remove+1}")
            
            with open('quantum_v33_ultimate_final.py', 'w') as f:
                f.writelines(lines)
            
            print("🎉 Return duplicati rimossi!")
        else:
            print("✅ Nessun return duplicato trovato")
    else:
        print("❌ 'def check_sell' non trovato nella funzione")
else:
    print("❌ 'def check_buy' non trovato")
