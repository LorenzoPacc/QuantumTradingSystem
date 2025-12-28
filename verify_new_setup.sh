#!/bin/bash
echo "🔍 VERIFYING NEW CONFIGURATION..."
echo ""

# 1. Check bot running
if pgrep -f quantum_v33_ultimate_final.py > /dev/null; then
    echo "✅ Bot is RUNNING"
    PID=$(pgrep -f quantum_v33_ultimate_final.py)
    echo "   PID: $PID"
else
    echo "❌ Bot NOT running!"
    exit 1
fi
echo ""

# 2. Check max_positions in code
echo "✅ Max positions in code:"
grep "self.max_positions = " quantum_v33_ultimate_final.py | head -1
echo ""

# 3. Check current status
echo "✅ Last cycle info:"
tail -20 quantum_v33_ultimate_final.log | grep "Positions:"
echo ""

# 4. Wait for next BUY check
echo "🔍 Monitoring for new BUY checks (next 3 minutes)..."
echo "   Press Ctrl+C to stop"
echo ""

timeout 180 tail -f quantum_v33_ultimate_final.log | grep --line-buffered -E "BUY|FEAR BONUS|Max positions|Positions:"
