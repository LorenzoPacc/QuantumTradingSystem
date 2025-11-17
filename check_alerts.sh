#!/bin/bash
echo "🚨 QUANTUM SYSTEMS ALERT CHECK"
echo "=============================="

# Check if systems are running
if ! ps -p $(cat v21_pid.txt 2>/dev/null) >/dev/null 2>&1; then
    echo "❌ ALERT: V2.1 LIVE is not running!"
fi

if ! ps -p $(cat v30_pid.txt 2>/dev/null) >/dev/null 2>&1; then
    echo "❌ ALERT: V3.0 DRY-RUN is not running!"
fi

# Check for errors in logs
if grep -q "ERROR\|CRITICAL" v21_live.log 2>/dev/null; then
    echo "⚠️  V2.1 has errors in log. Check v21_live.log"
fi

if grep -q "ERROR\|CRITICAL" v30_dryrun.log 2>/dev/null; then
    echo "⚠️  V3.0 has errors in log. Check v30_dryrun.log"
fi

# Check performance
echo ""
echo "📊 Performance Status:"
python3 quantum_report.py 2>/dev/null | grep -E "(ROI:|Positions:)" | head -4

echo ""
echo "✅ Alert check completed at $(date)"
