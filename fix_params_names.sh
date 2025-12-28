#!/bin/bash
echo "🔧 FIX NOMI PARAMETRI..."

cp quantum_v33_ultimate_final.py quantum_backup_params.py

# Sostituisci i parametri con i nomi corretti
sed -i '679,684c\        should_trade, confidence, score_info = self.fixes.fix_confidence_threshold(\
            fg=fear_index,\
            rsi=rsi,\
            pc=price_change_24h,\
            min_conf=45.0\
        )' quantum_v33_ultimate_final.py

echo "✅ Parametri corretti!"
echo ""
echo "🔍 Verifica 679-685..."
sed -n '679,685p' quantum_v33_ultimate_final.py

echo ""
echo "🚀 Test avvio (30 secondi)..."
timeout 35 python3 quantum_v33_ultimate_final.py 2>&1 | tail -40
