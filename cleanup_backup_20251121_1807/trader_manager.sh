#!/bin/bash
TRADER_SCRIPT="quantum_trader_production.py"
LOG_FILE="production.log"
PID_FILE="trader.pid"
case "$1" in
    start) echo "🚀 Avvio Quantum Trader..."; nohup python3 $TRADER_SCRIPT > $LOG_FILE 2>&1 & echo $! > $PID_FILE; echo "✅ Trader avviato (PID: $(cat $PID_FILE))";;
    stop) if [ -f "$PID_FILE" ]; then PID=$(cat $PID_FILE); kill $PID; rm -f $PID_FILE; echo "✅ Trader arrestato (PID: $PID)"; else echo "❌ Nessun trader attivo"; fi;;
    restart) $0 stop; sleep 2; $0 start;;
    status) if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then echo "✅ Trader ATTIVO (PID: $(cat $PID_FILE))"; tail -5 $LOG_FILE; else echo "❌ Trader NON attivo"; rm -f $PID_FILE; fi;;
    monitor) tail -f $LOG_FILE;;
    logs) tail -20 $LOG_FILE;;
    *) echo "Usage: $0 {start|stop|restart|status|monitor|logs}";;
esac
