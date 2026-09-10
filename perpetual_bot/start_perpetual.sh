#!/bin/bash

BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$BOT_DIR/../venv/bin/activate"
PID_FILE="$BOT_DIR/perpetual_bot.pid"
LOG_FILE="$BOT_DIR/perpetual_output.log"
LOCK_FILE="$BOT_DIR/perpetual_start.lock"

# Impedisce due avvii simultanei da shell diverse
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
    echo "⚠️ Perpetual Bot start already in progress"
    exit 0
fi

find_running_bot() {
    for PID in $(pgrep -f '[p]ython3 -u main.py' 2>/dev/null); do
        CWD=$(readlink -f "/proc/$PID/cwd" 2>/dev/null)
        CMD=$(tr '\0' ' ' < "/proc/$PID/cmdline" 2>/dev/null)

        if [ "$CWD" = "$BOT_DIR" ] && [[ "$CMD" == *"main.py"* ]]; then
            echo "$PID"
            return 0
        fi
    done

    return 1
}

is_bot_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")

        if [[ "$PID" =~ ^[0-9]+$ ]] && [ -d "/proc/$PID" ]; then
            CWD=$(readlink -f "/proc/$PID/cwd" 2>/dev/null)
            CMD=$(tr '\0' ' ' < "/proc/$PID/cmdline" 2>/dev/null)

            if [ "$CWD" = "$BOT_DIR" ] && [[ "$CMD" == *"main.py"* ]]; then
                return 0
            fi
        fi

        rm -f "$PID_FILE"
    fi

    EXISTING_PID=$(find_running_bot)

    if [ -n "$EXISTING_PID" ]; then
        echo "$EXISTING_PID" > "$PID_FILE"
        return 0
    fi

    return 1
}

echo "🚀 Starting Perpetual Bot V1..."

if is_bot_running; then
    echo "⚠️ Perpetual Bot already running (PID: $(cat "$PID_FILE"))"
    exit 0
fi

cd "$BOT_DIR" || exit 1
source "$VENV"

nohup python3 -u main.py > "$LOG_FILE" 2>&1 9>&- &
NEW_PID=$!
echo "$NEW_PID" > "$PID_FILE"

sleep 2

if is_bot_running; then
    echo "✅ Perpetual Bot started (PID: $(cat "$PID_FILE"))"
    echo "📋 Monitor: tail -f $LOG_FILE"
    exit 0
else
    echo "❌ Perpetual Bot failed to start"
    rm -f "$PID_FILE"
    exit 1
fi
