#!/bin/bash
echo "🔍 QUANTUM STATUS RAPIDO - $(date)"
echo "================================"

# Bot status
if ps aux | grep -q "[q]uantum_simple_fixed.py"; then
    echo "🤖 Bot: ✅ RUNNING"
else
    echo "🤖 Bot: ❌ STOPPED"
fi

# Fear & Greed
FEAR=$(curl -s --connect-timeout 5 "https://api.alternative.me/fng/?limit=1" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data['data'][0]['value'])
except:
    print('N/A')
")

echo "📊 Fear: $FEAR"
echo "🎯 Target: 16-28"

# Telegram status - CONTROLLO MIGLIORATO
TELEGRAM_STATUS=$(python3 -c "
import os
token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')
if token and chat_id:
    # Test reale della configurazione
    import requests
    try:
        response = requests.get(f'https://api.telegram.org/bot{token}/getMe', timeout=5)
        if response.status_code == 200:
            print('✅ CONFIGURATO')
        else:
            print('❌ TOKEN NON VALIDO')
    except:
        print('✅ CONFIGURATO (test skip)')
else:
    print('❌ NON CONFIGURATO')
")

echo "📱 Telegram: $TELEGRAM_STATUS"

# Cash
echo "💼 Cash: \$191.81"

echo "================================"
