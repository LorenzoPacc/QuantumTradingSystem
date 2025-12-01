#!/bin/bash
# ============================================================================
# QUANTUM TRADER V3.3 ULTIMATE - COMPLETE DEPLOYMENT SCRIPT
# ============================================================================
# Author: Quantum Trading System
# Version: 3.3.0
# Date: 2024-11-30
# Description: Complete deployment and management script for Quantum Trader V3.3
# ============================================================================

set -e  # Exit on error

# ============================================================================
# CONFIGURATION
# ============================================================================
PROJECT_DIR="$HOME/trading_project/QuantumTradingSystem"
VENV_DIR="$PROJECT_DIR/venv"
BOT_FILE="quantum_v33_ultimate_final.py"
DASHBOARD_FILE="quantum_dashboard_v33_web.py"
TELEGRAM_FILE="quantum_telegram_v33.py"
STATE_FILE="qv33_ultimate_final_state.json"
LOG_DIR="$PROJECT_DIR/logs"

# Screen session names
SCREEN_BOT="quantum_bot_v33"
SCREEN_DASHBOARD="quantum_dashboard_v33"
SCREEN_TELEGRAM="quantum_telegram_v33"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

print_header() {
    echo ""
    echo -e "${CYAN}============================================================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}============================================================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        print_success "$1 is installed"
        return 0
    else
        print_error "$1 is not installed"
        return 1
    fi
}

# ============================================================================
# SYSTEM CHECKS
# ============================================================================

check_system() {
    print_header "System Requirements Check"
    
    local all_ok=true
    
    # Check Python
    if check_command python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_info "Python version: $PYTHON_VERSION"
    else
        all_ok=false
    fi
    
    # Check pip
    check_command pip3 || all_ok=false
    
    # Check git (optional)
    check_command git || print_warning "git not found (optional)"
    
    # Check screen (for background processes)
    if ! check_command screen; then
        print_warning "screen not found. Install with: sudo apt-get install screen"
        print_info "Continuing without screen support..."
    fi
    
    if [ "$all_ok" = false ]; then
        print_error "Some required packages are missing. Please install them first."
        exit 1
    fi
    
    print_success "All system requirements met!"
}

# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================

