#!/bin/bash
echo "🚀 Avvio bot con output filtrato..."

pkill -f quantum_v33 2>/dev/null

python3 quantum_v33_ultimate_final.py 2>&1 | \
grep -v "klines" | \
grep -v "GET https://api" | \
grep -v "Response: 200" | \
grep -v '^\[\[' | \
while read line; do
    if echo "$line" | grep -qi "error"; then
        echo -e "\033[1;31m$line\033[0m"
    elif echo "$line" | grep -q "Conf="; then
        echo -e "\033[0;33m$line\033[0m"
    elif echo "$line" | grep -q "PORTFOLIO"; then
        echo -e "\033[1;36m$line\033[0m"
    else
        echo "$line"
    fi
done
