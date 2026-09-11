#!/bin/bash

# ════════════════════════════════════════════════════════════
# QUANTUM BOT - PRODUCTION CONTROL SCRIPT
# ════════════════════════════════════════════════════════════

BOT_DIR=~/trading_project/QuantumTradingSystem
BOT_SCRIPT=autonomous_trading_bot_improved.py
PID_FILE="$BOT_DIR/bot.pid"
CONTROL_LOCK="/tmp/quantum_v37_control_${UID}.lock"
WATCHDOG_SCRIPT="$BOT_DIR/ops/bot_watchdog.sh"
CONNECTION_SCRIPT="$BOT_DIR/ops/connection_monitor.sh"
HEALTH_SCRIPT="$BOT_DIR/ops/bot_health_check.sh"

WATCHDOG_PID_FILE="/tmp/quantum_v37_watchdog_${UID}.lock/pid"
CONNECTION_PID_FILE="/tmp/quantum_v37_connection_${UID}.lock/pid"
HEALTH_PID_FILE="/tmp/quantum_v37_health_${UID}.lock/pid"

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

    echo "❌ Bot ancora presente dopo 10 secondi"
    echo "⚠️ SIGKILL non inviato: verificare processo e log"
    return 1
}


is_expected_monitor_pid() {
    local pid="$1"
    local script="$2"
    local expected_script
    local proc_cwd
    local arg
    local resolved

    [[ "$pid" =~ ^[0-9]+$ ]] || return 1
    [ -d "/proc/$pid" ] || return 1

    expected_script=$(readlink -f "$script") || return 1
    proc_cwd=$(readlink -f "/proc/$pid/cwd" 2>/dev/null) || return 1

    while IFS= read -r -d '' arg; do
        if [ "$arg" = "$expected_script" ]; then
            return 0
        fi

        case "$arg" in
            /*)
                resolved=$(readlink -f "$arg" 2>/dev/null || true)
                ;;
            */*)
                resolved=$(readlink -f "$proc_cwd/$arg" 2>/dev/null || true)
                ;;
            *)
                resolved=""
                ;;
        esac

        if [ -n "$resolved" ] && [ "$resolved" = "$expected_script" ]; then
            return 0
        fi
    done < "/proc/$pid/cmdline"

    return 1
}


get_monitor_pid() {
    local script="$1"
    local pid_file="$2"
    local pid=""

    [ -f "$pid_file" ] || return 1

    pid=$(tr -d '[:space:]' < "$pid_file")

    if is_expected_monitor_pid "$pid" "$script"; then
        echo "$pid"
        return 0
    fi

    return 1
}


stop_monitor() {
    local name="$1"
    local script="$2"
    local pid_file="$3"
    local pid=""

    if ! pid=$(get_monitor_pid "$script" "$pid_file"); then
        echo "ℹ️  $name: non attivo o PID non valido"
        return 0
    fi

    echo "🛑 $name PID $pid"

    kill -TERM "$pid" 2>/dev/null || true

    for _ in {1..10}; do
        if ! is_expected_monitor_pid "$pid" "$script"; then
            echo "✅ $name fermato"
            return 0
        fi
        sleep 1
    done

    echo "❌ $name non si è fermato entro 10 secondi"
    return 1
}


monitor_status() {
    local name="$1"
    local script="$2"
    local pid_file="$3"
    local pid=""

    if pid=$(get_monitor_pid "$script" "$pid_file"); then
        echo "✅ $name: RUNNING (PID $pid)"
    else
        echo "❌ $name: STOPPED"
    fi
}


start_monitor() {
    local name="$1"
    local script="$2"
    local pid_file="$3"
    local log_file="$4"
    local pid=""
    local launched_pid=""

    if pid=$(get_monitor_pid "$script" "$pid_file"); then
        echo "✅ $name già attivo (PID $pid)"
        return 0
    fi

    nohup "$script" > "$log_file" 2>&1 9>&- &
    launched_pid=$!

    for _ in {1..5}; do
        if pid=$(get_monitor_pid "$script" "$pid_file"); then
            if [ "$pid" = "$launched_pid" ]; then
                echo "✅ $name avviato (PID $pid)"
                return 0
            fi

            echo "⚠️  $name attivo con PID $pid, diverso dal processo lanciato $launched_pid"
            return 1
        fi

        if ! ps -p "$launched_pid" > /dev/null 2>&1; then
            echo "❌ $name non è riuscito ad avviarsi"
            return 1
        fi

        sleep 1
    done

    echo "❌ $name non verificato dopo l'avvio"
    return 1
}


start_monitors() {
    local rc=0

    mkdir -p "$HOME/logs"

    start_monitor         "Watchdog"         "$WATCHDOG_SCRIPT"         "$WATCHDOG_PID_FILE"         "$HOME/logs/watchdog.log" || rc=1

    start_monitor         "Connection monitor"         "$CONNECTION_SCRIPT"         "$CONNECTION_PID_FILE"         "$HOME/logs/connection.log" || rc=1

    start_monitor         "Health check"         "$HEALTH_SCRIPT"         "$HEALTH_PID_FILE"         "$HOME/logs/health.log" || rc=1

    return "$rc"
}

stop_monitors() {
    local rc=0

    stop_monitor         "Watchdog"         "$WATCHDOG_SCRIPT"         "$WATCHDOG_PID_FILE" || rc=1

    stop_monitor         "Connection monitor"         "$CONNECTION_SCRIPT"         "$CONNECTION_PID_FILE" || rc=1

    stop_monitor         "Health check"         "$HEALTH_SCRIPT"         "$HEALTH_PID_FILE" || rc=1

    if [ "$rc" -eq 0 ]; then
        echo "✅ All monitors stopped"
    else
        echo "⚠️  Uno o più monitor non si sono fermati correttamente"
    fi

    return "$rc"
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
            start_monitors || exit 1
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

        # Ferma prima i monitor; interrompi in caso di errore
        stop_monitors || exit 1
        stop_bot || exit 1

        echo ""
        echo "✅ System stopped"
        ;;

    restart)
        echo "🔄 Restarting Quantum Trading System..."
        echo ""

        # Ferma prima i monitor; interrompi in caso di errore
        stop_monitors || exit 1
        stop_bot || exit 1

        sleep 3

        start_bot
        if [ $? -eq 0 ]; then
            start_monitors || exit 1
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

        monitor_status             "Watchdog"             "$WATCHDOG_SCRIPT"             "$WATCHDOG_PID_FILE"

        monitor_status             "Connection Monitor"             "$CONNECTION_SCRIPT"             "$CONNECTION_PID_FILE"

        monitor_status             "Health Check"             "$HEALTH_SCRIPT"             "$HEALTH_PID_FILE"

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
