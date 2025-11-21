#!/bin/bash
echo "🗄️  QUANTUM TRADING DATABASE"
echo "============================"
echo ""

# Crea directory database se non esiste
mkdir -p database

# File database
DB_FILE="database/trading_history.json"
CSV_FILE="database/trading_history.csv"

if [ ! -f "$DB_FILE" ]; then
    echo "📁 Creazione database..."
    echo '{"trades": [], "performance": {}, "created": "'$(date)'"}' > "$DB_FILE"
fi

# Estrai trade dai log e salva nel database
echo "📊 ESTRazione trade dai log..."
grep -E "ACQUISTATO|VENDUTO" quantum_your_strategy.log 2>/dev/null | while read line; do
    TIMESTAMP=$(echo "$line" | grep -o '202[0-9]-[0-9:-]*' | head -1)
    ACTION=$(echo "$line" | grep -o "ACQUISTATO\\|VENDUTO")
    SYMBOL=$(echo "$line" | grep -oE "[A-Z]{3,6}USDT")
    QUANTITY=$(echo "$line" | grep -oE "[0-9]+\.[0-9]+ [A-Z]" | head -1)
    PRICE=$(echo "$line" | grep -oE "\$[0-9]+\.[0-9]+" | sed 's/\$//')
    
    if [ ! -z "$TIMESTAMP" ] && [ ! -z "$ACTION" ]; then
        TRADE_JSON="{\"timestamp\": \"$TIMESTAMP\", \"action\": \"$ACTION\", \"symbol\": \"$SYMBOL\", \"quantity\": \"$QUANTITY\", \"price\": $PRICE}"
        echo "$TRADE_JSON" >> "$DB_FILE.tmp"
    fi
done

# Se ci sono nuovi trade, aggiorna il database
if [ -f "$DB_FILE.tmp" ]; then
    echo "🔄 Aggiornamento database..."
    # Qui andrebbe una logica più sofisticata per merge
    mv "$DB_FILE.tmp" "$DB_FILE"
fi

# Mostra contenuto database
echo ""
echo "📋 CONTENUTO DATABASE:"
if [ -f "$DB_FILE" ]; then
    jq '.' "$DB_FILE" 2>/dev/null || cat "$DB_FILE"
else
    echo "   Database vuoto"
fi

echo ""
echo "💾 File database: $DB_FILE"
