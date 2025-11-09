#!/bin/bash
echo "🔐 CONFIGURAZIONE COMPLETA API KEYS BINANCE TESTNET"
echo "==================================================="
echo ""

echo "📋 PASSO 1: Ottieni le API Keys da Binance Testnet"
echo "   🌐 Vai su: https://testnet.binance.vision/"
echo "   👤 Fai login con GitHub"
echo "   🔑 Clicca 'Generate API Key'"
echo "   📝 Copia API Key e Secret Key"
echo ""

echo "📋 PASSO 2: Modifica il file .env.testnet"
echo "   ✏️  Sostituisci: EXyS3Fvmsrb9pCKjQMuJSlLiUIWYih5JiglIsiRzvLDR2tzJS60r3DXzknca0FC1"
echo "   ✏️  Sostituisci: yvPlsaFwUg8XaBejUmptovSRH3XjQ6lOeGTRwbDprV2tAXs5naD6y1dsWbcmb2aI"
echo "   Con le tue chiavi REALI"
echo ""

# Mostra il file attuale
echo "📄 CONTENUTO ATTUALE di .env.testnet:"
echo "--------------------------------------"
cat .env.testnet
echo "--------------------------------------"
echo ""

read -p "Vuoi modificare il file ORA? (s/n): " scelta

if [ "$scelta" = "s" ] || [ "$scelta" = "S" ]; then
    nano .env.testnet
    echo "✅ File modificato!"
else
    echo "❌ Ricorda di modificare il file prima di usare l'Auto Trader!"
    echo "   Comando: nano .env.testnet"
fi

echo ""
echo "📋 PASSO 3: Test delle API Keys"
echo "   Esegui: python3 test_api_keys.py"
echo ""
