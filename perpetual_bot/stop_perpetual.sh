#!/bin/bash

BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$BOT_DIR/perpetual_bot.pid"


is_expected_bot() {
    local pid="$1"

    [[ "$pid" =~ ^[0-9]+$ ]] || return 1
    [ -d "/proc/$pid" ] || return 1

    local cwd cmd
    cwd=$(readlink -f "/proc/$pid/cwd" 2>/dev/null)
    cmd=$(tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null)

    [ "$cwd" = "$BOT_DIR" ] && [[ "$cmd" == *"main.py"* ]]
}


find_running_bot() {
    local pid

    for pid in $(pgrep -f '[p]ython3 -u main.py' 2>/dev/null); do
        if is_expected_bot "$pid"; then
            echo "$pid"
            return 0
        fi
    done

    return 1
}


PID=""

if [ -f "$PID_FILE" ]; then
    CANDIDATE=$(cat "$PID_FILE" 2>/dev/null)

    if is_expected_bot "$CANDIDATE"; then
        PID="$CANDIDATE"
    fi
fi

if [ -z "$PID" ]; then
    PID=$(find_running_bot)
fi

if [ -z "$PID" ]; then
    rm -f "$PID_FILE"
    echo "⚠️ Perpetual Bot is not running"
    exit 0
fi

echo "🛑 Requesting graceful shutdown (PID: $PID)..."
kill -TERM "$PID" 2>/dev/null || {
    echo "❌ Unable to send SIGTERM"
    exit 1
}

for i in {1..30}; do
    if [ ! -d "/proc/$PID" ]; then
        rm -f "$PID_FILE"
        echo "✅ Perpetual Bot stopped gracefully"
        exit 0
    fi

    sleep 1
done

echo "❌ Perpetual Bot did not stop within 30 seconds"
echo "⚠️ SIGKILL NOT sent automatically to protect trading state"
exit 1