setup_environment() {
    print_header "Setting Up Environment"
    
    # Create project directory if not exists
    if [ ! -d "$PROJECT_DIR" ]; then
        print_info "Creating project directory: $PROJECT_DIR"
        mkdir -p "$PROJECT_DIR"
    fi
    
    cd "$PROJECT_DIR" || exit 1
    print_success "Working directory: $PROJECT_DIR"
    
    # Create log directory
    if [ ! -d "$LOG_DIR" ]; then
        mkdir -p "$LOG_DIR"
        print_success "Created log directory: $LOG_DIR"
    fi
    
    # Setup virtual environment
    if [ ! -d "$VENV_DIR" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    else
        print_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    print_success "Virtual environment activated"
}

# ============================================================================
# DEPENDENCIES INSTALLATION
# ============================================================================

install_dependencies() {
    print_header "Installing Dependencies"
    
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip -q
    
    # Core trading dependencies
    print_info "Installing core trading packages..."
    pip install -q ccxt numpy pandas requests
    
    # Dashboard dependencies
    print_info "Installing dashboard packages..."
    pip install -q streamlit plotly
    
    # Telegram bot dependencies
    print_info "Installing Telegram bot packages..."
    pip install -q python-telegram-bot
    
    # Optional but useful
    print_info "Installing additional packages..."
    pip install -q python-dotenv
    
    print_success "All dependencies installed successfully!"
    
    # Show installed packages
    print_info "Installed packages:"
    pip list | grep -E "ccxt|streamlit|plotly|telegram|numpy|pandas"
}

# ============================================================================
# CONFIGURATION
# ============================================================================

setup_configuration() {
    print_header "Configuration Setup"
    
    # Check for .env file
    if [ ! -f "$PROJECT_DIR/.env" ]; then
        print_warning ".env file not found. Creating template..."
        cat > "$PROJECT_DIR/.env" << 'ENVFILE'
# Binance API Configuration
BINANCE_API_KEY=your_api_key_here
BINANCE_SECRET=your_secret_here

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Optional: BNB fee discount
USE_BNB_DISCOUNT=0
ENVFILE
        print_warning "Please edit .env file with your actual credentials:"
        print_info "  nano $PROJECT_DIR/.env"
    else
        print_success ".env file exists"
    fi
    
    # Source .env if exists
    if [ -f "$PROJECT_DIR/.env" ]; then
        set -a
        source "$PROJECT_DIR/.env"
        set +a
        print_success "Environment variables loaded from .env"
    fi
}

# ============================================================================
# FILE VALIDATION
# ============================================================================

validate_files() {
    print_header "Validating Required Files"
    
    local all_files_ok=true
    
    # Check bot file
    if [ -f "$PROJECT_DIR/$BOT_FILE" ]; then
        print_success "Bot file found: $BOT_FILE"
        # Syntax check
        python3 -m py_compile "$PROJECT_DIR/$BOT_FILE" 2>/dev/null && \
            print_success "Bot file syntax OK" || \
            { print_error "Bot file has syntax errors"; all_files_ok=false; }
    else
        print_error "Bot file not found: $BOT_FILE"
        all_files_ok=false
    fi
    
    # Check dashboard file
    if [ -f "$PROJECT_DIR/$DASHBOARD_FILE" ]; then
        print_success "Dashboard file found: $DASHBOARD_FILE"
        python3 -m py_compile "$PROJECT_DIR/$DASHBOARD_FILE" 2>/dev/null && \
            print_success "Dashboard file syntax OK" || \
            print_warning "Dashboard file has syntax errors (non-critical)"
    else
        print_warning "Dashboard file not found: $DASHBOARD_FILE (optional)"
    fi
    
    # Check Telegram file
    if [ -f "$PROJECT_DIR/$TELEGRAM_FILE" ]; then
        print_success "Telegram bot file found: $TELEGRAM_FILE"
        python3 -m py_compile "$PROJECT_DIR/$TELEGRAM_FILE" 2>/dev/null && \
            print_success "Telegram bot syntax OK" || \
            print_warning "Telegram bot has syntax errors (non-critical)"
    else
        print_warning "Telegram bot file not found: $TELEGRAM_FILE (optional)"
    fi
    
    if [ "$all_files_ok" = false ]; then
        print_error "Critical files missing or invalid. Please check."
        exit 1
    fi
    
    print_success "All required files validated!"
}

# ============================================================================
# BOT MANAGEMENT
# ============================================================================

start_bot() {
    print_header "Starting Trading Bot"
    
    cd "$PROJECT_DIR" || exit 1
    source "$VENV_DIR/bin/activate"
    
    # Check if already running
    if screen -list | grep -q "$SCREEN_BOT"; then
        print_warning "Bot is already running!"
        print_info "Use 'stop_bot' first to restart"
        return 1
    fi
    
    # Backup state file
    if [ -f "$STATE_FILE" ]; then
        cp "$STATE_FILE" "${STATE_FILE}.backup_$(date +%Y%m%d_%H%M%S)"
        print_success "State file backed up"
    fi
    
    # Start in screen session
    if command -v screen &> /dev/null; then
        screen -dmS "$SCREEN_BOT" bash -c "cd $PROJECT_DIR && source $VENV_DIR/bin/activate && python3 $BOT_FILE"
        print_success "Bot started in screen session: $SCREEN_BOT"
        print_info "Attach with: screen -r $SCREEN_BOT"
        print_info "Detach with: Ctrl+A then D"
    else
        # Fallback: run in background
        nohup python3 "$BOT_FILE" > "$LOG_DIR/bot.log" 2>&1 &
        echo $! > "$PROJECT_DIR/bot.pid"
        print_success "Bot started (PID: $(cat $PROJECT_DIR/bot.pid))"
    fi
    
    sleep 3
    
    # Verify bot is running
    if pgrep -f "$BOT_FILE" > /dev/null; then
        print_success "Bot is running successfully!"
        show_bot_status
    else
        print_error "Bot failed to start. Check logs:"
        print_info "  tail -f quantum_v33_ultimate_final.log"
    fi
}

stop_bot() {
    print_header "Stopping Trading Bot"
    
    # Kill screen session
    if screen -list | grep -q "$SCREEN_BOT"; then
        screen -S "$SCREEN_BOT" -X quit
        print_success "Screen session terminated"
    fi
    
    # Kill by PID file
    if [ -f "$PROJECT_DIR/bot.pid" ]; then
        kill $(cat "$PROJECT_DIR/bot.pid") 2>/dev/null || true
        rm "$PROJECT_DIR/bot.pid"
    fi
    
    # Kill by process name
    pkill -f "$BOT_FILE" 2>/dev/null || true
    
    # Clean up lock file
    rm -f /tmp/quantum_v33_ultimate_final.lock
    
    print_success "Bot stopped"
}

restart_bot() {
    print_header "Restarting Trading Bot"
    stop_bot
    sleep 2
    start_bot
}

show_bot_status() {
    print_header "Bot Status"
    
    if pgrep -f "$BOT_FILE" > /dev/null; then
        print_success "Bot is RUNNING"
        
        # Show process info
        ps aux | grep "$BOT_FILE" | grep -v grep
        
        # Show recent log
        if [ -f "quantum_v33_ultimate_final.log" ]; then
            echo ""
            print_info "Recent log entries:"
            tail -15 quantum_v33_ultimate_final.log | grep -E "CYCLE|Total Value|PnL"
        fi
        
        # Show state file info
        if [ -f "$STATE_FILE" ]; then
            echo ""
            print_info "State file last modified: $(stat -c %y $STATE_FILE | cut -d'.' -f1)"
        fi
    else
        print_error "Bot is NOT running"
    fi
}

# ============================================================================
# DASHBOARD MANAGEMENT
# ============================================================================

start_dashboard() {
    print_header "Starting Web Dashboard"
    
    cd "$PROJECT_DIR" || exit 1
    source "$VENV_DIR/bin/activate"
    
    if [ ! -f "$DASHBOARD_FILE" ]; then
        print_error "Dashboard file not found: $DASHBOARD_FILE"
        return 1
    fi
    
    # Check if already running
    if screen -list | grep -q "$SCREEN_DASHBOARD"; then
        print_warning "Dashboard is already running!"
        return 1
    fi
    
    # Start dashboard
    if command -v screen &> /dev/null; then
        screen -dmS "$SCREEN_DASHBOARD" bash -c "cd $PROJECT_DIR && source $VENV_DIR/bin/activate && streamlit run $DASHBOARD_FILE --server.port 8501 --server.headless true"
        print_success "Dashboard started in screen session: $SCREEN_DASHBOARD"
    else
        nohup streamlit run "$DASHBOARD_FILE" --server.port 8501 --server.headless true > "$LOG_DIR/dashboard.log" 2>&1 &
        echo $! > "$PROJECT_DIR/dashboard.pid"
        print_success "Dashboard started (PID: $(cat $PROJECT_DIR/dashboard.pid))"
    fi
    
    sleep 3
    print_success "Dashboard running at: http://localhost:8501"
}

stop_dashboard() {
    print_header "Stopping Web Dashboard"
    
    if screen -list | grep -q "$SCREEN_DASHBOARD"; then
        screen -S "$SCREEN_DASHBOARD" -X quit
        print_success "Dashboard screen session terminated"
    fi
    
    if [ -f "$PROJECT_DIR/dashboard.pid" ]; then
        kill $(cat "$PROJECT_DIR/dashboard.pid") 2>/dev/null || true
        rm "$PROJECT_DIR/dashboard.pid"
    fi
    
    pkill -f "streamlit run $DASHBOARD_FILE" 2>/dev/null || true
    
    print_success "Dashboard stopped"
}

# ============================================================================
# TELEGRAM BOT MANAGEMENT
# ============================================================================

start_telegram() {
    print_header "Starting Telegram Bot"
    
    cd "$PROJECT_DIR" || exit 1
    source "$VENV_DIR/bin/activate"
    
    if [ ! -f "$TELEGRAM_FILE" ]; then
        print_error "Telegram bot file not found: $TELEGRAM_FILE"
        return 1
    fi
    
    # Check credentials
    if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ "$TELEGRAM_BOT_TOKEN" = "your_bot_token_here" ]; then
        print_error "Telegram bot token not configured in .env"
        return 1
    fi
    
    if screen -list | grep -q "$SCREEN_TELEGRAM"; then
        print_warning "Telegram bot is already running!"
        return 1
    fi
    
    if command -v screen &> /dev/null; then
        screen -dmS "$SCREEN_TELEGRAM" bash -c "cd $PROJECT_DIR && source $VENV_DIR/bin/activate && python3 $TELEGRAM_FILE"
        print_success "Telegram bot started in screen session: $SCREEN_TELEGRAM"
    else
        nohup python3 "$TELEGRAM_FILE" > "$LOG_DIR/telegram.log" 2>&1 &
        echo $! > "$PROJECT_DIR/telegram.pid"
        print_success "Telegram bot started (PID: $(cat $PROJECT_DIR/telegram.pid))"
    fi
}

