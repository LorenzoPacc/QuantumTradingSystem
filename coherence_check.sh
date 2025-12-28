#!/bin/bash

# 🔍 COHERENCE CHECK - Verifica coerenza tra log, state, processo e snapshot

LOG_FILE="quantum_v33_ultimate_final.log"
STATE_FILE="qv33_ultimate_final_state.json"
BOT_PID=27532

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        🔍 COHERENCE CHECK - SYSTEM CONSISTENCY TEST         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📅 Check time: $(date)"
echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. PROCESSO (BOT RUNNING)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  PROCESSO (PID $BOT_PID)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if ps -p $BOT_PID > /dev/null 2>&1; then
    echo "   ✅ Bot running: YES"
    
    # Quando è partito
    START_TIME=$(ps -p $BOT_PID -o lstart= | xargs)
    echo "   📅 Started: $START_TIME"
    
    # Uptime
    ELAPSED=$(ps -p $BOT_PID -o etime= | xargs)
    echo "   ⏱️  Uptime: $ELAPSED"
    
    # CPU e Memory
    CPU=$(ps -p $BOT_PID -o %cpu= | xargs)
    MEM=$(ps -p $BOT_PID -o %mem= | xargs)
    echo "   💻 CPU: ${CPU}% | Memory: ${MEM}%"
    
    # Comando
    CMD=$(ps -p $BOT_PID -o cmd= | xargs)
    echo "   🔧 Command: $CMD"
    
    PROCESS_OK=true
else
    echo "   ❌ Bot NOT running!"
    PROCESS_OK=false
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. LOG FILE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  LOG FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "$LOG_FILE" ]; then
    echo "   ✅ Log exists: YES"
    
    # Size
    LOG_SIZE=$(ls -lh "$LOG_FILE" | awk '{print $5}')
    echo "   📦 Size: $LOG_SIZE"
    
    # Last modified
    LOG_MODIFIED=$(stat -c '%y' "$LOG_FILE" | cut -d'.' -f1)
    echo "   🕐 Modified: $LOG_MODIFIED"
    
    # Ultimo ciclo nel log (ultimi 10000 righe per velocità)
    echo ""
    echo "   🔍 Searching last cycle (in last 10000 lines)..."
    LAST_CYCLE=$(tail -10000 "$LOG_FILE" | tac | grep -m 1 "CYCLE [0-9]* - 2025" || echo "NOT_FOUND")
    
    if [ "$LAST_CYCLE" != "NOT_FOUND" ]; then
        CYCLE_NUM=$(echo "$LAST_CYCLE" | grep -oP 'CYCLE \K[0-9]+')
        CYCLE_DATE=$(echo "$LAST_CYCLE" | grep -oP '\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
        echo "   📍 Last cycle: CYCLE $CYCLE_NUM"
        echo "   📅 Cycle date: $CYCLE_DATE"
        
        # Età del ciclo
        CYCLE_TS=$(date -d "$CYCLE_DATE" +%s 2>/dev/null)
        NOW_TS=$(date +%s)
        AGE_SEC=$((NOW_TS - CYCLE_TS))
        AGE_MIN=$((AGE_SEC / 60))
        
        echo "   ⏰ Cycle age: $AGE_MIN minutes ago"
        
        if [ $AGE_MIN -lt 5 ]; then
            echo "   ✅ Status: VERY RECENT (< 5 min)"
            LOG_OK=true
        elif [ $AGE_MIN -lt 60 ]; then
            echo "   ⚠️  Status: RECENT (< 1 hour)"
            LOG_OK=true
        elif [ $AGE_MIN -lt 1440 ]; then
            echo "   ⚠️  Status: OLD (< 24 hours)"
            LOG_OK=false
        else
            echo "   ❌ Status: VERY OLD (> 24 hours)"
            LOG_OK=false
        fi
    else
        echo "   ❌ Last cycle: NOT FOUND in last 10000 lines!"
        LOG_OK=false
    fi
else
    echo "   ❌ Log NOT found!"
    LOG_OK=false
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. STATE FILE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  STATE FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "$STATE_FILE" ]; then
    echo "   ✅ State exists: YES"
    
    # Size
    STATE_SIZE=$(ls -lh "$STATE_FILE" | awk '{print $5}')
    echo "   📦 Size: $STATE_SIZE"
    
    # Last modified
    STATE_MODIFIED=$(stat -c '%y' "$STATE_FILE" | cut -d'.' -f1)
    echo "   🕐 Modified: $STATE_MODIFIED"
    
    # Età modifica
    STATE_MOD_TS=$(stat -c '%Y' "$STATE_FILE")
    NOW_TS=$(date +%s)
    STATE_AGE_SEC=$((NOW_TS - STATE_MOD_TS))
    STATE_AGE_MIN=$((STATE_AGE_SEC / 60))
    
    echo "   ⏰ Modified: $STATE_AGE_MIN minutes ago"
    
    if [ $STATE_AGE_MIN -lt 5 ]; then
        echo "   ✅ Status: VERY RECENT (< 5 min)"
        STATE_OK=true
    elif [ $STATE_AGE_MIN -lt 60 ]; then
        echo "   ⚠️  Status: RECENT (< 1 hour)"
        STATE_OK=true
    else
        echo "   ❌ Status: OLD (> 1 hour)"
        STATE_OK=false
    fi
    
    # Contenuto
    echo ""
    echo "   📊 State content:"
    python3 << PYEOF 2>/dev/null
