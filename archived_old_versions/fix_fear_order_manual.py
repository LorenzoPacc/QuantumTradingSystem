#!/usr/bin/env python3
"""
Fix manuale per spostare fear_index prima del try block
"""

with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

# Trova il try block che usa fear_greed (intorno alla riga 893)
try_idx = None
for i, line in enumerate(lines):
    if 'detect_market_regime(btc_data, fear_greed)' in line:
        # Trova il try: prima di questa riga
        for j in range(i - 1, max(0, i - 20), -1):
            if 'try:' in lines[j]:
                try_idx = j
                break
        break

if try_idx is None:
    print("❌ Try block non trovato")
    exit(1)

print(f"✅ Try block trovato alla riga {try_idx + 1}")

# Trova dove è definito fear_index (dopo il try block)
fear_idx = None
for i in range(try_idx, min(len(lines), try_idx + 50)):
    if 'fear_index = self.get_fear_greed_index()' in lines[i]:
        fear_idx = i
        break

if fear_idx is None:
    print("❌ fear_index non trovato")
    exit(1)

print(f"✅ fear_index trovato alla riga {fear_idx + 1}")

# Estrai le righe da spostare (fear_index e sentiment)
fear_lines = []
sentiment_start = None

# Prendi fear_index
fear_lines.append(lines[fear_idx])

# Cerca sentiment subito dopo
for i in range(fear_idx + 1, min(len(lines), fear_idx + 10)):
    if 'sentiment = (' in lines[i]:
        sentiment_start = i
        # Prendi tutte le righe del blocco sentiment
        j = i
        while j < len(lines) and (')' not in lines[j] or 'EXTREME_GREED' not in lines[j]):
            fear_lines.append(lines[j])
            j += 1
        fear_lines.append(lines[j])  # Ultima riga del sentiment
        break

print(f"✅ Trovate {len(fear_lines)} righe da spostare")

# Rimuovi le righe dalla posizione originale (in ordine inverso)
for i in range(len(fear_lines) - 1, -1, -1):
    if sentiment_start and i == 0:
        lines.pop(fear_idx)
    elif sentiment_start:
        lines.pop(sentiment_start + i - 1)

# Inserisci PRIMA del try block
for i, line in enumerate(fear_lines):
    lines.insert(try_idx + i, line)

# Aggiungi alias fear_greed = fear_index
lines.insert(try_idx + len(fear_lines), '        fear_greed = fear_index  # Alias per regime detection\n')

# Salva
with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.writelines(lines)

print("\n🎯 Fix completato!")
print(f"Spostato fear_index e sentiment dalla riga {fear_idx+1} alla riga {try_idx+1}")
