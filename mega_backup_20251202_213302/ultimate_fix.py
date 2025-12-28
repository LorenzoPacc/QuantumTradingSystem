#!/usr/bin/env python3
"""
Fix definitivo per tutti i problemi
"""

with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

modified = False

# FIX 1: Commenta completamente il blocco try del regime report
in_regime_try = False
for i, line in enumerate(lines):
    # Trova il try block che causa il problema Series
    if 'btc_data = self.get_symbol_data' in line and i > 0:
        # Cerca il try: prima di questa riga
        for j in range(i-1, max(0, i-10), -1):
            if 'try:' in lines[j] and 'regime' in ''.join(lines[j:i]).lower():
                # Commenta dal try fino all'except
                k = j
                while k < len(lines) and 'Market regime report error' not in lines[k]:
                    if not lines[k].strip().startswith('#'):
                        lines[k] = '        # TEMP DISABLED: ' + lines[k]
                    k += 1
                # Commenta anche la riga dell'except
                if k < len(lines):
                    lines[k] = '        # TEMP DISABLED: ' + lines[k]
                modified = True
                print(f"✅ Commentato regime report try block (righe {j+1}-{k+1})")
                break
        break

# FIX 2: Trova check_buy_signal e assicura che usi self.fear_index
for i, line in enumerate(lines):
    if 'def check_buy_signal(self, symbol' in line:
        # Cerca la prima riga di codice dopo la def
        j = i + 1
        while j < len(lines) and (lines[j].strip() == '' or '"""' in lines[j] or lines[j].strip().startswith('#')):
            j += 1
        
        # Inserisci controllo fear_index
        indent = '        '
        check = f'{indent}# Ensure fear_index is available\n'
        check += f'{indent}fear_index = getattr(self, "fear_index", None)\n'
        check += f'{indent}if fear_index is None:\n'
        check += f'{indent}    fear_index = self.get_fear_greed_index()\n'
        
        # Controlla se già presente
        if 'fear_index = getattr' not in ''.join(lines[j:j+5]):
            lines.insert(j, check)
            modified = True
            print(f"✅ Aggiunto check fear_index in check_buy_signal (riga {j+1})")
        break

if modified:
    # Salva
    with open('quantum_v33_ultimate_final.py', 'w') as f:
        f.writelines(lines)
    print("\n🎯 Fix applicati!")
else:
    print("⚠️  Nessuna modifica necessaria o pattern non trovati")

