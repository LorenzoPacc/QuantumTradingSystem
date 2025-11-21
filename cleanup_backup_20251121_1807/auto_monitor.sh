#!/bin/bash
echo "🤖 QUANTUM AUTO-MONITOR SYSTEM"
echo "=============================="

while true; do
    clear
    echo "$(date) - Quantum Auto-Monitor"
    echo "=============================="
    
    # Check if systems are running
    V21_RUNNING=$(ps -p $(cat v21_pid.txt 2>/dev/null) >/dev/null 2>&1 && echo "🟢" || echo "🔴")
    V30_RUNNING=$(ps -p $(cat v30_pid.txt 2>/dev/null) >/dev/null 2>&1 && echo "🟢" || echo "🔴")
    
    echo "System Status:"
    echo "  V2.1 LIVE:    $V21_RUNNING"
    echo "  V3.0 DRY-RUN: $V30_RUNNING"
    echo ""
    
    # Show recent activity
    echo "Recent Activity:"
    if [ "$V21_RUNNING" = "🟢" ]; then
        echo "  V2.1: $(tail -1 v21_live.log 2>/dev/null | cut -c-50)"
    else
        echo "  V2.1: ❌ Not running"
    fi
    
    if [ "$V30_RUNNING" = "🟢" ]; then
        echo "  V3.0: $(tail -1 v30_dryrun.log 2>/dev/null | cut -c-50)" 
    else
        echo "  V3.0: ❌ Not running"
    fi
    
    echo ""
    echo "Performance Summary:"
    python3 quantum_report.py 2>/dev/null | grep -E "(💰 Total Value|📈 ROI|📊 Positions)" | head -6
    
    echo ""
    echo "⏱️  Auto-refresh in 30s (Ctrl+C to stop)"
    sleep 30
done
