#!/bin/bash
# QUANTUM V4 - UPGRADE SICURO E SEMPLICE
# Solo le modifiche che POSSIAMO fare con sed

echo "🔧 QUANTUM V4 - MINIMAL SAFE UPGRADE"
echo "====================================="

# 1. Backup
cp quantum_v33_ultimate_final.py quantum_v33_backup_$(date +%s).py
echo "✅ Backup creato"

# 2. Ferma il bot
pkill -f quantum_v33_ultimate_final.py 2>/dev/null
echo "✅ Bot fermato"

# 3. CONFIDENCE STANDARD 45%
echo "📊 Confidence → 45%"
sed -i 's/min_confidence=40\.0/min_confidence=45.0/g' quantum_v33_ultimate_final.py
sed -i 's/min_confidence=50\.0/min_confidence=45.0/g' quantum_v33_ultimate_final.py
sed -i 's/min_confidence=60\.0/min_confidence=45.0/g' quantum_v33_ultimate_final.py

# 4. RSI THRESHOLDS
echo "📈 RSI → 75/82"
sed -i 's/RSI_OVERBOUGHT = 70/RSI_OVERBOUGHT = 75/' quantum_v33_ultimate_final.py
sed -i 's/RSI_EXTREME_OVERBOUGHT = 85/RSI_EXTREME_OVERBOUGHT = 82/' quantum_v33_ultimate_final.py

# 5. Verifica sintassi
echo "🔍 Verifica sintassi..."
if python3 -m py_compile quantum_v33_ultimate_final.py; then
    echo "✅ Sintassi OK"
    
    # 6. Riavvia
    echo "🚀 Riavvio bot..."
    nohup python3 quantum_v33_ultimate_final.py > quantum_v33_ultimate_final.log 2>&1 &
    sleep 3
    
    # 7. Monitora
    echo ""
    echo "=========================================="
    echo "🎉 UPGRADE COMPLETATO!"
    echo ""
    echo "📊 MODIFICHE APPLICATE:"
    echo "   • Confidence: 45%"
    echo "   • RSI overbought: 75 (da 70)"
    echo "   • RSI extreme: 82 (da 85)"
    echo ""
    echo "📈 MONITORA:"
    echo "   tail -f quantum_v33_ultimate_final.log | grep -E 'Exposure|PARTIAL|Win Rate'"
    echo ""
    echo "🔧 MODIFICHE MANUALI OPZIONALI:"
    echo "   • Exposure cap 40%"
    echo "   • Sell parziali"
    echo "   • Enhanced logging"
    echo "   (Aggiungi DOPO se vedi miglioramenti)"
    echo "=========================================="
    
else
    echo "❌ Errori di sintassi! Ripristino backup..."
    cp quantum_v33_backup_*.py quantum_v33_ultimate_final.py
    echo "✅ Backup ripristinato"
fi
