#!/bin/bash

echo "🔍 VERIFICA INTEGRAZIONE QUANTUM SMART V3"
echo "========================================"

# Check file esistono
echo ""
echo "📁 File necessari:"
[ -f "quantum_smart_improvements.py" ] && echo "✅ quantum_smart_improvements.py" || echo "❌ quantum_smart_improvements.py MANCANTE"
[ -f "quantum_v3_enhanced.py" ] && echo "✅ quantum_v3_enhanced.py" || echo "❌ quantum_v3_enhanced.py MANCANTE"
[ -f "quantum_simple_fixed.py" ] && echo "✅ quantum_simple_fixed.py" || echo "❌ quantum_simple_fixed.py MANCANTE"

# Check import
echo ""
echo "🔧 Test import modulo:"
python3 -c "from quantum_smart_improvements import SmartTradingEngine; print('✅ Import OK')" 2>/dev/null || echo "❌ Import FALLITO"

# Check integrazione in quantum_v3_enhanced.py
echo ""
echo "🔍 Check integrazione in quantum_v3_enhanced.py:"

if grep -q "from quantum_smart_improvements import SmartTradingEngine" quantum_v3_enhanced.py 2>/dev/null; then
    echo "✅ Import SmartTradingEngine trovato"
else
    echo "❌ Import SmartTradingEngine NON trovato"
fi

if grep -q "self.smart_engine = SmartTradingEngine" quantum_v3_enhanced.py 2>/dev/null; then
    echo "✅ Inizializzazione SmartEngine trovata"
else
    echo "❌ Inizializzazione SmartEngine NON trovata"
fi

if grep -q "klines_5m = self.api.get_klines(symbol, '5m'" quantum_v3_enhanced.py 2>/dev/null; then
    echo "✅ Timeframe 5m configurato"
else
    echo "❌ Timeframe 5m NON configurato"
fi

# Check ciclo 5 minuti
echo ""
echo "⏱️  Check ciclo:"
if grep -q "time.sleep(300)" quantum_simple_fixed.py 2>/dev/null; then
    echo "✅ Ciclo 5 minuti (300s) configurato"
else
    echo "❌ Ciclo NON aggiornato a 5 minuti"
fi

echo ""
echo "========================================"
echo "Se tutti i check sono ✅, sei pronto!"
echo "Altrimenti, segui INTEGRATION_GUIDE.txt"
