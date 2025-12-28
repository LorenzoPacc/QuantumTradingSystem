import re

with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

print("🔧 Correzione posizione Fear Bonus...")

# Trova la chiamata a fix_confidence_threshold
for i, line in enumerate(lines):
    if 'should_trade, confidence, score_info = self.fixes.fix_confidence_threshold' in line:
        print(f"✅ Trovato fix_confidence_threshold a riga {i+1}")
        
        # Trova la fine della chiamata (parentesi chiusa)
        for j in range(i, min(i+30, len(lines))):
            if lines[j].strip() == ')':
                print(f"✅ Fine chiamata a riga {j+1}")
                
                # Sposta il Fear Bonus DOPO la chiamata
                # Trova l'inizio del Fear Bonus
                for k in range(i, j):
                    if 'DYNAMIC FEAR & GREED BOOST' in lines[k]:
                        print(f"✅ Fear Bonus inizia a riga {k+1}")
                        
                        # Estrai le righe del Fear Bonus (da k a j-1)
                        fear_bonus_lines = lines[k:j]
                        
                        # Rimuovi le righe dalla posizione originale
                        del lines[k:j]
                        
                        # Inserisci DOPO la chiamata (dopo la riga j)
                        # Ma ora j è cambiato perché abbiamo rimosso righe
                        # Calcola nuova posizione
                        new_pos = j - len(fear_bonus_lines) + 1
                        lines[new_pos:new_pos] = fear_bonus_lines
                        
                        print(f"✅ Fear Bonus spostato dopo la chiamata (riga {new_pos+1})")
                        break
                break
        break

# Scrivi file corretto
with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.writelines(lines)

print("🎉 Fear Bonus posizionato correttamente!")
