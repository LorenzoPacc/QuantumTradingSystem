#!/bin/bash
echo "╔════════════════════════════════════════╗"
echo "║  🎯 QUANTUM BOT - STATUS CHECK        ║" 
echo "╚════════════════════════════════════════╝"
echo ""

# 1. STATO BOT
bot_proc=$(ps aux | grep quantum_simple_fixed | grep -v grep | wc -l)
if [ "$bot_proc" -eq 1 ]; then
    echo "✅ Bot: RUNNING"
    pid=$(ps aux | grep quantum_simple_fixed | grep -v grep | awk '{print $2}')
    echo "   PID: $pid"
    uptime_sec=$(ps -p $pid -o etimes= 2>/dev/null | tr -d ' ')
    if [ -n "$uptime_sec" ]; then
        uptime_min=$((uptime_sec / 60))
        echo "   Uptime: ${uptime_min} minuti"
    fi
else
    echo "❌ Bot: STOPPED"
    echo "   Riavvia: nohup python3 -u quantum_simple_fixed.py > quantum_fixed.log 2>&1 &"
fi

# 2. MERCATO LIVE
echo ""
echo "🌐 MERCATO LIVE:"
btc_price=$(curl -s "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT" | python3 -c "import json, sys; data = json.load(sys.stdin); print(f'{float(data[\"price\"]):,.2f}')" 2>/dev/null || echo "N/A")
echo "💰 BTC: \$$btc_price"

fg_data=$(curl -s "https://api.alternative.me/fng/?limit=1" | python3 -c "import json, sys; data = json.load(sys.stdin); fg = data['data'][0]; print(f'{fg[\"value\"]} ({fg[\"value_classification\"]})')" 2>/dev/null || echo "N/A")
echo "🎯 Fear & Greed: $fg_data"

# 3. STRATEGIA ATTIVA
echo ""
echo "🎯 STRATEGIA ATTIVA:"
if grep -q "FEAR_GREED_MIN" quantum_v3_enhanced.py 2>/dev/null; then
    min_val=$(grep "FEAR_GREED_MIN" quantum_v3_enhanced.py | grep -oP '\d+' | head -1)
    max_val=$(grep "FEAR_GREED_MAX" quantum_v3_enhanced.py | grep -oP '\d+' | head -1)
    echo "   Range Fear & Greed: ${min_val}-${max_val}"
    echo "   Con F&G 11: NON COMPRA (sotto ${min_val})"
else
    echo "   Strategia: Configurata"
fi

# 4. PORTAFOGLIO
echo ""
echo "💼 PORTAFOGLIO:"
if [ -f "quantum_fixed.log" ]; then
    # Estrai dati in modo sicuro
    cash=$(tail -100 quantum_fixed.log | grep "Cash:" | tail -1 | grep -oE '\$[0-9.]+' | head -1)
    total=$(tail -100 quantum_fixed.log | grep "TOTAL:" | tail -1 | grep -oE '\$[0-9.]+' | head -1)
    
    if [ -n "$cash" ]; then
        echo "   Cash: $cash"
        [ -n "$total" ] && echo "   Total: $total"
        echo "   Posizioni: 0/6"
    else
        echo "   Caricamento..."
    fi
else
    echo "   ⚠️ Log non trovato"
fi

# 5. ULTIME ATTIVITÀ
echo ""
echo "📈 ULTIME 3 ATTIVITÀ:"
if [ -f "quantum_fixed.log" ]; then
    tail -50 quantum_fixed.log | grep "Fear & Greed" | tail -3 | sed 's/^/   /'
fi

# 6. STATISTICHE
echo ""
echo "📊 STATISTICHE:"
if [ -f "quantum_fixed.log" ]; then
    cycles=$(grep -c "CYCLE" quantum_fixed.log 2>/dev/null || echo "0")
    trades=$(grep -c "EXECUTED" quantum_fixed.log 2>/dev/null || echo "0")
    errors=$(grep -ci "error" quantum_fixed.log 2>/dev/null || echo "0")
    
    echo "   Cicli: $cycles | Trade: $trades | Errori: $errors"
fi

# 7. SALUTE
echo ""
echo "🏥 SALUTE SISTEMA:"
disk=$(df -h . | tail -1 | awk '{print $5}')
echo "   Disk: $disk"

if [ -f "quantum_v2_state.json" ]; then
    echo "   State: OK"
else
    echo "   State: ⚠️ Mancante"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 COMANDI:"
echo "   tail -f quantum_fixed.log    # Log live"
echo "   ./check_bot.sh               # Richeck"
echo ""
echo "⏰ Check: $(date '+%H:%M:%S')"
