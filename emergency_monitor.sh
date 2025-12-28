#!/bin/bash
LOG_FILE=~/trading_project/QuantumTradingSystem/quantum_v33_ultimate_final.log
ALERT_FILE=~/emergency_alerts.log
BOT_FILE="quantum_v33_ultimate_final.py"
echo "🛡️ Emergency Monitor Started: $(date)" | tee -a "$ALERT_FILE"
while true; do
    if ! pgrep -f "$BOT_FILE" > /dev/null; then
        sleep 60; continue
    fi
    PNL=$(tail -100 "$LOG_FILE" 2>/dev/null | grep "Total PnL" | tail -1 | grep -oP "[-\d.]+" | head -2 | tail -1 || echo "0")
    FG=$(tail -50 "$LOG_FILE" 2>/dev/null | grep "Fear & Greed" | tail -1 | grep -oP "Fear & Greed: \K\d+" || echo "50")
    DD=$(tail -100 "$LOG_FILE" 2>/dev/null | grep "Max Drawdown" | tail -1 | grep -oP "\d+\.\d+" || echo "0")
    SHOULD_STOP=false
    if [ ! -z "$FG" ] && [ "$FG" -lt 20 ]; then SHOULD_STOP=true; TRIGGER_REASON="FEAR<20"; fi
    if [ ! -z "$PNL" ] && (( $(echo "$PNL < -9" | bc -l 2>/dev/null || echo 0) )); then SHOULD_STOP=true; TRIGGER_REASON="PNL<-9%"; fi
    if [ ! -z "$DD" ] && (( $(echo "$DD > 12" | bc -l 2>/dev/null || echo 0) )); then SHOULD_STOP=true; TRIGGER_REASON="DD>12%"; fi
    if [ "$SHOULD_STOP" = true ]; then
        echo "🚨 EMERGENCY STOP: $TRIGGER_REASON at $(date)" | tee -a "$ALERT_FILE"
        echo "Metrics: Fear=$FG | PnL=$PNL% | DD=$DD%" | tee -a "$ALERT_FILE"
        pkill -f "$BOT_FILE"; sleep 2
        ~/qv4snapshot > ~/emergency_snapshot_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null
        exit 0
    fi
    sleep 300
done
