#!/usr/bin/env python3

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# Abbassa da 50 a 45
content = content.replace('min_confidence=50', 'min_confidence=45')
content = content.replace('min_conf=50', 'min_conf=45')

with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.write(content)

print("✅ Soglia abbassata a 45%")
print("   BTC e SOL (47%) ora passano! ✓")
