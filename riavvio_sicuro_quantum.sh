#!/bin/bash
echo "🔧 RIAVVIO SICURO CON BACKUP"
echo "============================"

# =====================================================
# STEP 1: BACKUP COMPLETO (SEMPRE!)
# =====================================================
echo "📦 STEP 1: BACKUP DATI..."
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

cp quantum_trader.log "$BACKUP_DIR/" 2>/dev/null
cp quantum_state.json "$BACKUP_DIR/" 2>/dev/null
cp positions.db "$BACKUP_DIR/" 2>/dev/null
cp quantum_v2.log "$BACKUP_DIR/" 2>/dev/null

echo "✅ Backup salvato in: $BACKUP_DIR"
ls -lh "$BACKUP_DIR"

# =====================================================
# STEP 2: SALVA STATO ATTUALE POSIZIONE DOTUSDT
# =====================================================
echo ""
echo "💾 STEP 2: SALVO POSIZIONE DOTUSDT..."
cat > save_position.py << 'PYEOF'
import json
import os

# Leggi stato corrente
if os.path.exists('quantum_state.json'):
    with open('quantum_state.json', 'r') as f:
        state = json.load(f)
    
    print("📊 STATO CORRENTE:")
    print(f"   Cash: \${state.get('cash_balance', 0):.2f}")
    print(f"   Posizioni: {list(state.get('portfolio', {}).keys())}")
    
    # Salva in file separato
    with open('position_backup.json', 'w') as f:
        json.dump(state, f, indent=2)
    
    print("✅ Posizione salvata in position_backup.json")
else:
    print("⚠️  Nessun file state trovato")
PYEOF

python3 save_position.py

# =====================================================
# STEP 3: FORZA CHIUSURA PROCESSO
# =====================================================
echo ""
echo "🛑 STEP 3: CHIUSURA PROCESSO 10161..."
kill -9 10161
sleep 3

# Verifica che sia morto
if ps -p 10161 > /dev/null 2>&1; then
    echo "❌ Processo ancora vivo! Riprova..."
    exit 1
else
    echo "✅ Processo terminato"
fi

# Verifica nessun altro quantum attivo
ALTRI=$(pgrep -f "quantum_v31_wrapper" | wc -l)
if [ $ALTRI -gt 0 ]; then
    echo "⚠️  Trovati altri processi quantum, li fermo..."
    pkill -9 -f "quantum_v31_wrapper"
    sleep 2
fi

echo "✅ Tutti i processi quantum fermati"

# =====================================================
# STEP 4: PREPARA AMBIENTE (SENZA CANCELLARE I LOG!)
# =====================================================
echo ""
echo "🧹 STEP 4: PREPARO AMBIENTE..."

# NON cancellare i log, spostali
if [ -f quantum_trader.log ]; then
    mv quantum_trader.log "quantum_trader_old_$(date +%Y%m%d_%H%M).log"
    echo "✅ Log vecchio spostato"
fi

# Rimuovi solo lock files (non i log!)
rm -f *.lock 2>/dev/null
echo "✅ Lock files rimossi"

# Crea nuovo file log vuoto
touch quantum_trader.log
echo "✅ Nuovo log creato"

# =====================================================
# STEP 5: VERIFICA STATE (NON RIGENERARE SE ESISTE!)
# =====================================================
echo ""
echo "🔍 STEP 5: VERIFICA STATE FILE..."

if [ ! -f quantum_state.json ]; then
    echo "⚠️  State file mancante, rigenero..."
    cat > quantum_state.json << 'JSONEOF'
{
  "cash_balance": 173.91,
  "portfolio": {
    "DOTUSDT": {
      "quantity": 7.11,
      "entry_price": 2.72,
      "current_price": 2.73,
      "total_cost": 19.34,
      "trailing_stop": 2.6928,
      "stop_active": true
    }
  },
  "portfolio_value": 193.25,
  "initial_capital": 200.00,
  "dry_run": true
}
JSONEOF
    echo "✅ State rigenerato CON posizione DOTUSDT"
else
    echo "✅ State file esistente mantenuto"
fi

# =====================================================
# STEP 6: TEST INIZIALIZZAZIONE (SENZA LOOP)
# =====================================================
echo ""
echo "🧪 STEP 6: TEST INIZIALIZZAZIONE..."

cat > test_init.py << 'PYEOF'
#!/usr/bin/env python3
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

try:
    print("🔄 Carico QuantumTraderV31...")
    from quantum_v31_wrapper import QuantumTraderV31
    
    print("🎯 Inizializzo trader...")
    trader = QuantumTraderV31(dry_run=True)
    
    print("✅ TRADER INIZIALIZZATO CON SUCCESSO!")
    print(f"💰 Cash: \${trader.cash_balance:.2f}")
    print(f"📊 Posizioni: {len(trader.portfolio)}")
    
    if trader.portfolio:
        for symbol, pos in trader.portfolio.items():
            print(f"   🟢 {symbol}: {pos.get('quantity', 0)} unità @ \${pos.get('entry_price', 0):.2f}")
    
    print("\n🧪 Test ciclo singolo...")
    trader.run_cycle()
    print("✅ CICLO COMPLETATO!")
    
    sys.exit(0)
    
except Exception as e:
    print(f"❌ ERRORE: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF

python3 test_init.py
TEST_RESULT=$?

if [ $TEST_RESULT -ne 0 ]; then
    echo ""
    echo "❌ ERRORE NEL TEST! Non avvio il bot."
    echo "🔍 Controlla l'output sopra per il motivo."
    exit 1
fi

# =====================================================
# STEP 7: AVVIO DEFINITIVO
# =====================================================
echo ""
echo "🚀 STEP 7: AVVIO BOT..."

nohup python3 quantum_v31_wrapper.py --dry-run > quantum_startup.log 2>&1 &
NEW_PID=$!

echo "✅ Bot avviato - PID: $NEW_PID"
echo "⏳ Attendo 10 secondi..."
sleep 10

# =====================================================
# STEP 8: VERIFICA FINALE
# =====================================================
echo ""
echo "📊 STEP 8: VERIFICA FINALE..."

# Controlla processo
if ps -p $NEW_PID > /dev/null; then
    echo "✅ Processo vivo (PID: $NEW_PID)"
else
    echo "❌ Processo morto! Controlla quantum_startup.log"
    exit 1
fi

# Controlla log recenti
echo ""
echo "📋 ULTIMI LOG:"
tail -10 quantum_trader.log 2>/dev/null || echo "⚠️  Nessun log ancora generato"

# Status
echo ""
echo "🎯 STATUS:"
./quantum_status.sh

echo ""
echo "✅ RIAVVIO COMPLETATO!"
echo ""
echo "💡 COMANDI UTILI:"
echo "   📋 Monitora log: tail -f quantum_trader.log"
echo "   📊 Status: ./quantum_status.sh"
echo "   🏥 Health: ./health_check.sh"
echo "   🔍 Backup: ls -lh $BACKUP_DIR"
