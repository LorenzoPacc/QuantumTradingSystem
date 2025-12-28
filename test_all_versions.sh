#!/bin/bash
# Test Framework per 3 versioni

echo "🧪 QUANTUM TRADING V34 - TEST FRAMEWORK"
echo "========================================================================"
echo ""

# Stop any running bot
pkill -9 -f quantum_v34
pkill -9 -f simple_strategy

# Create test directories
mkdir -p test_results/{mtf40,inverted,simple}

echo "📊 CONFIGURAZIONE TEST:"
echo "   Durata: 24 ore (recommended) o 6 ore (quick test)"
echo "   Modalità: Paper Trading (DRY_RUN=True)"
echo ""

read -p "Vuoi test QUICK (6h) o FULL (24h)? [q/f]: " test_duration

if [ "$test_duration" = "q" ]; then
    TEST_HOURS=6
    CYCLES=180  # 6 ore * 30 cicli/ora (2min/ciclo)
else
    TEST_HOURS=24
    CYCLES=720  # 24 ore * 30 cicli/ora
fi

echo ""
echo "✅ Test configurato per $TEST_HOURS ore ($CYCLES cicli)"
echo ""

# Function to run test
run_test() {
    local version=$1
    local script=$2
    local logfile=$3
    
    echo "🚀 Avvio test: $version"
    nohup python3 -u "$script" > "$logfile" 2>&1 &
    local pid=$!
    echo "   PID: $pid"
    echo "$pid" > "test_results/${version}/pid.txt"
    echo "$version:$pid:$(date)" >> test_results/test_tracker.txt
}

# Test Version 1: MTF 40%
if [ -f quantum_v34_integrated.py ]; then
    echo "VERSION 1: MTF 40%"
    run_test "mtf40" "quantum_v34_integrated.py" "test_results/mtf40/test.log"
    sleep 5
fi

# Test Version 2: Inverted Logic
if [ -f quantum_v34_integrated_inverted.py ]; then
    echo "VERSION 2: Inverted Logic"
    # Rename temporaneamente per test
    cp quantum_v34_integrated_inverted.py test_results/inverted/quantum_test.py
    run_test "inverted" "test_results/inverted/quantum_test.py" "test_results/inverted/test.log"
    sleep 5
fi

# Test Version 3: Simple Strategy
if [ -f simple_strategy_test.py ]; then
    echo "VERSION 3: Simple Strategy"
    run_test "simple" "simple_strategy_test.py" "test_results/simple/test.log"
fi

echo ""
echo "========================================================================"
echo "✅ TUTTI I TEST AVVIATI"
echo "========================================================================"
echo ""
echo "📊 Monitora con:"
echo "   ./monitor_tests.sh"
echo ""
echo "⏱️  Tempo stimato: $TEST_HOURS ore"
echo "📅 Fine prevista: $(date -d "+${TEST_HOURS} hours" 2>/dev/null || date)"
echo ""
echo "⚠️  NON fermare i processi manualmente!"
echo "   Usa: ./stop_tests.sh per fermare tutto"
echo ""

