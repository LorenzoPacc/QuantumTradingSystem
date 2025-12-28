#!/bin/bash
echo "🔧 FIX INDENTAZIONE COMPLETO..."

# Mostra contesto
echo "=== RIGHE 720-735 ==="
sed -n '720,735p' quantum_v33_ultimate_final.py

echo ""
echo "=== RIGHE 675-690 ==="
sed -n '675,690p' quantum_v33_ultimate_final.py

echo ""
echo "🔍 Cerca righe con indentazione anomala..."
grep -n "^            [a-z]" quantum_v33_ultimate_final.py | head -20
