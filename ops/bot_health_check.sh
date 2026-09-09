#!/bin/bash

# ============================================================
# QUANTUM V37 HEALTH MONITOR - B23b
# Diagnostica passiva: nessun restart / kill / modifica V37
# ============================================================

BOT_DIR="$HOME/trading_project/QuantumTradingSystem"
BOT_SCRIPT="autonomous_trading_bot_improved.py"
PID_FILE="$BOT_DIR/bot.pid"
CYCLE_FILE="$BOT_DIR/last_cycle.txt"
BOT_LOG="$BOT_DIR/autonomous_bot.log"
ENV_FILE="$BOT_DIR/.env"

LOG_FILE="$HOME/bot_health.log"

CYCLE_ALERT_FLAG="$HOME/.quantum_health_cycle_alert"
ERROR_ALERT_FLAG="$HOME/.quantum_health_error_alert"

# Warning prima del watchdog B21 (che interviene a 3h).
MAX_CYCLE_AGE=9000       # 2.5 ore
STARTUP_GRACE=300        # 5 minuti
CHECK_INTERVAL=1800      # 30 minuti

# Errori recenti nel log.
ERROR_TAIL_LINES=200
ERROR_THRESHOLD=5


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

    if [ ! -f "$PID_FILE" ]; then
        return 1
    fi

    pid=$(tr -d '[:space:]' < "$PID_FILE")

    if is_expected_bot_pid "$pid"; then
        echo "$pid"
        return 0
    fi

    return 1
}


CYCLE_NOTE=""
CYCLE_AGE=-1


check_last_cycle() {
    local pid="$1"
    local uptime
    local raw
    local last
    local now
    local diff

    uptime=$(ps -p "$pid" -o etimes= 2>/dev/null | tr -d ' ')

    if [[ "$uptime" =~ ^[0-9]+$ ]] && [ "$uptime" -lt "$STARTUP_GRACE" ]; then
        CYCLE_NOTE="startup grace (${uptime}s)"
        CYCLE_AGE=0
        return 0
    fi

    if [ ! -f "$CYCLE_FILE" ]; then
        CYCLE_NOTE="last_cycle.txt assente"
        CYCLE_AGE=-1
        return 1
    fi

    raw=$(tr -d '[:space:]' < "$CYCLE_FILE")

    if ! [[ "$raw" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
        CYCLE_NOTE="last_cycle.txt invalido"
        CYCLE_AGE=-1
        return 1
    fi

    last="${raw%.*}"
    now=$(date +%s)
    diff=$((now - last))

    if [ "$diff" -lt 0 ]; then
        diff=0
    fi

    CYCLE_AGE="$diff"

    if [ "$diff" -gt "$MAX_CYCLE_AGE" ]; then
        CYCLE_NOTE="ultimo ciclo ${diff}s fa"
        return 1
    fi

    CYCLE_NOTE="ultimo ciclo ${diff}s fa"
    return 0
}


ERROR_COUNT=0


check_recent_errors() {
    if [ ! -f "$BOT_LOG" ]; then
        ERROR_COUNT=0
        return 0
    fi

    ERROR_COUNT=$(
        tail -n "$ERROR_TAIL_LINES" "$BOT_LOG" \
        | grep -Ei '(^|[[:space:]-])(ERROR|CRITICAL)([[:space:]:-]|$)|Traceback' \
        | wc -l
    )

    if [ "$ERROR_COUNT" -gt "$ERROR_THRESHOLD" ]; then
        return 1
    fi

    return 0
}


check_once() {
    local pid
    local rc=0

    if pid=$(get_bot_pid); then
        echo "BOT_PROCESS : OK (PID $pid)"

        if check_last_cycle "$pid"; then
            echo "LAST_CYCLE  : OK ($CYCLE_NOTE)"
        else
            echo "LAST_CYCLE  : FAIL ($CYCLE_NOTE)"
            rc=1
        fi
    else
        echo "BOT_PROCESS : FAIL"
        echo "LAST_CYCLE  : N/A"
        rc=1
    fi

    if check_recent_errors; then
        echo "RECENT_ERRORS: OK ($ERROR_COUNT)"
    else
        echo "RECENT_ERRORS: FAIL ($ERROR_COUNT)"
        rc=1
    fi

    return "$rc"
}


if [ "${1:-}" = "--check-once" ]; then
    check_once
    exit $?
fi


log_msg "✅ B23b health monitor avviato"

while true; do
    pid=""

    if pid=$(get_bot_pid); then
        if check_last_cycle "$pid"; then
            if [ -f "$CYCLE_ALERT_FLAG" ]; then
                rm -f "$CYCLE_ALERT_FLAG"

                log_msg "✅ Cicli V37 tornati regolari"

                send_telegram \
                    "✅ QUANTUM V37: attività cicli tornata regolare."
            fi
        else
            if [ ! -f "$CYCLE_ALERT_FLAG" ]; then
                touch "$CYCLE_ALERT_FLAG"

                log_msg \
                    "⚠️ Health warning: $CYCLE_NOTE"

                send_telegram \
                    "⚠️ QUANTUM V37 HEALTH
$CYCLE_NOTE
Health monitor passivo: nessuna azione automatica."
            fi
        fi
    else
        if [ ! -f "$CYCLE_ALERT_FLAG" ]; then
            touch "$CYCLE_ALERT_FLAG"

            log_msg "⚠️ Health warning: processo V37 non valido"

            send_telegram \
                "⚠️ QUANTUM V37 HEALTH
Processo V37 non rilevato correttamente.
Health monitor passivo: nessuna azione automatica."
        fi
    fi


    if check_recent_errors; then
        if [ -f "$ERROR_ALERT_FLAG" ]; then
            rm -f "$ERROR_ALERT_FLAG"

            log_msg "✅ Livello errori V37 tornato normale"

            send_telegram \
                "✅ QUANTUM V37: livello errori recente tornato normale."
        fi
    else
        if [ ! -f "$ERROR_ALERT_FLAG" ]; then
            touch "$ERROR_ALERT_FLAG"

            log_msg \
                "⚠️ Health warning: ${ERROR_COUNT} errori recenti"

            send_telegram \
                "⚠️ QUANTUM V37 HEALTH
Rilevati ${ERROR_COUNT} ERROR/CRITICAL/Traceback nelle ultime ${ERROR_TAIL_LINES} righe.
Controllare i log."
        fi
    fi

    sleep "$CHECK_INTERVAL"
done
