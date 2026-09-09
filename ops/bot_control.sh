#!/bin/bash

# ════════════════════════════════════════════════════════════
# QUANTUM BOT - PRODUCTION CONTROL SCRIPT
# ════════════════════════════════════════════════════════════

BOT_DIR=~/trading_project/QuantumTradingSystem
BOT_SCRIPT=autonomous_trading_bot_improved.py
PID_FILE="$BOT_DIR/bot.pid"
CONTROL_LOCK="/tmp/quantum_v37_control_${UID}.lock"
WATCHDOG_SCRIPT=/home/orenzo/bot_watchdog.sh
CONNECTION_SCRIPT=/home/orenzo/connection_monitor.sh
HEALTH_SCRIPT=/home/orenzo/bot_health_check.sh

# ─────────────────────────────────────────────
# FUNZIONI CORE
# ─────────────────────────────────────────────

is_expected_bot_pid() {
    local pid="$1"

    [[ "$pid" =~ ^[0-9]+$ ]] || return 1
    [ -d "/proc/$pid" ] || return 1

    local expected_dir
    local process_dir
    local process_cmd

    expected_dir=$(readlink -f "$BOT_DIR")
    process_dir=$(readlink -f "/proc/$pid/cwd" 2>/dev/null) || return 1
    process_cmd=$(tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null)

    [ "$process_dir" = "$expected_dir" ] || return 1
    [[ "$process_cmd" == *"$BOT_SCRIPT"* ]] || return 1

    return 0
}

find_expected_bot_pids() {
    local pid

    while read -r pid; do
        [ -n "$pid" ] || continue

        if is_expected_bot_pid "$pid"; then
            echo "$pid"
        fi
    done < <(
        pgrep -u "$(id -u)" -f "$BOT_SCRIPT" 2>/dev/null
    )
}

find_any_bot_pids() {
    pgrep -u "$(id -u)" -f "$BOT_SCRIPT" 2>/dev/null || true
}

is_bot_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")

        if is_expected_bot_pid "$PID"; then
            return 0
        fi

        rm -f "$PID_FILE"
    fi

    local found
    found=$(find_expected_bot_pids | head -n 1)

    if [ -n "$found" ]; then
        echo "$found" > "$PID_FILE"
        return 0
    fi

    return 1
}

start_bot() (
    # B17/B17b FINAL:
    # l'intera sezione protetta vive in un subshell.
    # FD 9 muore automaticamente quando questa funzione termina.
    if ! command -v flock > /dev/null 2>&1; then
        echo "❌ Comando flock non disponibile"
        return 1
    fi

    exec 9>"$CONTROL_LOCK"

    if ! flock -n 9; then
        echo "❌ Un altro start/restart V37 è già in corso"
        return 1
    fi

    # Controlla il V37 gestito normalmente.
    if is_bot_running; then
        echo "⚠️  Bot already running (PID: $(cat "$PID_FILE"))"
        return 1
    fi

    # Rifiuta anche eventuali V37 avviati fuori dal controller.
    local foreign_pids
    foreign_pids=$(find_any_bot_pids | paste -sd ' ' -)

    if [ -n "$foreign_pids" ]; then
        echo "❌ Processo V37 già presente fuori dal controller"
        echo "   PID rilevati: $foreign_pids"
        return 1
    fi

    mkdir -p "$BOT_DIR/logs"

    cd "$BOT_DIR" || return 1
    source venv/bin/activate

    # Anche il processo Python chiude esplicitamente FD 9.
    nohup python3 "$BOT_SCRIPT" > logs/bot.log 2>&1 9>&- &

    echo $! > "$PID_FILE"

    sleep 3

    if is_bot_running; then
        echo "✅ Trading bot started (PID: $(cat "$PID_FILE"))"
        return 0
    fi

    echo "❌ Failed to start trading bot"
    rm -f "$PID_FILE"
    return 1
)

stop_bot() {
    if ! is_bot_running; then
        echo "⚠️  Bot not running"
        rm -f "$PID_FILE"
        return 0
    fi

    PID=$(cat "$PID_FILE")
    echo "🛑 Stopping bot (PID: $PID)..."

    # Graceful shutdown
    kill -TERM "$PID" 2>/dev/null

    # Wait up to 10 seconds
    for i in {1..10}; do
        if ! ps -p "$PID" > /dev/null 2>&1; then
            echo "✅ Trading bot stopped gracefully"
            rm -f "$PID_FILE"
            return 0
        fi
        sleep 1
    done

    # Force kill
    echo "⚠️  Forcing shutdown..."
    kill -KILL "$PID" 2>/dev/null
    sleep 2

    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ Trading bot stopped (forced)"
        rm -f "$PID_FILE"
        return 0
    else
        echo "❌ Failed to stop bot"
        return 1
    fi
}

