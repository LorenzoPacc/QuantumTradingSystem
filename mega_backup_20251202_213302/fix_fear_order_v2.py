#!/usr/bin/env python3
"""
Fix v2 - più robusto
"""

with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

# Trova il try block
try_idx = None
for i, line in enumerate(lines):
    if 'detect_market_regime(btc_data, fear_greed)' in line:
        for j in range(i - 1, max(0, i - 20), -1):
            if 'try:' in lines[j]:
                try_idx = j
                break
        break

if try_idx is None:
    print("❌ Try block non trovato")
    exit(1)

print(f"✅ Try block trovato alla riga {try_idx + 1}")

# Trova fear_index
fear_idx = None
for i in range(try_idx, min(len(lines), try_idx + 50)):
    if 'fear_index = self.get_fear_greed_index()' in lines[i]:
        fear_idx = i
        break

if fear_idx is None:
    print("❌ fear_index non trovato")
    exit(1)

print(f"✅ fear_index trovato alla riga {fear_idx + 1}")

# Estrai fear_index line
fear_line = lines[fear_idx]

# Trova sentiment block (le righe dopo fear_index fino alla chiusura)
sentiment_lines = []
sentiment_start = None

for i in range(fear_idx + 1, min(len(lines), fear_idx + 15)):
    if 'sentiment = (' in lines[i]:
        sentiment_start = i
        # Prendi tutte le righe fino alla chiusura
        j = i
        paren_count = 1  # Conta parentesi
        sentiment_lines.append(lines[j])
        j += 1
        
        while j < len(lines) and paren_count > 0:
            sentiment_lines.append(lines[j])
            # Conta parentesi per trovare la chiusura
            paren_count += lines[j].count('(') - lines[j].count(')')
            j += 1
        
        break

print(f"✅ Trovate {len(sentiment_lines)} righe di sentiment")

# Costruisci blocco da spostare
block_to_move = [fear_line] + sentiment_lines + ['        fear_greed = fear_index  # Alias\n', '\n']

# Rimuovi dalla posizione originale (in ordine inverso per non sballare gli indici)
# Prima rimuovi sentiment
if sentiment_start:
    for _ in range(len(sentiment_lines)):
        lines.pop(sentiment_start)

# Poi rimuovi fear_index
lines.pop(fear_idx)

# Inserisci prima del try (che ora ha un indice diverso se abbiamo rimosso righe prima)
# Ricalcola try_idx
new_try_idx = try_idx
if fear_idx < try_idx:
    new_try_idx -= (1 + len(sentiment_lines))

# Inserisci il blocco
for i, line in enumerate(block_to_move):
    lines.insert(new_try_idx + i, line)

# Salva
with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.writelines(lines)

print("\n🎯 Fix completato!")
print(f"✅ Spostato blocco fear_greed prima del try block")
