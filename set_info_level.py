#!/usr/bin/env python3

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# Cambia il livello di logging da DEBUG a INFO
replacements = [
    ('level=logging.DEBUG', 'level=logging.INFO'),
    ('setLevel(logging.DEBUG)', 'setLevel(logging.INFO)'),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f"✅ Sostituito: {old} → {new}")

with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.write(content)

print("\n✅ Bot configurato per logging pulito (INFO level)")
