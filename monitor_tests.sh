#!/bin/bash
# Monitor test progress

clear
echo "📊 QUANTUM TRADING V34 - TEST MONITOR"
echo "========================================================================"
echo ""

while true; do
    clear
    echo "📊 TEST MONITOR - $(date)"
    echo "========================================================================"
    echo ""
    
    # Check running processes
    echo "🔄 PROCESSI ATTIVI:"
    if [ -f test_results/test_tracker.txt ]; then
        while IFS=: read -r version pid starttime; do
            if ps -p "$pid" > /dev/null 2>&1; then
                runtime=$(ps -p "$pid" -o etime= | xargs)
                echo "   ✅ $version (PID: $pid, Runtime: $runtime)"
            else
                echo "   ❌ $version (PID: $pid, STOPPED)"
            fi
        done < test_results/test_tracker.txt
    fi
    
    echo ""
    echo "📈 PERFORMANCE SNAPSHOT:"
    echo "========================================================================"
    
    # MTF 40%
    if [ -f test_results/mtf40/test.log ]; then
        echo ""
        echo "VERSION 1: MTF 40%"
        tail -50 test_results/mtf40/test.log | grep -E "Total PnL:|Win Rate:|Trades:" | tail -3
        echo "   Latest cycle:"
        tail -5 test_results/mtf40/test.log | grep CYCLE | tail -1
    fi
    
    # Inverted
    if [ -f test_results/inverted/test.log ]; then
        echo ""
        echo "VERSION 2: Inverted Logic"
        tail -50 test_results/inverted/test.log | grep -E "Total PnL:|Win Rate:|Trades:" | tail -3
        echo "   Latest cycle:"
        tail -5 test_results/inverted/test.log | grep CYCLE | tail -1
    fi
    
    # Simple
    if [ -f test_results/simple/test.log ]; then
        echo ""
        echo "VERSION 3: Simple Strategy"
        tail -20 test_results/simple/test.log
    fi
    
    echo ""
    echo "========================================================================"
    echo "🔄 Auto-refresh ogni 30 secondi... (Ctrl+C per uscire)"
    echo "========================================================================"
    
    sleep 30
done

