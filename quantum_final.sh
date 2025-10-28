#!/bin/bash

# Quantum Trading System - Controller Script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Funzioni
print_status() { echo -e "${BLUE}[QUANTUM]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

check_environment() {
    if [ ! -d "venv" ]; then
        print_error "Virtual environment non trovato!"
        return 1
    fi
    if [ ! -f "quantum_trader_ultimate_final.py" ]; then
        print_error "File quantum_trader_ultimate_final.py non trovato!"
        return 1
    fi
    return 0
}

start_trader() {
    print_status "Avvio Quantum Trader..."
    source venv/bin/activate
    nohup python3 quantum_trader_ultimate_final.py > trader.log 2>&1 &
    TRADER_PID=$!
    echo $TRADER_PID > trader.pid
    print_success "Trader avviato con PID: $TRADER_PID"
}

start_testnet() {
    print_status "Avvio versione ottimizzata per Testnet..."
    source venv/bin/activate
    if [ -f "quantum_trader_testnet_optimized.py" ]; then
        nohup python3 quantum_trader_testnet_optimized.py > trader.log 2>&1 &
    else
        nohup python3 quantum_trader_ultimate_final.py > trader.log 2>&1 &
    fi
    TRADER_PID=$!
    echo $TRADER_PID > trader.pid
    print_success "Trader Testnet avviato con PID: $TRADER_PID"
}

start_micro() {
    print_status "Avvio MICRO TRADING (fondi limitati)..."
    source venv/bin/activate
    nohup python3 quantum_trader_micro.py > trader.log 2>&1 &
    TRADER_PID=$!
    echo $TRADER_PID > trader.pid
    print_success "Micro Trader avviato con PID: $TRADER_PID"
    print_success "💰 Position size: 5.0 USDT | 📈 Max: 1 posizione"
}

stop_trader() {
    if [ -f "trader.pid" ]; then
        TRADER_PID=$(cat trader.pid)
        print_status "Fermando trader (PID: $TRADER_PID)..."
        kill $TRADER_PID 2>/dev/null
        rm -f trader.pid
        print_success "Trader fermato"
    else
        print_warning "Nessun PID file trovato, kill processi manuali..."
        pkill -f "python.*quantum_trader" 2>/dev/null
    fi
}

monitor_logs() {
    print_status "Monitoraggio log in tempo reale..."
    if [ -f "trader.log" ]; then
        tail -f trader.log
    else
        print_error "File trader.log non trovato!"
    fi
}

show_status() {
    print_status "=== STATO SISTEMA QUANTUM ==="
    echo -e "\n${BLUE}📊 PROCESSI ATTIVI:${NC}"
    ps aux | grep -E "python.*quantum|streamlit" | grep -v grep
    echo -e "\n${BLUE}📁 FILE DI LOG:${NC}"
    ls -la *.log 2>/dev/null || echo "Nessun file log trovato"
    echo -e "\n${BLUE}🗃️ DATABASE:${NC}"
    if [ -f "quantum_final.db" ]; then
        python3 << 'DB_EOF'
import sqlite3
try:
    conn = sqlite3.connect('quantum_final.db')
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM balance_history ORDER BY timestamp DESC LIMIT 1")
    balance_result = cursor.fetchone()
    balance = balance_result[0] if balance_result else 0
    cursor.execute("SELECT COUNT(*) FROM open_positions")
    open_trades = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM trades")
    total_trades = cursor.fetchone()[0]
    print(f"💰 Balance corrente: ${balance:.2f}")
    print(f"📈 Trade aperti: {open_trades}")
    print(f"📊 Trade totali: {total_trades}")
    cursor.execute("SELECT symbol, side, quantity, entry_price, timestamp FROM trades ORDER BY timestamp DESC LIMIT 3")
    recent_trades = cursor.fetchall()
    if recent_trades:
        print(f"\n🔄 Ultimi trade:")
        for trade in recent_trades:
            print(f"   {trade[0]} {trade[1]} {trade[2]} @ ${trade[3]:.2f}")
    conn.close()
except Exception as e:
    print(f"❌ Errore DB: {e}")
DB_EOF
    else
        echo "Database non trovato"
    fi
}

# Main menu
case "$1" in
    "start")
        check_environment || exit 1
        start_trader
        print_success "Quantum Trading System avviato!"
        ;;
    "testnet")
        check_environment || exit 1
        start_testnet
        print_success "Quantum Trading System (Testnet) avviato!"
        ;;
    "micro")
        check_environment || exit 1
        start_micro
        ;;
    "trader-only")
        check_environment || exit 1
        start_trader
        ;;
    "stop")
        stop_trader
        ;;
    "monitor")
        monitor_logs
        ;;
    "status")
        show_status
        ;;
    "logs")
        monitor_logs
        ;;
    "restart")
        stop_trader
        sleep 2
        check_environment || exit 1
        start_trader
        ;;
    *)
        echo -e "${BLUE}🎯 QUANTUM TRADING SYSTEM - COMANDI DISPONIBILI${NC}"
        echo -e "${GREEN}./quantum_final.sh start${NC}     - 🚀 Avvio standard"
        echo -e "${GREEN}./quantum_final.sh testnet${NC}   - 💰 Testnet ottimizzato" 
        echo -e "${GREEN}./quantum_final.sh micro${NC}     - 📦 Micro trading ($84)"
        echo -e "${GREEN}./quantum_final.sh stop${NC}      - 🛑 Ferma tutto"
        echo -e "${GREEN}./quantum_final.sh monitor${NC}   - 📊 Monitora log"
        echo -e "${GREEN}./quantum_final.sh status${NC}    - 📡 Stato sistema"
        echo -e "\n${YELLOW}🌐 DASHBOARD:${NC}"
        echo "streamlit run dashboard_finale.py --server.port 8503 --server.address=0.0.0.0"
        ;;
esac
