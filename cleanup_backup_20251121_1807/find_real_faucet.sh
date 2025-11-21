#!/bin/bash
echo "🔍 DOVE TROVARE IL FAUCET REALE"
echo "================================"
echo ""
echo "📍 CERCA IN QUESTI POSTI:"
echo ""
echo "1. 📱 TELEGRAM BOT (FUNZIONA SICURAMENTE):"
echo "   🔍 Cerca: @BinanceTestnetFaucetBot"
echo "   💬 Scrivi: /start"
echo "   🎯 Seleziona: USDT"
echo "   💰 Richiedi: 1000 USDT"
echo ""
echo "2. 🌐 URL DIRETTO:"
echo "   🔗 https://testnet.binance.vision/faucet"
echo "   (a volte nascosto, prova a ricaricare)"
echo ""
echo "3. 🔧 API DIRETTA:"
echo "   Prova questo comando curl:"
echo "   curl -X POST https://testnet.binance.vision/faucet/request \\"
echo "     -H 'X-MBX-APIKEY: YOUR_API_KEY' \\"
echo "     -d 'asset=USDT&amount=1000'"
echo ""
echo "4. 📧 SUPPORTO:"
echo "   Se nulla funziona:"
echo "   💌 support@binance.com"
echo "   🐛 Segnala bug faucet"
echo ""

read -p "Vuoi provare il Telegram Bot ORA? (s/n): " scelta
if [ "$scelta" = "s" ]; then
    echo "📱 APRÌ TELEGRAM E CERCA: @BinanceTestnetFaucetBot"
    echo "📍 Tornato qui dopo aver richiesto i fondi? (s/n): "
    read done
    if [ "$done" = "s" ]; then
        python3 test_api_finale.py
    fi
fi
