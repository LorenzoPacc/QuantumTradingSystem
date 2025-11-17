#!/bin/bash
echo "🚀 QUANTUM TRADING SYSTEMS - STARTUP SCRIPT"
echo "==========================================="
echo ""

# Check if systems are already running
echo "🔍 Checking existing processes..."
V21_PID=$(pgrep -f "quantum_v2_1_complete.py")
V30_PID=$(pgrep -f "quantum_v3_mvp.py")

if [ ! -z "$V21_PID" ]; then
    echo "⚠️  V2.1 already running (PID: $V21_PID)"
else
    echo "✅ Starting V2.1 LIVE..."
    nohup python3 quantum_v2_1_complete.py > v21_live.log 2>&1 &
    echo $! > v21_pid.txt
    echo "   📁 Log: v21_live.log"
    echo "   📄 PID: $(cat v21_pid.txt)"
fi

if [ ! -z "$V30_PID" ]; then
    echo "⚠️  V3.0 already running (PID: $V30_PID)" 
else
    echo "✅ Starting V3.0 DRY-RUN..."
    nohup python3 quantum_v3_mvp.py --dry-run --capital 200 > v30_dryrun.log 2>&1 &
    echo $! > v30_pid.txt
    echo "   📁 Log: v30_dryrun.log"
    echo "   📄 PID: $(cat v30_pid.txt)"
fi

echo ""
echo "🎯 SYSTEMS STATUS:"
echo "   V2.1 LIVE:    $(ps -p $(cat v21_pid.txt 2>/dev/null) >/dev/null 2>&1 && echo '🟢 RUNNING' || echo '🔴 STOPPED')"
echo "   V3.0 DRY-RUN: $(ps -p $(cat v30_pid.txt 2>/dev/null) >/dev/null 2>&1 && echo '🟢 RUNNING' || echo '🔴 STOPPED')"

echo ""
echo "📊 To monitor performance: ./monitor_v2_v3.sh"
echo "🛑 To stop all systems: ./stop_quantum_systems.sh"
