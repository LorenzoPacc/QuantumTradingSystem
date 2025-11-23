#!/bin/bash

echo "🧪 TEST QUANTUM SMART V3 - DRY RUN"
echo "=================================="
echo ""
echo "Questo script testa il bot per 30 secondi"
echo "e mostra i log in tempo reale."
echo ""
echo "Premi CTRL+C per interrompere"
echo ""
sleep 2

# Kill bot esistente se presente
if pgrep -f "quantum_simple_fixed.py" > /dev/null; then
    echo "⚠️  Bot già in esecuzione, arresto..."
    pkill -f "quantum_simple_fixed.py"
    sleep 2
fi

# Pulisci log
> quantum_fixed.log

echo "🚀 Avvio bot in test mode..."
echo ""

# Avvia bot e mostra log
timeout 30 python3 quantum_simple_fixed.py &
BOT_PID=$!

sleep 3

echo "📊 LOG IN TEMPO REALE (30 secondi):"
echo "===================================="
tail -f quantum_fixed.log &
TAIL_PID=$!

# Aspetta 30 secondi
sleep 30

# Cleanup
kill $TAIL_PID 2>/dev/null
kill $BOT_PID 2>/dev/null

echo ""
echo "===================================="
echo "✅ Test completato!"
echo ""
echo "📊 Controlla quantum_fixed.log per i dettagli"
echo "🔍 Verifica che:"
echo "   - Non ci siano errori Import"
echo "   - I timeframe 5m, 15m, 1h siano caricati"
echo "   - I filtri smart siano applicati"
