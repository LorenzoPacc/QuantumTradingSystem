#!/bin/bash
echo "🧹 PULIZIA TOTALE DUPLICATI..."

cp quantum_v33_ultimate_final.py quantum_backup_before_total_clean.py

python3 << 'PYEND'
with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

# Trova tutte le occorrenze di FEAR BONUS
fear_bonus_lines = []
for i, line in enumerate(lines):
    if '# 🚀 FEAR BONUS' in line:
        fear_bonus_lines.append(i)

print(f"🔍 Trovati {len(fear_bonus_lines)} blocchi FEAR BONUS alle righe: {[x+1 for x in fear_bonus_lines]}")

# Ricostruisci il file SENZA duplicati
new_lines = []
skip_until = -1

for i, line in enumerate(lines):
    if i < skip_until:
        continue
    
    # Se è l'inizio di un blocco FEAR BONUS
    if '# 🚀 FEAR BONUS' in line:
        # Controlla se è il PRIMO blocco (dopo fix_confidence_threshold)
        # Cerca indietro per "fix_confidence_threshold"
        found_threshold = False
        for j in range(max(0, i-20), i):
            if 'fix_confidence_threshold' in lines[j]:
                found_threshold = True
                break
        
        if found_threshold and len([x for x in fear_bonus_lines if x < i]) == 0:
            # È il primo blocco, mantienilo
            # Aggiungi 8 righe (il blocco completo)
            for j in range(8):
                if i+j < len(lines):
                    new_lines.append(lines[i+j])
            skip_until = i + 8
            print(f"✅ Mantenuto blocco FEAR BONUS alla riga {i+1}")
        else:
            # È un duplicato, saltalo completamente
            # Cerca la fine del blocco (fino alla prossima riga non indentata o print con 📊)
            end = i + 1
            while end < len(lines):
                next_line = lines[end]
                # Fine blocco se: non indentato molto O contiene print con 📊 O if should_trade
                if (not next_line.startswith('            ') or 
                    'print(f"📊' in next_line or
                    'if should_trade:' in next_line):
                    break
                end += 1
            skip_until = end
            print(f"❌ Rimosso blocco duplicato righe {i+1}-{end}")
    else:
        new_lines.append(line)

# Rimuovi anche righe orfane tipo "min_confidence=45.0" e ")"
final_lines = []
for i, line in enumerate(new_lines):
    # Salta righe orfane
    stripped = line.strip()
    if stripped == 'min_confidence=45.0' or (stripped == ')' and i > 0 and 'if should_trade:' in new_lines[i+1] if i+1 < len(new_lines) else False):
        print(f"❌ Rimossa riga orfana: {stripped}")
        continue
    final_lines.append(line)

with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.writelines(final_lines)

print("\n✅ Pulizia completata!")
PYEND

echo ""
echo "🔍 Verifica 680-730..."
sed -n '680,730p' quantum_v33_ultimate_final.py

echo ""
echo "🧪 Test sintassi..."
python3 -m py_compile quantum_v33_ultimate_final.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉🎉🎉 FINALMENTE FUNZIONA! 🎉🎉🎉"
else
    echo ""
    echo "❌ Errore rimanente:"
    python3 -m py_compile quantum_v33_ultimate_final.py 2>&1
fi
