#!/usr/bin/env python3

with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

# Correggi la riga 695
for i, line in enumerate(lines):
    if '< 60%' in line and 'Low confidence' in line:
        lines[i] = line.replace('< 60%', '< 45%')
        print(f"✅ Riga {i+1} corretta:")
        print(f"   PRIMA: {line.strip()}")
        print(f"   DOPO:  {lines[i].strip()}")

with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.writelines(lines)

print("\n✅ Fix applicato!")
