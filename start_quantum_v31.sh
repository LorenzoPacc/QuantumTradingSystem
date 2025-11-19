#!/bin/bash

echo "🚀 AVVIO QUANTUM V3.1 - TRAILING STOP EDITION"
echo "=============================================="

# Verifica file necessari
if [ ! -f "quantum_v31_wrapper.py" ]; then
    echo "❌ ERRORE: quantum_v31_wrapper.py non trovato!"
    echo "   Assicurati di aver creato i file necessari"
    exit 1
fi

if [ ! -f "quantum_trailing_stop.py" ]; then
    echo "❌ ERRORE: quantum_trailing_stop.py non trovato!"
    exit 1
fi

# Modalità dry-run di default (SICUREZZA)
DRY_RUN="--dry-run"
MODE="DRY-RUN"

if [ "$1" == "--live" ]; then
    DRY_RUN=""
    MODE="LIVE"
    echo "⚠️  ATTENZIONE: MODALITÀ LIVE ATTIVATA"
    read -p "Sei sicuro di voler continuare? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "❌ Operazione annullata"
        exit 1
    fi
else
    echo "🔒 MODALITÀ DRY-RUN ATTIVA (Sicura)"
fi

echo ""
echo "🎯 CONFIGURAZIONE:"
echo "   - Trailing Stop: ATTIVO"
echo "   - Activation: +2%"
echo "   - Trailing: -1% dal picco" 
echo "   - Min Lock: +1.5%"
echo "   - Modalità: $MODE"
echo ""
echo "🚀 AVVIO IN CORSO..."
echo "=========================================="

# Avvia Quantum V3.1
python3 quantum_v31_wrapper.py $DRY_RUN --capital 200
