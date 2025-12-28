#!/usr/bin/env python3
"""
Abbassa la soglia di confidence da 60% a 50%
"""

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# Trova e sostituisci tutte le chiamate con min_confidence=60
replacements = [
    ('min_confidence=60', 'min_confidence=50'),
    ('min_conf=60', 'min_conf=50'),
]

modified = False
for old, new in replacements:
    if old in content:
        count = content.count(old)
        content = content.replace(old, new)
        print(f"✅ Sostituito {count}x: {old} → {new}")
        modified = True

if modified:
    with open('quantum_v33_ultimate_final.py', 'w') as f:
        f.write(content)
    print("\n✅ Soglia abbassata a 50%")
else:
    print("⚠️ Nessuna soglia trovata, provo ricerca alternativa...")
    
    # Ricerca alternativa
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if 'confidence' in line.lower() and ('60' in line or '0.6' in line):
            print(f"Linea {i}: {line.strip()}")
