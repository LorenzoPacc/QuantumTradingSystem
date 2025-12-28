#!/bin/bash
echo "🔍 MONITOR BOT - Mostra solo le info importanti"
echo "================================================"
echo ""

# Segui il log filtrando solo le righe rilevanti
tail -f quantum_v33_ultimate_final.log 2>/dev/null | grep --line-buffered -E "(INFO.*PORTFOLIO|Conf=|BUY|SELL|ERROR|Position opened|Position closed)" | while read line; do
    # Colora le righe importanti
    if echo "$line" | grep -q "BUY"; then
        echo -e "\033[0;32m$line\033[0m"  # Verde per BUY
    elif echo "$line" | grep -q "SELL"; then
        echo -e "\033[0;31m$line\033[0m"  # Rosso per SELL
    elif echo "$line" | grep -q "ERROR"; then
        echo -e "\033[1;31m$line\033[0m"  # Rosso bold per ERROR
    elif echo "$line" | grep -q "Conf="; then
        echo -e "\033[0;33m$line\033[0m"  # Giallo per confidence
    else
        echo "$line"
    fi
done
