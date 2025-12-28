#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        🔍 TEST TUTTI I COMANDI - AUDIT COMPLETO            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ═══════════════════════════════════════════════════════════════════
# 📊 GESTIONE BOT
# ═══════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 1. GESTIONE BOT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test ~/qstatus
if [ -f ~/qstatus ]; then
    echo "✅ ~/qstatus - ESISTE"
    echo "   Descrizione: Check veloce stato bot"
else
    echo "❌ ~/qstatus - NON TROVATO"
fi

# Test ~/qstart
if [ -f ~/qstart ]; then
    echo "✅ ~/qstart - ESISTE"
    echo "   Descrizione: Avvia bot"
else
    echo "❌ ~/qstart - NON TROVATO"
fi

# Test ~/qstop
if [ -f ~/qstop ]; then
    echo "✅ ~/qstop - ESISTE"
    echo "   Descrizione: Ferma bot"
else
    echo "❌ ~/qstop - NON TROVATO"
fi

# Test ~/qrestart
if [ -f ~/qrestart ]; then
    echo "✅ ~/qrestart - ESISTE"
    echo "   Descrizione: Riavvia bot"
else
    echo "❌ ~/qrestart - NON TROVATO"
fi

# Test ps aux
if ps aux | grep quantum_v33 | grep -v grep > /dev/null 2>&1; then
    echo "✅ ps aux | grep quantum - FUNZIONA"
    echo "   Bot attivo: SÌ"
else
    echo "⚠️  ps aux | grep quantum - Bot non attivo"
fi

echo ""

# ═══════════════════════════════════════════════════════════════════
# 📈 MONITORING
# ═══════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📈 2. MONITORING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test ~/qv4snapshot
if [ -f ~/qv4snapshot ]; then
    echo "✅ ~/qv4snapshot - ESISTE"
    echo "   Descrizione: Portfolio e posizioni live"
else
    echo "❌ ~/qv4snapshot - NON TROVATO"
fi

# Test ~/qmonitor
if [ -f ~/qmonitor ]; then
    echo "✅ ~/qmonitor - ESISTE"
    echo "   Descrizione: Log live colorato"
else
    echo "❌ ~/qmonitor - NON TROVATO"
fi

# Test log file
if [ -f quantum_v33_ultimate_final.log ]; then
    echo "✅ quantum_v33_ultimate_final.log - ESISTE"
    LOG_SIZE=$(du -h quantum_v33_ultimate_final.log | awk '{print $1}')
    echo "   Size: $LOG_SIZE"
else
    echo "❌ quantum_v33_ultimate_final.log - NON TROVATO"
fi

# Test bug_timeline.sh
if [ -f ./bug_timeline.sh ]; then
    echo "✅ ./bug_timeline.sh - ESISTE"
    echo "   Descrizione: Controllo bug sistema"
else
    echo "❌ ./bug_timeline.sh - NON TROVATO"
fi

echo ""

# ═══════════════════════════════════════════════════════════════════
# 🔧 UTILITÀ
# ═══════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 3. UTILITÀ"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test ~/qbackup
if [ -f ~/qbackup ]; then
    echo "✅ ~/qbackup - ESISTE"
    echo "   Descrizione: Backup locale"
else
    echo "❌ ~/qbackup - NON TROVATO"
fi

# Test ~/qgithub
if [ -f ~/qgithub ]; then
    echo "✅ ~/qgithub - ESISTE"
    echo "   Descrizione: Push GitHub"
else
    echo "❌ ~/qgithub - NON TROVATO"
fi

# Test ~/qgitstatus
if [ -f ~/qgitstatus ]; then
    echo "✅ ~/qgitstatus - ESISTE"
    echo "   Descrizione: Status Git"
else
    echo "❌ ~/qgitstatus - NON TROVATO"
fi

# Test ~/qclean
if [ -f ~/qclean ]; then
    echo "✅ ~/qclean - ESISTE"
    echo "   Descrizione: Pulizia"
else
    echo "❌ ~/qclean - NON TROVATO"
fi

# Test comprehensive_audit.sh
if [ -f ./comprehensive_audit.sh ]; then
    echo "✅ ./comprehensive_audit.sh - ESISTE"
    echo "   Descrizione: Controllo sistema completo"
else
    echo "❌ ./comprehensive_audit.sh - NON TROVATO"
fi

# Test coherence_check.sh
if [ -f ./coherence_check.sh ]; then
    echo "✅ ./coherence_check.sh - ESISTE"
    echo "   Descrizione: Check-up completo"
else
    echo "❌ ./coherence_check.sh - NON TROVATO"
fi

echo ""

# ═══════════════════════════════════════════════════════════════════
# 🌐 DASHBOARD
# ═══════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 4. DASHBOARD"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test ~/qdashboard
if [ -f ~/qdashboard ]; then
    echo "✅ ~/qdashboard - ESISTE"
    echo "   Descrizione: Web UI (porta 8501)"
else
    echo "❌ ~/qdashboard - NON TROVATO"
fi

echo ""

# ═══════════════════════════════════════════════════════════════════
# 📊 NUOVI COMANDI (Enhanced Modules)
# ═══════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🆕 5. NUOVI COMANDI (Enhanced Modules)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test monitor_decisions.sh
if [ -f ./monitor_decisions.sh ]; then
    echo "✅ ./monitor_decisions.sh - ESISTE"
    echo "   Descrizione: Monitoring decisioni con confluence"
else
    echo "❌ ./monitor_decisions.sh - NON TROVATO"
fi

# Test test_enhanced_modules.sh
if [ -f ./test_enhanced_modules.sh ]; then
    echo "✅ ./test_enhanced_modules.sh - ESISTE"
    echo "   Descrizione: Test moduli enhanced"
else
    echo "❌ ./test_enhanced_modules.sh - NON TROVATO"
fi

# Test final_integration_test.sh
if [ -f ./final_integration_test.sh ]; then
    echo "✅ ./final_integration_test.sh - ESISTE"
    echo "   Descrizione: Test integrazione completa"
else
    echo "❌ ./final_integration_test.sh - NON TROVATO"
fi

echo ""

# ═══════════════════════════════════════════════════════════════════
# 📋 RIEPILOGO
# ═══════════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 RIEPILOGO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TOTAL=0
FOUND=0

for cmd in ~/qstatus ~/qstart ~/qstop ~/qrestart ~/qv4snapshot ~/qmonitor ~/qbackup ~/qgithub ~/qgitstatus ~/qclean ~/qdashboard ./bug_timeline.sh ./comprehensive_audit.sh ./coherence_check.sh ./monitor_decisions.sh ./test_enhanced_modules.sh ./final_integration_test.sh; do
    TOTAL=$((TOTAL + 1))
    if [ -f "$cmd" ]; then
        FOUND=$((FOUND + 1))
    fi
done

echo ""
echo "Comandi trovati: $FOUND/$TOTAL"
echo ""

if [ $FOUND -eq $TOTAL ]; then
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  ✅ TUTTI I COMANDI PRESENTI!                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
elif [ $FOUND -gt $((TOTAL / 2)) ]; then
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  ⚠️  ALCUNI COMANDI MANCANTI                               ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
else
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  ❌ MOLTI COMANDI MANCANTI                                 ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
fi