stop_telegram() {
    print_header "Stopping Telegram Bot"
    
    if screen -list | grep -q "$SCREEN_TELEGRAM"; then
        screen -S "$SCREEN_TELEGRAM" -X quit
    fi
    
    if [ -f "$PROJECT_DIR/telegram.pid" ]; then
        kill $(cat "$PROJECT_DIR/telegram.pid") 2>/dev/null || true
        rm "$PROJECT_DIR/telegram.pid"
    fi
    
    pkill -f "$TELEGRAM_FILE" 2>/dev/null || true
    
    print_success "Telegram bot stopped"
}

# ============================================================================
# ALL-IN-ONE MANAGEMENT
# ============================================================================

start_all() {
    print_header "Starting All Services"
    
    start_bot
    sleep 2
    start_dashboard
    sleep 2
    start_telegram
    
    echo ""
    print_success "All services started!"
    print_info "Access dashboard at: http://localhost:8501"
}

stop_all() {
    print_header "Stopping All Services"
    
    stop_telegram
    stop_dashboard
    stop_bot
    
    print_success "All services stopped!"
}

restart_all() {
    stop_all
    sleep 3
    start_all
}

show_status() {
    print_header "System Status Overview"
    
    echo -e "${CYAN}Trading Bot:${NC}"
    if pgrep -f "$BOT_FILE" > /dev/null; then
        print_success "RUNNING"
    else
        print_error "STOPPED"
    fi
    
    echo ""
    echo -e "${CYAN}Web Dashboard:${NC}"
    if pgrep -f "streamlit run $DASHBOARD_FILE" > /dev/null; then
        print_success "RUNNING (http://localhost:8501)"
    else
        print_error "STOPPED"
    fi
    
    echo ""
    echo -e "${CYAN}Telegram Bot:${NC}"
    if pgrep -f "$TELEGRAM_FILE" > /dev/null; then
        print_success "RUNNING"
    else
        print_error "STOPPED"
    fi
    
    echo ""
    echo -e "${CYAN}Screen Sessions:${NC}"
    screen -list 2>/dev/null | grep quantum || echo "  No screen sessions"
}

