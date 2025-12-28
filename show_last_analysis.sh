#!/bin/bash
echo "📊 ULTIMA ANALISI DEL BOT"
echo "========================"
echo ""

# Mostra le ultime righe con confidence
echo "🎯 Confidence scores (ultimi 5):"
tail -200 quantum_v33_ultimate_final.log | grep "Conf=" | tail -5

echo ""
echo "💼 Ultimo stato portfolio:"
tail -200 quantum_v33_ultimate_final.log | grep -A 6 "PORTFOLIO STATUS" | tail -7

echo ""
echo "⚠️  Eventuali errori recenti:"
tail -200 quantum_v33_ultimate_final.log | grep ERROR | tail -5

echo ""
echo "📈 Posizioni aperte nelle ultime ore:"
tail -1000 quantum_v33_ultimate_final.log | grep "Position opened" | tail -5

echo ""
echo "📉 Posizioni chiuse nelle ultime ore:"
tail -1000 quantum_v33_ultimate_final.log | grep "Position closed" | tail -5

echo ""
echo "⏰ Ultimo aggiornamento:"
tail -1 quantum_v33_ultimate_final.log
