#!/bin/bash
echo "💰 FAUCET UFFICIALE BINANCE TESTNET"
echo "==================================="
echo ""
echo "📍 PASSO 1: Vai su: https://testnet.binance.vision/"
echo "📍 PASSO 2: Fai login con GitHub"
echo "📍 PASSO 3: CERCA 'Faucet' in ALTO A DESTRA"
echo "📍 PASSO 4: Se non vedi 'Faucet', usa il METODO ALTERNATIVO qui sotto ⬇️"
echo ""
echo "🎯 METODO ALTERNATIVO GARANTITO:"
echo "1. 🌐 Vai su: https://testnet.binance.vision/"
echo "2. 🔑 Clicca sulle tue iniziali in alto a destra"
echo "3. 🏦 Clicca 'Faucet' o 'Wallet'"
echo "4. 💰 Seleziona USDT e richiedi 1000"
echo ""
read -p "Vuoi che proviamo il metodo API diretto? (s/n): " scelta
if [ "$scelta" = "s" ]; then
    echo "🔄 Provando metodo API..."
    API_KEY=$(cat .env.testnet | grep API_KEY | cut -d'=' -f2)
    curl -X POST "https://testnet.binance.vision/api/v3/order/test" \
         -H "X-MBX-APIKEY: $API_KEY" \
         -d "symbol=BTCUSDT&side=BUY&type=MARKET&quantity=0.001"
    echo ""
    echo "📍 Se funziona, hai i fondi. Se da errore, non hai fondi."
fi
