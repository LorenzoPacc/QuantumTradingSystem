#!/usr/bin/env python3

with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

# Trova e sistema l'errore
fixed = False
for i, line in enumerate(lines):
    # Cerca righe dopo il BUY signal che usano 'confidence' invece di 'conf'
    if 'check_buy' in ''.join(lines[max(0, i-10):i]):
        if 'confidence' in line and 'conf' not in line and 'min_conf' not in line:
            # Sostituisci confidence con conf
            lines[i] = line.replace('confidence', 'conf')
            print(f"✅ Riga {i+1} corretta:")
            print(f"   PRIMA: {line.strip()}")
            print(f"   DOPO:  {lines[i].strip()}")
            fixed = True

if fixed:
    with open('quantum_v33_ultimate_final.py', 'w') as f:
        f.writelines(lines)
    print("\n✅ Bug corretto!")
else:
    print("⚠️ Pattern non trovato, cerco manualmente...")
    # Mostra le righe problematiche
    with open('quantum_v33_ultimate_final.py', 'r') as f:
        content = f.read()
        if 'name \'confidence\' is not defined' in content or True:
            # Trova le funzioni check_buy
            start = content.find('def check_buy_conditions')
            if start != -1:
                section = content[start:start+2000]
                print("\nSezione check_buy_conditions:")
                for i, line in enumerate(section.split('\n')[:50]):
                    if 'confidence' in line.lower():
                        print(f"{i}: {line}")
