#!/bin/bash
echo "🔄 AGGIORNAMENTO COMANDI PER LA TUA STRATEGIA"
echo "============================================="

# Backup del file originale
if [ -f "quantum_commands.sh" ]; then
    cp quantum_commands.sh quantum_commands.sh.backup_$(date +%Y%m%d_%H%M%S)
    echo "✅ Backup creato: quantum_commands.sh.backup"
fi

# Crea la nuova versione aggiornata
cat > quantum_commands_updated.sh << 'QUANTUMCOMMANDS'
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
STATE_FILE="paper_trading_state.json"

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
        echo "   📊 Dati: 100% REALI da Binance"
        echo "   🎯 Strategia: Le tue confluenze avanzate"
        echo "   💰 Modalità: Paper Trading"
        
        if [ -f "$TRADER_SCRIPT" ]; then
            # Ferma eventuali processi esistenti
            pkill -f "$TRADER_SCRIPT" 2>/dev/null
            
            # Avvia il nuovo sistema
            python3 "$TRADER_SCRIPT" &
            TRADER_PID=$!
            echo $TRADER_PID > quantum_trader.pid
            
            echo -e "${GREEN}✅ Sistema avviato (PID: $TRADER_PID)${NC}"
            echo "📁 Log: $LOG_FILE"
        else
            echo -e "${RED}❌ File $TRADER_SCRIPT non trovato${NC}"
        fi
        ;;
        
    stop)
        show_header
        echo -e "${YELLOW}🛑 FERMO SISTEMA${NC}"
        
        if [ -f "quantum_trader.pid" ]; then
            TRADER_PID=$(cat quantum_trader.pid)
            kill $TRADER_PID 2>/dev/null
            rm -f quantum_trader.pid
            echo -e "${GREEN}✅ Sistema fermato${NC}"
        else
            # Ferma comunque qualsiasi processo
            pkill -f "$TRADER_SCRIPT" 2>/dev/null
            echo -e "${YELLOW}⚠️  Sistema fermato (forzato)${NC}"
        fi
        ;;
        
    status)
        show_header
        echo -e "${CYAN}📊 STATO SISTEMA${NC}"
        
        if [ -f "quantum_trader.pid" ]; then
            TRADER_PID=$(cat quantum_trader.pid)
            if ps -p $TRADER_PID > /dev/null; then
                echo -e "${GREEN}✅ SISTEMA ATTIVO${NC}"
                echo "   PID: $TRADER_PID"
                
                # Info aggiuntive
                CYCLES=$(grep -c "FINE CICLO" "$LOG_FILE" 2>/dev/null || echo "0")
                TRADES=$(grep -c "ACQUISTATO\\|VENDUTO" "$LOG_FILE" 2>/dev/null || echo "0")
                echo "   🔄 Cicli completati: $CYCLES"
                echo "   💰 Trade eseguiti: $TRADES"
                
                # Ultimo portfolio
                PORTFOLIO_LINE=$(tail -10 "$LOG_FILE" 2>/dev/null | grep "Portfolio:" | tail -1)
                if [ ! -z "$PORTFOLIO_LINE" ]; then
                    echo "   📈 $(echo "$PORTFOLIO_LINE" | sed 's/.*INFO - //')"
                fi
            else
                echo -e "${RED}❌ PID esistente ma processo non attivo${NC}"
                rm -f quantum_trader.pid
            fi
        else
            echo -e "${YELLOW}⚠️  SISTEMA FERMO${NC}"
        fi
        ;;
        
    logs)
        show_header
        echo -e "${BLUE}📋 LOG IN TEMPO REALE${NC}"
        echo "   File: $LOG_FILE"
        echo "   Ctrl+C per uscire"
        echo ""
        
        if [ -f "$LOG_FILE" ]; then
            tail -f "$LOG_FILE"
        else
            echo -e "${YELLOW}⚠️  File log non trovato${NC}"
        fi
        ;;
        
    performance)
        show_header
        echo -e "${GREEN}📈 PERFORMANCE STRATEGIA${NC}"
        
        if [ -f "$LOG_FILE" ]; then
            # Statistiche base
            TOTAL_CYCLES=$(grep -c "FINE CICLO" "$LOG_FILE" 2>/dev/null || echo "0")
            TOTAL_TRADES=$(grep -c "ACQUISTATO\\|VENDUTO" "$LOG_FILE" 2>/dev/null || echo "0")
            BUY_TRADES=$(grep -c "ACQUISTATO" "$LOG_FILE" 2>/dev/null || echo "0")
            SELL_TRADES=$(grep -c "VENDUTO" "$LOG_FILE" 2>/dev/null || echo "0")
            
            echo "   🔄 Cicli totali: $TOTAL_CYCLES"
            echo "   💰 Trade totali: $TOTAL_TRADES"
            echo "   📗 Acquisti: $BUY_TRADES"
            echo "   📕 Vendite: $SELL_TRADES"
            
            # Portfolio attuale
            PORTFOLIO_LINE=$(tail -20 "$LOG_FILE" 2>/dev/null | grep "Portfolio:" | tail -1)
            if [ ! -z "$PORTFOLIO_LINE" ]; then
                echo ""
                echo "   📊 $(echo "$PORTFOLIO_LINE" | sed 's/.*INFO - //')"
            fi
            
            # Ultime decisioni
            echo ""
            echo "   🎯 ULTIME DECISIONI:"
            tail -15 "$LOG_FILE" 2>/dev/null | grep "DECISIONE:" | tail -3 | sed 's/.*INFO - /      /'
            
        else
            echo -e "${YELLOW}⚠️  Nessun dato performance disponibile${NC}"
        fi
        ;;
        
    analysis)
        show_header
        echo -e "${PURPLE}🧠 ANALISI AVANZATA STRATEGIA${NC}"
        
        if [ -f "$LOG_FILE" ]; then
            # Analisi confluenze
            echo "   📊 DISTRIBUZIONE DECISIONI:"
            grep "DECISIONE:" "$LOG_FILE" 2>/dev/null | awk '{print $NF}' | sort | uniq -c | while read count decision; do
                echo "      $decision: $count volte"
            done
            
            # Score medi
            echo ""
            echo "   📈 SCORE MEDI:"
            grep "CONFLUENZA" "$LOG_FILE" 2>/dev/null | grep -o "Score: [0-9.]*" | awk '{sum+=$2; count++} END {if(count>0) print "      Media: " sum/count}'
            
        else
            echo -e "${YELLOW}⚠️  Nessun dato per analisi${NC}"
        fi
        ;;
        
    dashboard)
        show_header
        echo -e "${CYAN}🎛️  DASHBOARD LIVE${NC}"
        
        while true; do
            clear
            show_header
            ./quantum_commands.sh status
            echo ""
            ./quantum_commands.sh performance
            echo ""
            echo -e "${YELLOW}🔄 Aggiornamento in 10 secondi...${NC}"
            echo "   Ctrl+C per uscire"
            sleep 10
        done
        ;;
        
    clean)
        show_header
        echo -e "${YELLOW}🧹 PULIZIA SISTEMA${NC}"
        
        # Ferma il sistema
        ./quantum_commands.sh stop
        
        # Pulisci file temporanei (mantieni log e stato)
        echo "   ✅ Sistema fermato"
        echo "   📁 Log e dati storici mantenuti"
        echo "   💾 File stato paper trading mantenuto"
        ;;
        
    backup)
        show_header
        echo -e "${GREEN}💾 BACKUP DATI${NC}"
        
        # Crea backup con timestamp
        BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        
        cp "$LOG_FILE" "$BACKUP_DIR/" 2>/dev/null
        cp "$STATE_FILE" "$BACKUP_DIR/" 2>/dev/null
        cp "quantum_your_strategy.py" "$BACKUP_DIR/" 2>/dev/null
        
        echo "   ✅ Backup creato: $BACKUP_DIR"
        echo "   📁 Contenuto: log, stato, strategia"
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
        echo "  ${CYAN}dashboard${NC}    Dashboard live"
        echo ""
        echo "🔧 COMANDI UTILITY:"
        echo "  ${YELLOW}clean${NC}       Pulizia sistema"
        echo "  ${YELLOW}backup${NC}      Backup dati"
        echo ""
        echo "💡 La tua strategia è in esecuzione con dati 100% reali!"
        ;;
esac
QUANTUMCOMMANDS

# Rimpiazza il file originale
mv quantum_commands_updated.sh quantum_commands.sh
chmod +x quantum_commands.sh

echo ""
echo "✅ COMANDI AGGIORNATI!"
echo "🎯 ORA PUOI USARE:"
echo "   ./quantum_commands.sh analysis    # Analisi strategia"
echo "   ./quantum_commands.sh dashboard   # Dashboard migliorata"
echo "   ./quantum_commands.sh performance # Performance personalizzata"
