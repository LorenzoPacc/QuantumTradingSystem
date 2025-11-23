#!/bin/bash
echo ""
echo "🎯 TELEGRAM PRO - SETUP ULTRA-SEMPLICE"
echo "========================================"
echo ""

# Verifica se già configurato
if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    echo "✅ Telegram già configurato!"
    echo "   Token: ...${TELEGRAM_BOT_TOKEN: -10}"
    echo "   Chat ID: $TELEGRAM_CHAT_ID"
    echo ""
    echo "🧪 Test sistema..."
    python3 telegram_pro.py
    exit 0
fi

echo "📱 PASSO 1: Crea Bot Telegram"
echo "   • Cerca @BotFather"
echo "   • /newbot"
echo "   • Scegli nome"
echo "   • Copia TOKEN"
echo ""
read -p "🤖 Incolla TOKEN: " token

echo ""
echo "📱 PASSO 2: Ottieni Chat ID"  
echo "   • Cerca @userinfobot"
echo "   • /start"
echo "   • Copia ID numerico"
echo ""
read -p "💬 Incolla CHAT_ID: " chatid

# Salva configurazione
echo "" >> ~/.bashrc
echo "# Quantum Trading Bot - Telegram" >> ~/.bashrc
echo "export TELEGRAM_BOT_TOKEN=\"$token\"" >> ~/.bashrc
echo "export TELEGRAM_CHAT_ID=\"$chatid\"" >> ~/.bashrc

# Applica immediatamente
export TELEGRAM_BOT_TOKEN="$token"
export TELEGRAM_CHAT_ID="$chatid"

echo ""
echo "✅ CONFIGURAZIONE COMPLETATA!"
echo ""
echo "🧪 TEST FINALE..."
python3 telegram_pro.py

echo ""
echo "🚀 PROSSIMI PASSI:"
echo "   1. Il sistema Telegram è pronto"
echo "   2. Riavvia il bot trading per integrare"
echo "   3. Riceverai notifiche automatiche"
echo ""
echo "🔄 Comando riavvio bot:"
echo "   pkill -f quantum_simple_fixed.py; sleep 2; nohup python3 -u quantum_simple_fixed.py > quantum_fixed.log 2>&1 &"
echo ""
