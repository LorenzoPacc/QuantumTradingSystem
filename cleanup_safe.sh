#!/bin/bash
echo "🧹 QUANTUM CLEANUP - VERSIONE SICURA"
echo "===================================="

# Verifica directory
if [[ $(pwd) != *"QuantumTradingSystem"* ]]; then
    echo "❌ ERRORE: Non sei nella directory corretta!"
    exit 1
fi

echo "📊 Spazio prima: $(du -sh .)"

# SOLO operazioni SICURE:
echo ""
echo "🗑️  Pulizia SICURA in corso..."

# 1. Cache Python (SICURO)
echo "  → Cache Python..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# 2. File backup duplicati (SICURO - solo nella cartella corrente)
echo "  → File backup duplicati..."
rm -f quantum_trader_ultimate_final_ORIGINAL.py 2>/dev/null
rm -f quantum_trader_ultimate_final_FIXED.py 2>/dev/null  
rm -f quantum_trader_ultimate_final.py.backup* 2>/dev/null
rm -f quantum_trader_PRECISE.py 2>/dev/null
rm -f quantum_trader_FORCED*.py 2>/dev/null

# 3. Log vecchi (SICURO - mantieni production.log)
echo "  → Log vecchi..."
if [ -d "logs" ]; then
    find logs/ -name "*.log" -mtime +7 -delete 2>/dev/null
fi

echo ""
echo "📊 Spazio dopo: $(du -sh .)"
echo "✅ PULIZIA SICURA COMPLETATA!"
