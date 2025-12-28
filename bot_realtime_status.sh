#!/bin/bash

echo "🤖 QUANTUM BOT - REAL-TIME STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Ultimo ciclo (parte dalla fine!)
echo "🔄 ULTIMO CICLO:"
tac quantum_v33_ultimate_final.log | grep -m 1 "CYCLE.*- 2025" | awk '{print $1, $2, $5, $6, $7, $8}'

echo ""
echo "💰 ULTIMO PORTFOLIO:"
tac quantum_v33_ultimate_final.log | grep -m 1 "Total PnL:" 

echo ""
echo "📊 STATE FILE:"
ls -lh qv33_ultimate_final_state.json | awk '{print "Size:", $5, "| Updated:", $6, $7, $8}'

echo ""
echo "🔴 ULTIMI 3 SELL:"
tac quantum_v33_ultimate_final.log | grep "🔴 SELL" -m 3 | tac

echo ""
echo "🟢 ULTIMI 3 BUY:"
tac quantum_v33_ultimate_final.log | grep "🟢 BUY" -m 3 | tac

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
