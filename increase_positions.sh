#!/bin/bash
echo "🔧 INCREASING MAX POSITIONS TO 5..."

cp quantum_v33_ultimate_final.py quantum_backup_positions.py

# Change max_positions from 3 to 5
sed -i 's/self\.max_positions = 3/self.max_positions = 5/' quantum_v33_ultimate_final.py

echo "✅ Max positions changed: 3 → 5"
echo ""
echo "📊 New configuration:"
grep "max_positions" quantum_v33_ultimate_final.py | head -3
echo ""
echo "🔄 Restarting bot..."
pkill -f quantum_v33_ultimate_final.py
sleep 2
nohup python3 quantum_v33_ultimate_final.py > /dev/null 2>&1 &
sleep 2

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║  ✅ MAX POSITIONS INCREASED: 3 → 5                   ║"
echo "║  📊 More opportunities for profit                    ║"
echo "║  ⚠️  Slightly higher risk but controlled             ║"
echo "╚═══════════════════════════════════════════════════════╝"