import json
try:
    with open('$STATE_FILE', 'r') as f:
        data = json.load(f)
    print(f"      • Positions: {len(data.get('positions', {}))}")
    print(f"      • Cash: \${data.get('cash', 0):.2f}")
    print(f"      • Total Value: \${data.get('total_value', 0):.2f}")
    print(f"      • Total PnL: \${data.get('total_pnl', 0):.2f}")
    print(f"      • Trades: {data.get('total_trades', 0)}")
    print(f"      • Win Rate: {data.get('win_rate', 0):.1f}%")
except Exception as e:
    print(f"      ❌ Error parsing: {e}")
PYEOF
    
else
    echo "   ❌ State NOT found!"
    STATE_OK=false
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. ATTIVITÀ OGGI (19/12/2025)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  ATTIVITÀ OGGI ($(date +%Y-%m-%d))"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TODAY=$(date +%Y-%m-%d)

# Cicli oggi
CYCLES_TODAY=$(grep "$TODAY" "$LOG_FILE" 2>/dev/null | grep -c "CYCLE [0-9]* -" || echo "0")
echo "   📊 Cycles today: $CYCLES_TODAY"

# BUY oggi
BUY_TODAY=$(grep "$TODAY" "$LOG_FILE" 2>/dev/null | grep -c "🟢 BUY" || echo "0")
echo "   🟢 BUY orders: $BUY_TODAY"

# SELL oggi
SELL_TODAY=$(grep "$TODAY" "$LOG_FILE" 2>/dev/null | grep -c "🔴 SELL" || echo "0")
echo "   🔴 SELL orders: $SELL_TODAY"

# Errori oggi
ERRORS_TODAY=$(grep "$TODAY" "$LOG_FILE" 2>/dev/null | grep -c " - ERROR - " || echo "0")
echo "   ❌ Errors: $ERRORS_TODAY"

if [ $CYCLES_TODAY -gt 0 ]; then
    echo "   ✅ Activity: ACTIVE today"
    ACTIVITY_OK=true
