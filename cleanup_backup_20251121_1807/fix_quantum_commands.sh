#!/bin/bash
echo "🔧 RIPRISTINO QUANTUM_COMMANDS.SH"
echo "================================"

# Crea la versione corretta
cat > quantum_commands_fixed.sh << 'QUANTUMCOMMANDS'
#!/bin/bash

# COLORI
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# CONFIGURAZIONE
TRADER_SCRIPT="quantum_your_strategy.py"
LOG_FILE="quantum_your_strategy.log"

show_header() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════╗"
    echo "║           QUANTUM YOUR STRATEGY          ║"
    echo "║     Paper Trading - Confluenze Avanzate  ║"
    echo "╚══════════════════════════════════════════╝"
    echo -e "${NC}"
}

case "$1" in
    start)
        show_header
        echo -e "${GREEN}🚀 AVVIO STRATEGIA PERSONALIZZATA${NC}"
        python3 "$TRADER_SCRIPT" &
        echo $! > quantum_trader.pid
        echo -e "${GREEN}✅ Sistema avviato${NC}"
        ;;
        
    stop)
        show_header
        echo -e "${YELLOW}🛑 FERMO SISTEMA${NC}"
        if [ -f "quantum_trader.pid" ]; then
            kill $(cat quantum_trader.pid) 2>/dev/null
            rm -f quantum_trader.pid
        fi
        pkill -f "$TRADER_SCRIPT" 2>/dev/null
        echo -e "${GREEN}✅ Sistema fermato${NC}"
        ;;
        
    status)
        show_header
        echo -e "${CYAN}📊 STATO SISTEMA${NC}"
        if [ -f "quantum_trader.pid" ] && ps -p $(cat quantum_trader.pid) > /dev/null; then
            echo -e "${GREEN}✅ SISTEMA ATTIVO${NC}"
            CYCLES=$(grep -c "FINE CICLO" "$LOG_FILE" 2>/dev/null || echo "0")
            TRADES=$(grep -c "ACQUISTATO\\|VENDUTO" "$LOG_FILE" 2>/dev/null || echo "0")
            echo "   🔄 Cicli: $CYCLES"
            echo "   💰 Trade: $TRADES"
        else
            echo -e "${YELLOW}⚠️  SISTEMA FERMO${NC}"
        fi
        ;;
        
    logs)
        show_header
        echo -e "${BLUE}📋 LOG IN TEMPO REALE${NC}"
        tail -f "$LOG_FILE"
        ;;
        
    performance)
        show_header
        echo -e "${GREEN}📈 PERFORMANCE STRATEGIA${NC}"
        TOTAL_CYCLES=$(grep -c "FINE CICLO" "$LOG_FILE" 2>/dev/null || echo "0")
        TOTAL_TRADES=$(grep -c "ACQUISTATO\\|VENDUTO" "$LOG_FILE" 2>/dev/null || echo "0")
        echo "   🔄 Cicli: $TOTAL_CYCLES"
        echo "   💰 Trade: $TOTAL_TRADES"
        echo ""
        echo "   🎯 ULTIME DECISIONI:"
        tail -10 "$LOG_FILE" 2>/dev/null | grep "DECISIONE:" | tail -3 | sed 's/.*INFO - /      /'
        ;;
        
    analysis)
        show_header
        echo -e "${PURPLE}🧠 ANALISI STRATEGIA${NC}"
        echo "   📊 DISTRIBUZIONE DECISIONI:"
        grep "DECISIONE:" "$LOG_FILE" 2>/dev/null | awk '{print $NF}' | sort | uniq -c | while read count decision; do
            echo "      $decision: $count volte"
        done
        ;;
        
    database)
        show_header
        echo -e "${BLUE}🗄️  DATABASE TRADING${NC}"
        echo "   📁 File database: database/trading_history.json"
        echo "   📊 Trade salvati: $(find database/ -name "*.json" -exec cat {} \; 2>/dev/null | grep -c "timestamp" || echo "0")"
        echo ""
        echo "   📋 ULTIMI TRADE:"
        grep -E "ACQUISTATO|VENDUTO" "$LOG_FILE" 2>/dev/null | tail -5 | while read line; do
            echo "      $(echo "$line" | sed 's/.*INFO - //')"
        done
        ;;
        
    dashboard)
        show_header
        echo -e "${CYAN}🎛️  DASHBOARD${NC}"
        echo "   🌐 Dashboard Web: http://localhost:8502/"
        echo "   🎛️  Dashboard Terminale: ./quantum_dashboard.sh"
        echo ""
        echo "   Per avviare il dashboard web:"
        echo "   streamlit run dashboard.py --server.port 8502"
        ;;
        
    clean)
        show_header
        echo -e "${YELLOW}🧹 PULIZIA SISTEMA${NC}"
        ./quantum_commands.sh stop
        echo "   ✅ Sistema pulito"
        ;;
        
    backup)
        show_header
        echo -e "${GREEN}💾 BACKUP DATI${NC}"
        BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        cp "$LOG_FILE" "$BACKUP_DIR/" 2>/dev/null
        cp -r database/ "$BACKUP_DIR/" 2>/dev/null
        echo "   ✅ Backup creato: $BACKUP_DIR"
        ;;
        
    *)
        show_header
        echo -e "${BLUE}📖 UTILIZZO: ./quantum_commands.sh <comando>${NC}"
        echo ""
        echo "🎯 COMANDI PRINCIPALI:"
        echo "  ${GREEN}start${NC}       Avvia la TUA strategia"
        echo "  ${GREEN}stop${NC}        Ferma il sistema"
        echo "  ${GREEN}status${NC}      Stato sistema"
        echo "  ${GREEN}logs${NC}        Logs in tempo reale"
        echo ""
        echo "📊 COMANDI ANALISI:"
        echo "  ${CYAN}performance${NC}  Performance strategia"
        echo "  ${CYAN}analysis${NC}     Analisi avanzata"
        echo "  ${CYAN}database${NC}     Database trading"
        echo "  ${CYAN}dashboard${NC}    Dashboard"
        echo ""
        echo "🔧 COMANDI UTILITY:"
        echo "  ${YELLOW}clean${NC}       Pulizia sistema"
        echo "  ${YELLOW}backup${NC}      Backup dati"
        echo ""
        echo "💡 La tua strategia è in esecuzione con dati 100% reali!"
        ;;
esac
QUANTUMCOMMANDS

# Sostituisci il file corrotto
mv quantum_commands_fixed.sh quantum_commands.sh
chmod +x quantum_commands.sh

echo "✅ quantum_commands.sh RIPRISTINATO!"