# ============================================================================
# LOGS & MONITORING
# ============================================================================

show_logs() {
    print_header "Recent Logs"
    
    if [ -f "quantum_v33_ultimate_final.log" ]; then
        print_info "Trading Bot Log (last 20 lines):"
        tail -20 quantum_v33_ultimate_final.log
    else
        print_warning "Bot log file not found"
    fi
}

monitor_bot() {
    print_header "Live Bot Monitor (Ctrl+C to exit)"
    tail -f quantum_v33_ultimate_final.log
}

# ============================================================================
# BACKUP & RESTORE
# ============================================================================

backup_state() {
    print_header "Backing Up State Files"
    
    BACKUP_DIR="$PROJECT_DIR/backups"
    mkdir -p "$BACKUP_DIR"
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
    
    tar -czf "$BACKUP_FILE" \
        "$STATE_FILE" \
        *.log \
        .env 2>/dev/null || true
    
    print_success "Backup created: $BACKUP_FILE"
    
    # Keep only last 10 backups
    ls -t "$BACKUP_DIR"/backup_*.tar.gz | tail -n +11 | xargs rm -f 2>/dev/null || true
}

# ============================================================================
# MAIN MENU
# ============================================================================

show_menu() {
    clear
    print_header "🚀 QUANTUM TRADER V3.3 ULTIMATE - CONTROL PANEL"
    
    echo -e "${CYAN}SETUP:${NC}"
    echo "  1) Full Setup (check system, install deps, configure)"
    echo ""
    echo -e "${CYAN}BOT CONTROL:${NC}"
    echo "  2) Start Bot"
    echo "  3) Stop Bot"
    echo "  4) Restart Bot"
    echo "  5) Bot Status"
    echo ""
    echo -e "${CYAN}SERVICES:${NC}"
    echo "  6) Start Dashboard"
    echo "  7) Stop Dashboard"
    echo "  8) Start Telegram Bot"
    echo "  9) Stop Telegram Bot"
    echo ""
    echo -e "${CYAN}ALL-IN-ONE:${NC}"
    echo "  10) Start All Services"
    echo "  11) Stop All Services"
    echo "  12) Restart All Services"
    echo "  13) Show All Status"
    echo ""
    echo -e "${CYAN}MONITORING:${NC}"
    echo "  14) Show Logs"
    echo "  15) Monitor Live"
    echo "  16) Backup State"
    echo ""
    echo "  0) Exit"
    echo ""
    echo -ne "${GREEN}Enter choice: ${NC}"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    # If arguments provided, execute directly
    if [ $# -gt 0 ]; then
        case "$1" in
            setup)
                check_system
                setup_environment
                install_dependencies
                setup_configuration
                validate_files
                ;;
            start)
                start_all
                ;;
            stop)
                stop_all
                ;;
            restart)
                restart_all
                ;;
            status)
                show_status
                ;;
            bot-start)
                start_bot
                ;;
            bot-stop)
                stop_bot
                ;;
            bot-restart)
                restart_bot
                ;;
            dashboard-start)
                start_dashboard
                ;;
            dashboard-stop)
                stop_dashboard
                ;;
            telegram-start)
                start_telegram
                ;;
            telegram-stop)
                stop_telegram
                ;;
            logs)
                show_logs
                ;;
            monitor)
                monitor_bot
                ;;
            backup)
                backup_state
                ;;
            *)
                echo "Usage: $0 {setup|start|stop|restart|status|bot-start|bot-stop|bot-restart|dashboard-start|dashboard-stop|telegram-start|telegram-stop|logs|monitor|backup}"
                exit 1
                ;;
        esac
        exit 0
    fi
    
    # Interactive menu
    while true; do
        show_menu
        read -r choice
        
        case $choice in
            1)
                check_system
                setup_environment
                install_dependencies
                setup_configuration
                validate_files
                ;;
            2) start_bot ;;
            3) stop_bot ;;
            4) restart_bot ;;
            5) show_bot_status ;;
            6) start_dashboard ;;
            7) stop_dashboard ;;
            8) start_telegram ;;
            9) stop_telegram ;;
            10) start_all ;;
            11) stop_all ;;
            12) restart_all ;;
            13) show_status ;;
            14) show_logs ;;
            15) monitor_bot ;;
            16) backup_state ;;
            0)
                print_success "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid choice"
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Run main function
main "$@"