else
    echo "   ⚠️  Activity: NO cycles today"
    ACTIVITY_OK=false
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. COERENZA TEMPORALE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  COERENZA TEMPORALE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Confronta età state vs ultimo ciclo
if [ "$LOG_OK" = true ] && [ "$STATE_OK" = true ]; then
    TIME_DIFF=$((STATE_AGE_MIN - AGE_MIN))
    TIME_DIFF_ABS=${TIME_DIFF#-}  # valore assoluto
    
    echo "   📊 State age: $STATE_AGE_MIN min"
    echo "   📊 Cycle age: $AGE_MIN min"
    echo "   📊 Difference: $TIME_DIFF min"
    
    if [ $TIME_DIFF_ABS -lt 10 ]; then
        echo "   ✅ Temporal coherence: GOOD (< 10 min diff)"
        TEMPORAL_OK=true
    elif [ $TIME_DIFF_ABS -lt 60 ]; then
        echo "   ⚠️  Temporal coherence: ACCEPTABLE (< 1 hour diff)"
        TEMPORAL_OK=true
    else
        echo "   ❌ Temporal coherence: BAD (> 1 hour diff)"
        TEMPORAL_OK=false
    fi
else
    echo "   ⚠️  Cannot check (log or state issues)"
    TEMPORAL_OK=false
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. FILE APERTI DAL PROCESSO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  FILE APERTI DAL PROCESSO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$PROCESS_OK" = true ]; then
    echo "   🔍 Files opened by PID $BOT_PID:"
    echo ""
    
    # Log file
    LOG_OPEN=$(lsof -p $BOT_PID 2>/dev/null | grep "$LOG_FILE" | wc -l)
    if [ $LOG_OPEN -gt 0 ]; then
        echo "   ✅ Log file: OPEN for writing"
        lsof -p $BOT_PID 2>/dev/null | grep "$LOG_FILE" | awk '{print "      Mode:", $4, "| File:", $9}'
        FILES_OK=true
    else
        echo "   ❌ Log file: NOT open!"
        FILES_OK=false
    fi
    
    echo ""
    
    # State file
    STATE_OPEN=$(lsof -p $BOT_PID 2>/dev/null | grep "state" | wc -l)
    if [ $STATE_OPEN -gt 0 ]; then
        echo "   ℹ️  State files accessed:"
        lsof -p $BOT_PID 2>/dev/null | grep "state" | awk '{print "      •", $9}'
    else
        echo "   ℹ️  State file: Not currently open (normal, opened on save)"
    fi
else
    echo "   ⚠️  Process not running, cannot check"
    FILES_OK=false
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. VERDETTO FINALE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 VERDETTO FINALE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Conta quanti check sono passati
CHECKS_PASSED=0
CHECKS_TOTAL=6

[ "$PROCESS_OK" = true ] && CHECKS_PASSED=$((CHECKS_PASSED + 1))
[ "$LOG_OK" = true ] && CHECKS_PASSED=$((CHECKS_PASSED + 1))
[ "$STATE_OK" = true ] && CHECKS_PASSED=$((CHECKS_PASSED + 1))
[ "$ACTIVITY_OK" = true ] && CHECKS_PASSED=$((CHECKS_PASSED + 1))
[ "$TEMPORAL_OK" = true ] && CHECKS_PASSED=$((CHECKS_PASSED + 1))
[ "$FILES_OK" = true ] && CHECKS_PASSED=$((CHECKS_PASSED + 1))

echo "   📊 Checks passed: $CHECKS_PASSED/$CHECKS_TOTAL"
echo ""

# Status per componente
echo "   Component status:"
[ "$PROCESS_OK" = true ] && echo "   ✅ Process: OK" || echo "   ❌ Process: FAIL"
[ "$LOG_OK" = true ] && echo "   ✅ Log: OK" || echo "   ❌ Log: FAIL"
[ "$STATE_OK" = true ] && echo "   ✅ State: OK" || echo "   ❌ State: FAIL"
[ "$ACTIVITY_OK" = true ] && echo "   ✅ Activity: OK" || echo "   ⚠️  Activity: NO CYCLES TODAY"
[ "$TEMPORAL_OK" = true ] && echo "   ✅ Temporal: OK" || echo "   ❌ Temporal: INCOHERENT"
[ "$FILES_OK" = true ] && echo "   ✅ Files: OK" || echo "   ❌ Files: FAIL"

echo ""

# Verdetto globale
if [ $CHECKS_PASSED -eq $CHECKS_TOTAL ]; then
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  ✅ COHERENCE: PERFECT                                      ║"
    echo "║                                                              ║"
    echo "║  All components are aligned and working correctly!          ║"
    echo "║  Bot is healthy and operational. 🚀                         ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
elif [ $CHECKS_PASSED -ge 4 ]; then
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  ⚠️  COHERENCE: GOOD (minor issues)                         ║"
    echo "║                                                              ║"
    echo "║  Most components OK. Check warnings above.                  ║"
    echo "║  Bot functional but monitor closely.                        ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
else
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  🚨 COHERENCE: POOR (critical issues)                       ║"
    echo "║                                                              ║"
    echo "║  Major inconsistencies detected!                            ║"
    echo "║  Bot may not be functioning correctly.                      ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📅 Check completed: $(date)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"EOF
