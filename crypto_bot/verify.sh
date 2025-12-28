#!/bin/bash

echo "🔍 VERIFICA SETUP"
echo "================="

errors=0

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 non trovato"
    ((errors++))
else
    echo "✅ Python3: $(python3 --version)"
fi

# Check files
required_files=("strategy.py" "backtest.py" "config/config.yaml" "requirements.txt")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file presente"
    else
        echo "❌ $file mancante"
        ((errors++))
    fi
done

# Check .env
if [ -f ".env" ]; then
    echo "✅ .env configurato"
else
    echo "⚠️  .env non trovato (crea per API keys)"
fi

echo ""
if [ $errors -eq 0 ]; then
    echo "✅ Setup completo! Esegui: python backtest.py"
else
    echo "❌ $errors errori trovati"
    exit 1
fi
