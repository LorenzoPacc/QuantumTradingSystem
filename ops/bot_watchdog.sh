#!/bin/bash

# ============================================================
# QUANTUM V37 WATCHDOG - B21
# Monitor read/check + restart delegato al controller ufficiale
# ============================================================

BOT_DIR="$HOME/trading_project/QuantumTradingSystem"
BOT_SCRIPT="autonomous_trading_bot_improved.py"
PID_FILE="$BOT_DIR/bot.pid"
CYCLE_FILE="$BOT_DIR/last_cycle.txt"
CONTROL_SCRIPT="$BOT_DIR/ops/bot_control.sh"

LOG_FILE="$HOME/bot_watchdog.log"
ENV_FILE="$BOT_DIR/.env"

# V37 gira ogni 2 ore.
# 3 ore = 1 ora di margine prima di considerarlo realmente bloccato.
MAX_IDLE_TIME=10800
CHECK_INTERVAL=60

# Evita falsi allarmi subito dopo start/restart.
STARTUP_GRACE=300



MONITOR_NAME="watchdog"
MONITOR_SCRIPT="$(readlink -f "$0")"
MONITOR_LOCK_DIR="/tmp/quantum_v37_${MONITOR_NAME}_${UID}.lock"
MONITOR_PID_FILE="$MONITOR_LOCK_DIR/pid"


is_same_monitor_pid() {
    local pid="$1"
    local arg
    local proc_cwd
    local resolved

    [[ "$pid" =~ ^[0-9]+$ ]] || return 1
    [ -d "/proc/$pid" ] || return 1

    proc_cwd=$(readlink -f "/proc/$pid/cwd" 2>/dev/null) || return 1

    while IFS= read -r -d '' arg; do
        if [ "$arg" = "$MONITOR_SCRIPT" ]; then
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

        if [ -n "$resolved" ] && [ "$resolved" = "$MONITOR_SCRIPT" ]; then
            return 0
        fi
    done < "/proc/$pid/cmdline"

    return 1
}


cleanup_monitor_singleton() {
    local recorded=""

    if [ -f "$MONITOR_PID_FILE" ]; then
        recorded=$(tr -d '[:space:]' < "$MONITOR_PID_FILE")
    fi

    if [ "$recorded" = "$$" ]; then
        rm -rf "$MONITOR_LOCK_DIR"
    fi
}


handle_monitor_signal() {
    cleanup_monitor_singleton
    exit 0
}


acquire_monitor_singleton() {
    local old_pid=""

    if ! mkdir "$MONITOR_LOCK_DIR" 2>/dev/null; then
        if [ -f "$MONITOR_PID_FILE" ]; then
            old_pid=$(tr -d '[:space:]' < "$MONITOR_PID_FILE")
        fi

        if is_same_monitor_pid "$old_pid"; then
            echo "❌ ${MONITOR_NAME} già attivo (PID $old_pid)" >&2
            return 1
        fi

        # Lock stale: il PID non appartiene più a questo monitor.
        rm -rf "$MONITOR_LOCK_DIR"

        if ! mkdir "$MONITOR_LOCK_DIR" 2>/dev/null; then
            echo "❌ impossibile acquisire lock ${MONITOR_NAME}" >&2
            return 1
        fi
    fi

    printf '%s\n' "$$" > "$MONITOR_PID_FILE"

    trap cleanup_monitor_singleton EXIT
    trap handle_monitor_signal INT TERM HUP

    return 0
}


log_msg() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}


read_env_value() {
    local key="$1"

    python3 - "$ENV_FILE" "$key" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
wanted = sys.argv[2]

if not path.exists():
    raise SystemExit(0)

for raw in path.read_text(errors="ignore").splitlines():
    line = raw.strip()

    if not line or line.startswith("#") or "=" not in line:
        continue

    key, value = line.split("=", 1)

    if key.strip() != wanted:
        continue

    value = value.strip()

    if (
        len(value) >= 2
        and value[0] == value[-1]
        and value[0] in ("'", '"')
    ):
        value = value[1:-1]

    print(value)
    break
PY
}


TELEGRAM_TOKEN="$(read_env_value TELEGRAM_BOT_TOKEN)"
TELEGRAM_CHAT="$(read_env_value TELEGRAM_CHAT_ID)"


