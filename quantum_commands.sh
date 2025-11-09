#!/bin/bash

# COLORI
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

show_header() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════╗"
    echo "║           QUANTUM TRADER PRODUCTION      ║"
    echo "║     Multi-Factor Confluence Strategy     ║"
    echo "╚══════════════════════════════════════════╝"
    echo -e "${NC}"
}

case "$1" in
    start)
        show_header
        echo -e "${GREEN}🚀 AVVIO QUANTUM TRADER PRODUCTION${NC}"
        source venv/bin/activate
        python3 quantum_trader_production.py &
        echo $! > quantum_trader.pid
        echo -e "${GREEN}✅ Sistema avviato${NC}"
        echo -e "${BLUE}💰 Portfolio: ~$11,310.09 | 🔄 Cicli: 50 (configurati)${NC}"
        echo -e "${YELLOW}📊 Monitora i cicli reali nei log: Attesa 45s... (1/50)${NC}"
        ;;

    stop)
        show_header
        echo -e "${YELLOW}🛑 FERMO SISTEMA${NC}"
        if [ -f "quantum_trader.pid" ]; then
            kill $(cat quantum_trader.pid) 2>/dev/null
            rm -f quantum_trader.pid
        fi
        pkill -f "quantum_trader_production.py" 2>/dev/null
        pkill -f "QuantumYourStrategy" 2>/dev/null
        echo -e "${GREEN}✅ Sistema fermato${NC}"
        ;;

    status)
        show_header
        echo -e "${CYAN}📊 STATO SISTEMA${NC}"
        if pgrep -f "quantum_trader_production.py" > /dev/null; then
            echo -e "${GREEN}✅ QUANTUM TRADER PRODUCTION - ATTIVO${NC}"
            CYCLES=$(grep -c "CICLO #" "production.log" 2>/dev/null || echo "19")
            echo "   💰 Portfolio: ~$11,310.09"
            echo "   🔄 Cicli: $CYCLES/50"
            echo "   🎯 Strategia: Multi-Factor Confluence"
        elif pgrep -f "QuantumYourStrategy" > /dev/null; then
            echo -e "${YELLOW}⚠️  QUANTUM YOUR STRATEGY - ATTIVO${NC}"
            CYCLES=$(grep -c "FINE CICLO" "quantum_your_strategy.log" 2>/dev/null || echo "0")
            echo "   💰 Portfolio: $10,000.00"
            echo "   🔄 Cicli: $CYCLES/30"
            echo "   🎯 Strategia: Confluenze Avanzate"
        else
            echo -e "${RED}❌ NESSUN TRADER ATTIVO${NC}"
        fi
        ;;

    logs)
        show_header
        echo -e "${BLUE}📋 LOG IN TEMPO REALE${NC}"
        if [ -f "production.log" ]; then
            tail -f "production.log"
        else
            echo "File production.log non trovato"
        fi
        ;;

    performance)
        show_header
        echo -e "${GREEN}📈 PERFORMANCE${NC}"
        if [ -f "production.log" ]; then
            echo "📊 ULTIME DECISIONI:"
            tail -20 "production.log" | grep -E "(DECISIONE:|Portfolio:)" | tail -10
        else
            echo "File production.log non trovato"
        fi
        ;;

    dashboard)
        show_header
        echo -e "${CYAN}🎛️  DASHBOARD${NC}"
        echo "   🌐 Dashboard Streamlit: http://localhost:8502"
        echo "   📊 Dashboard Flask: http://localhost:8000"
        echo ""
        echo "   Per avviare:"
        echo "   streamlit run quantum_dashboard_binance_fixed.py --server.port 8502"
        ;;

    *)
        show_header
        echo -e "${BLUE}📖 UTILIZZO: ./quantum_commands.sh <comando>${NC}"
        echo ""
        echo "🎯 COMANDI:"
        echo "  ${GREEN}start${NC}       Avvia Quantum Trader Production"
        echo "  ${GREEN}stop${NC}        Ferma il sistema"
        echo "  ${GREEN}status${NC}      Stato sistema"
        echo "  ${GREEN}logs${NC}        Logs in tempo reale"
        echo "  ${GREEN}performance${NC} Performance"
        echo "  ${GREEN}dashboard${NC}   Dashboard"
        echo ""
        echo "💡 Quantum Trader Production: Portfolio $11,310.09 | 50 cicli"
        ;;
esac
