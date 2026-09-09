#!/bin/bash

# ============================================================
# QUANTUM CONNECTION MONITOR - B23a
# Monitor passivo Internet + Binance
# Nessuna azione diretta sul trading bot
# ============================================================

BOT_DIR="$HOME/trading_project/QuantumTradingSystem"
ENV_FILE="$BOT_DIR/.env"

LOG_FILE="$HOME/connection_monitor.log"

OFFLINE_FLAG="$HOME/bot_offline.flag"
OFFLINE_SINCE_FILE="$HOME/offline_since.txt"

MIN_OFFLINE_DURATION=300
MIN_ONLINE_DURATION=120
CHECK_INTERVAL=30


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


check_internet() {
    ping -c 1 -W 2 8.8.8.8 > /dev/null 2>&1
}


check_binance() {
    curl -fsS -m 5 \
        "https://api.binance.com/api/v3/ping" \
        > /dev/null 2>&1
}


check_once() {
    local internet="FAIL"
    local binance="FAIL"
    local rc=0

    if check_internet; then
        internet="OK"
    else
        rc=1
    fi

    if check_binance; then
        binance="OK"
    else
        rc=1
    fi

    echo "INTERNET: $internet"
    echo "BINANCE : $binance"

    return "$rc"
}


if [ "${1:-}" = "--check-once" ]; then
    check_once
    exit $?
fi


consecutive_online=0
notification_sent=false

log_msg "✅ B23a connection monitor avviato"

while true; do
    internet_ok=false
    binance_ok=false

    if check_internet; then
        internet_ok=true
    fi

    if check_binance; then
        binance_ok=true
    fi

    if [ "$internet_ok" = false ] || [ "$binance_ok" = false ]; then
        consecutive_online=0

        if [ ! -f "$OFFLINE_FLAG" ]; then
            date +%s > "$OFFLINE_SINCE_FILE"
            touch "$OFFLINE_FLAG"

            log_msg \
                "📡 Problema connessione rilevato; attendo debounce"
        fi

        if [ -f "$OFFLINE_SINCE_FILE" ]; then
            offline_since=$(cat "$OFFLINE_SINCE_FILE")
            now=$(date +%s)
            offline_duration=$((now - offline_since))

            if \
                [ "$offline_duration" -ge "$MIN_OFFLINE_DURATION" ] \
                && [ "$notification_sent" = false ]
            then
                offline_min=$((offline_duration / 60))

                if [ "$internet_ok" = false ]; then
                    log_msg \
                        "❌ Internet down da ${offline_min} minuti"

                    send_telegram \
                        "⚠️ QUANTUM: Internet non disponibile da ${offline_min}+ minuti."
                else
                    log_msg \
                        "⚠️ Binance API non raggiungibile da ${offline_min} minuti"

                    send_telegram \
                        "⚠️ QUANTUM: Binance API non raggiungibile da ${offline_min}+ minuti."
                fi

                notification_sent=true
            fi
        fi

    else
        if [ -f "$OFFLINE_FLAG" ]; then
            consecutive_online=$((consecutive_online + 1))
            online_seconds=$((consecutive_online * CHECK_INTERVAL))

            if [ "$online_seconds" -ge "$MIN_ONLINE_DURATION" ]; then
                if [ -f "$OFFLINE_SINCE_FILE" ]; then
                    offline_since=$(cat "$OFFLINE_SINCE_FILE")
                    now=$(date +%s)
                    total_offline=$((now - offline_since))
                    offline_min=$((total_offline / 60))

                    if [ "$notification_sent" = true ]; then
                        log_msg \
                            "✅ Connessione ripristinata dopo ${offline_min} min"

                        send_telegram \
                            "✅ QUANTUM: connessione ripristinata dopo ${offline_min} minuti."
                    else
                        log_msg \
                            "✅ Breve interruzione risolta; nessun alert inviato"
                    fi
                fi

                rm -f "$OFFLINE_FLAG" "$OFFLINE_SINCE_FILE"

                notification_sent=false
                consecutive_online=0
            fi
        else
            consecutive_online=0
        fi
    fi

    sleep "$CHECK_INTERVAL"
done