send_telegram() {
    local text="$1"

    if [ -z "$TELEGRAM_TOKEN" ] || [ -z "$TELEGRAM_CHAT" ]; then
        return 0
    fi

    curl -fsS -m 10 \
        -X POST \
        "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
        --data-urlencode "chat_id=${TELEGRAM_CHAT}" \
        --data-urlencode "text=${text}" \
        > /dev/null 2>&1 || true
}


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


get_bot_pid() {
    local pid

    if [ -f "$PID_FILE" ]; then
        pid=$(tr -d '[:space:]' < "$PID_FILE")

        if is_expected_bot_pid "$pid"; then
            echo "$pid"
            return 0
        fi
    fi

    while read -r pid; do
        [ -n "$pid" ] || continue

        if is_expected_bot_pid "$pid"; then
            echo "$pid"
            return 0
        fi
    done < <(
        pgrep -u "$(id -u)" -f "$BOT_SCRIPT" 2>/dev/null
    )

    return 1
}


LAST_CYCLE_AGE=-1
CHECK_NOTE=""


check_last_cycle() {
    local pid="$1"
    local uptime
    local raw
    local last
    local now
    local diff

    uptime=$(ps -p "$pid" -o etimes= 2>/dev/null | tr -d ' ')

    # Processo appena partito: concedi tempo al primo ciclo.
    if [[ "$uptime" =~ ^[0-9]+$ ]] && [ "$uptime" -lt "$STARTUP_GRACE" ]; then
        CHECK_NOTE="startup grace (${uptime}s)"
        LAST_CYCLE_AGE=0
        return 0
    fi

    if [ ! -f "$CYCLE_FILE" ]; then
        CHECK_NOTE="last_cycle.txt assente"
        LAST_CYCLE_AGE=-1
        return 1
    fi

    raw=$(tr -d '[:space:]' < "$CYCLE_FILE")

    if ! [[ "$raw" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
        CHECK_NOTE="last_cycle.txt invalido"
        LAST_CYCLE_AGE=-1
        return 1
    fi

    last="${raw%.*}"
    now=$(date +%s)
    diff=$((now - last))

    # Protezione da eventuale clock correction.
    if [ "$diff" -lt 0 ]; then
        diff=0
    fi

    LAST_CYCLE_AGE="$diff"

    if [ "$diff" -gt "$MAX_IDLE_TIME" ]; then
        CHECK_NOTE="ultimo ciclo ${diff}s fa"
        return 1
    fi

    CHECK_NOTE="ultimo ciclo ${diff}s fa"
    return 0
}


restart_via_controller() {
    local reason="$1"

    log_msg "🚨 B21: $reason - restart delegato a bot_control.sh"

    send_telegram \
        "⚠️ QUANTUM V37 WATCHDOG
${reason}
Restart sicuro tramite controller ufficiale."

    if [ ! -x "$CONTROL_SCRIPT" ]; then
        log_msg "❌ Controller non disponibile: $CONTROL_SCRIPT"
        send_telegram "❌ V37: controller restart non disponibile"
        return 1
    fi

    # Avvio indipendente: il controller fermerà anche questo watchdog
    # e avvierà una nuova istanza monitor dopo il restart.
    nohup "$CONTROL_SCRIPT" restart \
        >> "$HOME/logs/watchdog_restart.log" 2>&1 &

    return 0
}


check_once() {
    local pid

    if ! pid=$(get_bot_pid); then
        echo "❌ BOT_PROCESS: NOT FOUND"
        return 1
    fi

    echo "✅ BOT_PROCESS: OK (PID $pid)"

    if check_last_cycle "$pid"; then
        echo "✅ LAST_CYCLE: OK ($CHECK_NOTE)"
        return 0
    fi

    echo "❌ LAST_CYCLE: FAIL ($CHECK_NOTE)"
    return 2
}


if [ "${1:-}" = "--check-once" ]; then
    check_once
    exit $?
fi

if ! acquire_monitor_singleton; then
    exit 1
fi


log_msg "✅ B21 watchdog avviato"

while true; do
    PID=""

    if ! PID=$(get_bot_pid); then
        restart_via_controller "Processo V37 non trovato"
        exit 0
    fi

    if ! check_last_cycle "$PID"; then
        restart_via_controller \
            "V37 senza ciclo valido: $CHECK_NOTE"
        exit 0
    fi

    sleep "$CHECK_INTERVAL"
done
