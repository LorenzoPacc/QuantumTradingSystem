#!/bin/bash
echo "🛑 QUANTUM TRADING SYSTEMS - SHUTDOWN SCRIPT"
echo "============================================"

echo "🔍 Stopping processes..."
pkill -f "quantum_v2_1_complete.py"
pkill -f "quantum_v3_mvp.py"

sleep 2

# Verify shutdown
V21_PID=$(pgrep -f "quantum_v2_1_complete.py")
V30_PID=$(pgrep -f "quantum_v3_mvp.py")

if [ -z "$V21_PID" ] && [ -z "$V30_PID" ]; then
    echo "✅ All Quantum systems stopped"
else
    echo "⚠️  Some processes still running:"
    [ ! -z "$V21_PID" ] && echo "   V2.1: $V21_PID"
    [ ! -z "$V30_PID" ] && echo "   V3.0: $V30_PID"
    echo "   Use 'pkill -9 -f quantum' for force stop"
fi

# Cleanup PID files
rm -f v21_pid.txt v30_pid.txt