start_monitors() {
    mkdir -p ~/logs

    nohup "$WATCHDOG_SCRIPT" > ~/logs/watchdog.log 2>&1 9>&- &
    nohup "$CONNECTION_SCRIPT" > ~/logs/connection.log 2>&1 9>&- &
    nohup "$HEALTH_SCRIPT" > ~/logs/health.log 2>&1 9>&- &

    sleep 1
    echo "✅ Watchdog started"
    echo "✅ Connection monitor started"
    echo "✅ Health check started"
}

stop_monitors() {
    pkill -f bot_watchdog.sh
    pkill -f connection_monitor.sh
    pkill -f bot_health_check.sh
    sleep 1
    echo "✅ All monitors stopped"
}

# ─────────────────────────────────────────────
# COMANDI
# ─────────────────────────────────────────────

case "$1" in
    start)
        echo "🚀 Starting Quantum Trading System..."
        echo ""

        start_bot
        if [ $? -eq 0 ]; then
            start_monitors
            echo ""
            echo "🎉 System active!"
        else
            echo ""
            echo "❌ Failed to start system"
            exit 1
        fi
        ;;

    stop)
        echo "🛑 Stopping Quantum Trading System..."
        echo ""

        # ✅ FIX 2: Stop bot PRIMA dei monitor
        stop_bot
        stop_monitors

        echo ""
        echo "✅ System stopped"
        ;;

    restart)
        echo "🔄 Restarting Quantum Trading System..."
        echo ""

        # ✅ FIX 2: Ordine corretto
        stop_bot
        stop_monitors

        sleep 3

        start_bot
        if [ $? -eq 0 ]; then
            start_monitors
            echo ""
            echo "✅ System restarted"
        else
            echo ""
            echo "❌ Restart failed"
            exit 1
        fi
        ;;

    status)
        echo "╔════════════════════════════════════════════╗"
        echo "║     📊 QUANTUM BOT - SYSTEM STATUS       ║"
        echo "╚════════════════════════════════════════════╝"
        echo ""

        # Watchdog
        if pgrep -f bot_watchdog.sh > /dev/null; then
            echo "✅ Watchdog: RUNNING"
        else
            echo "❌ Watchdog: STOPPED"
        fi

        # Connection Monitor
        if pgrep -f connection_monitor.sh > /dev/null; then
            echo "✅ Connection Monitor: RUNNING"
        else
            echo "❌ Connection Monitor: STOPPED"
        fi

        # Health Check
        if pgrep -f bot_health_check.sh > /dev/null; then
            echo "✅ Health Check: RUNNING"
        else
            echo "❌ Health Check: STOPPED"
        fi

        # Trading Bot
        mapfile -t ALL_BOT_PIDS < <(find_any_bot_pids)

        if [ "${#ALL_BOT_PIDS[@]}" -gt 1 ]; then
            echo "❌ Trading Bot: MULTIPLE INSTANCES"
            echo "   PIDs: ${ALL_BOT_PIDS[*]}"
        elif is_bot_running; then
            BOT_PID=$(cat "$PID_FILE")
            BOT_UPTIME=$(ps -p "$BOT_PID" -o etime= | xargs)
            BOT_START=$(ps -p "$BOT_PID" -o lstart= | xargs)
            echo "✅ Trading Bot: RUNNING"
            echo "   PID: $BOT_PID"
            echo "   Uptime: $BOT_UPTIME"
            echo "   Started: $BOT_START"
        elif [ "${#ALL_BOT_PIDS[@]}" -eq 1 ]; then
            echo "⚠️  Trading Bot: processo fuori dal controller"
            echo "   PID: ${ALL_BOT_PIDS[0]}"
        else
            echo "❌ Trading Bot: STOPPED"
        fi

        echo ""
        ;;

    logs)
        echo "📋 Recent Bot Activity:"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        tail -30 "$BOT_DIR/logs/bot.log"
        ;;

    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start bot and all monitors"
        echo "  stop    - Stop bot and all monitors"
        echo "  restart - Restart entire system"
        echo "  status  - Show system status"
        echo "  logs    - Show recent bot logs"
        exit 1
        ;;
esac
