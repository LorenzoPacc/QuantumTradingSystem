#!/bin/bash
echo "📈 MONITOR PROGRESSI - LA TUA STRATEGIA"
echo "========================================"
echo "Sistema in esecuzione per 30 cicli (~5 ore)"
echo ""

cycle_count=0
trade_count=0
last_portfolio=10000.00

while true; do
    clear
    echo "🕒 $(date)"
    echo "=========================================="
    
    # Conta cicli completati
    current_cycles=$(grep -c "FINE CICLO" quantum_your_strategy.log 2>/dev/null || echo 0)
    current_trades=$(grep -c "ACQUISTATO\\|VENDUTO" quantum_your_strategy.log 2>/dev/null || echo 0)
    
    echo "📊 PROGRESSO: $current_cycles/30 cicli completati"
    echo "🔄 TRADE: $current_trades operazioni eseguite"
    
    # Ultime decisioni
    echo ""
    echo "🎯 ULTIME DECISIONI:"
    tail -8 quantum_your_strategy.log 2>/dev/null | grep -E "DECISIONE:|ANALISI CONFLUENZE" | tail -3 | sed 's/.*INFO - //'
    
    # Performance corrente
    echo ""
    echo "💰 PERFORMANCE CORRENTE:"
    portfolio_line=$(tail -20 quantum_your_strategy.log 2>/dev/null | grep "Portfolio:" | tail -1)
    cash_line=$(tail -20 quantum_your_strategy.log 2>/dev/null | grep "Cash:" | tail -1)
    
    if [ ! -z "$portfolio_line" ]; then
        echo "$portfolio_line" | sed 's/.*INFO - //'
        echo "$cash_line" | sed 's/.*INFO - //'
    else
        echo "   In attesa di dati..."
    fi
    
    # Stima tempo rimanente
    if [ $current_cycles -gt 0 ]; then
        minutes_per_cycle=10
        cycles_remaining=$((30 - current_cycles))
        minutes_remaining=$((cycles_remaining * minutes_per_cycle))
        hours=$((minutes_remaining / 60))
        minutes=$((minutes_remaining % 60))
        
        echo ""
        echo "⏳ TEMPO STIMATO: ${hours}h ${minutes}m rimanenti"
    fi
    
    echo ""
    echo "🔍 Per dettagli completi: tail -f quantum_your_strategy.log"
    echo "⏰ Prossimo aggiornamento in 60 secondi..."
    echo "   Ctrl+C per uscire dal monitor"
    
    sleep 60
done
