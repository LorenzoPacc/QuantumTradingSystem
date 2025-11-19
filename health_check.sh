#!/bin/bash
echo "🏥 QUANTUM HEALTH CHECK"
echo "======================"

# 1. Processi
echo "📊 Processi:"
ps aux | grep -E "(quantum|python)" | grep -v grep | wc -l

# 2. File state sync
if diff quantum_v2_state.json quantum_v3_state.json >/dev/null 2>&1; then
    echo "✅ File state: SINCRONIZZATI"
else
    echo "❌ File state: NON SINCRONIZZATI!"
fi

# 3. Errori nei log
errors=$(tail -n 100 quantum_v2.log | grep -c "ERROR")
if [ $errors -eq 0 ]; then
    echo "✅ Log: NESSUN ERROR"
else
    echo "❌ Log: $errors ERRORI trovati"
fi

# 4. Cicli attivi
cycles=$(tail -n 50 quantum_v2.log | grep -c "CICLO")
if [ $cycles -gt 0 ]; then
    echo "✅ Cicli: ATTIVI ($cycles ultimi 50 log)"
else
    echo "❌ Cicli: NESSUN CICLO ATTIVO!"
fi

# 5. API funzionante
python3 -c "
from quantum_v31_wrapper import QuantumTraderV31
try:
    t = QuantumTraderV31(dry_run=True)
    price = t.api.get_price('BTCUSDT')
    if price and price > 0:
        print('✅ API: FUNZIONANTE')
    else:
        print('❌ API: NON FUNZIONANTE')
except Exception as e:
    print(f'❌ API: ERRORE - {e}')
"

echo "======================"
