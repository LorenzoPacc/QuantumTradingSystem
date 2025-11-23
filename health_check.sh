#!/bin/bash
echo "🏥 QUANTUM HEALTH CHECK"
echo "======================"

# Bot status
if ps aux | grep -q "[q]uantum_simple_fixed.py"; then
    pid=$(ps aux | grep "[q]uantum_simple_fixed.py" | awk '{print $2}' | head -1)
    uptime=$(($(ps -p $pid -o etimes= | tr -d ' ') / 60))
    echo "✅ Bot: RUNNING (PID: $pid, Uptime: ${uptime}m)"
else
    echo "❌ Bot: STOPPED"
fi

# Fear & Greed
fg=$(curl -s "https://api.alternative.me/fng/?limit=1" | python3 -c "import json,sys;print(json.load(sys.stdin)['data'][0]['value'])" 2>/dev/null || echo "N/A")
echo "📊 Fear & Greed: $fg"

# Portafoglio
if [ -f "quantum_v2_state.json" ]; then
    echo "💼 State file: OK"
else
    echo "⚠️ State file: Mancante"
fi

# Disk
disk=$(df -h . | awk 'NR==2 {print $5}')
echo "💾 Disk: $disk"

echo "======================"
