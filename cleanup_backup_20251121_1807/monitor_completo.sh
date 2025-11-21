#!/bin/bash
while true; do
    clear
    echo "🎯 QUANTUM TRADER - MONITOR LIVE"
    echo "================================"
    echo "🕒 $(date '+%H:%M:%S')"
    echo ""
    
    # STATO SISTEMA
    echo "📊 STATO SISTEMA:"
    if ps aux | grep "quantum_trader_ultimate_final.py" | grep -v grep > /dev/null; then
        echo "   ✅ TRADER: ATTIVO"
    else
        echo "   ❌ TRADER: FERMO"
    fi
    
    if ps aux | grep "streamlit" | grep -v grep > /dev/null; then
        echo "   ✅ DASHBOARD: ATTIVA (porta 8503)"
    else
        echo "   ❌ DASHBOARD: FERMA"
    fi
    
    # DATI REALI
    echo ""
    echo "💰 DATI REALI:"
    python3 << 'PYEOF'
import sqlite3
try:
    conn = sqlite3.connect('quantum_final.db')
    cursor = conn.cursor()
    
    # Balance
    cursor.execute("SELECT balance FROM balance_history ORDER BY timestamp DESC LIMIT 1")
    balance = cursor.fetchone()[0]
    print(f"   • Balance database: ${balance:.2f}")
    
    # Trade aperti
    cursor.execute("SELECT symbol, side, quantity, entry_price FROM open_positions")
    open_trades = cursor.fetchall()
    print(f"   • Trade aperti: {len(open_trades)}")
    for trade in open_trades:
        print(f"     {trade[0]} {trade[1]} | Entry: ${trade[3]:.2f}")
    
    # Trade totali
    cursor.execute("SELECT COUNT(*) FROM trades")
    total_trades = cursor.fetchone()[0]
    print(f"   • Trade totali: {total_trades}")
    
    conn.close()
except Exception as e:
    print(f"   • Errore database: {e}")
PYEOF
    
    # ULTIMI EVENTI
    echo ""
    echo "📝 ULTIMI EVENTI:"
    tail -10 trader.log 2>/dev/null | grep -E "BUY|SELL|TP_HIT|SL_HIT|ERROR|Balance" | tail -3 | while read line; do
        echo "   • $(echo $line | cut -c1-60)..."
    done
    
    echo ""
    echo "📍 URL: http://localhost:8503"
    echo "🔄 Aggiornamento in 30s... (Ctrl+C per fermare)"
    sleep 30
done
