#!/bin/bash
echo "🧪 TEST COMPLETO DASHBOARD"
echo "==========================="

# Test connessione base
echo "1. 🔗 Test connessione base:"
if curl -s http://localhost:8000 > /dev/null; then
    echo "   ✅ Dashboard raggiungibile"
else
    echo "   ❌ Dashboard NON raggiungibile"
    exit 1
fi

# Test API Balance
echo ""
echo "2. 💰 Test API Balance:"
BALANCE_RESPONSE=$(curl -s http://localhost:8000/api/balance)
if echo "$BALANCE_RESPONSE" | grep -q "balance"; then
    BALANCE=$(echo "$BALANCE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['balance'])")
    echo "   ✅ API Balance funzionante: \$$BALANCE"
else
    echo "   ❌ API Balance non funzionante"
    echo "   Response: $BALANCE_RESPONSE"
fi

# Test API Trades
echo ""
echo "3. 📊 Test API Trades:"
TRADES_RESPONSE=$(curl -s http://localhost:8000/api/trades)
if echo "$TRADES_RESPONSE" | grep -q "trades"; then
    TRADE_COUNT=$(echo "$TRADES_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['trades']))")
    echo "   ✅ API Trades funzionante: $TRADE_COUNT trade trovati"
else
    echo "   ❌ API Trades non funzionante"
fi

# Test Health
echo ""
echo "4. ❤️  Test Health:"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/api/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "   ✅ Health check OK"
else
    echo "   ❌ Health check failed"
fi

# Test pagina principale
echo ""
echo "5. 🌐 Test pagina principale:"
HTML_RESPONSE=$(curl -s http://localhost:8000 | head -5)
if echo "$HTML_RESPONSE" | grep -q "DOCTYPE"; then
    echo "   ✅ Pagina HTML servita correttamente"
else
    echo "   ❌ Errore pagina HTML"
fi

echo ""
echo "🎉 TEST COMPLETATO!"
echo "🌐 Apri il browser su: http://localhost:8000"
