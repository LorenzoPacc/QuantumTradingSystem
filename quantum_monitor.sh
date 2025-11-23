#!/bin/bash
echo "🔍 Quantum Monitor - $(date)"
echo "=========================="

# Bot corretto
if ps aux | grep -q "[q]uantum_simple_fixed.py"; then
    echo "✅ Bot: RUNNING"
    
    # State file corretto
    if [ -f "quantum_v2_state.json" ]; then
        python3 << 'PY'
import json
try:
    with open("quantum_v2_state.json") as f:
        state = json.load(f)
    
    cash = state.get("cash_balance", 0)
    portfolio = state.get("portfolio", {})
    positions = len(portfolio)
    
    invested = sum(p.get("total_cost", 0) for p in portfolio.values())
    total = cash + invested
    
    print(f"💰 Cash: ${cash:.2f}")
    print(f"📦 Posizioni: {positions}/6")
    print(f"💎 Total: ${total:.2f}")
    
    if positions > 0:
        print(f"\n📊 Posizioni attive:")
        for sym, pos in portfolio.items():
            qty = pos.get("quantity", 0)
            cost = pos.get("total_cost", 0)
            print(f"   {sym}: {qty:.6f} (${cost:.2f})")
except Exception as e:
    print(f"❌ Errore: {e}")
PY
    else
        echo "⚠️ State file non trovato"
    fi
else
    echo "❌ Bot: STOPPED"
fi

# Fear & Greed
echo ""
fg=$(curl -s "https://api.alternative.me/fng/?limit=1" | python3 -c "import json,sys;d=json.load(sys.stdin)['data'][0];print(f'{d[\"value\"]} ({d[\"value_classification\"]})')" 2>/dev/null)
echo "🎯 Fear & Greed: $fg"

echo "=========================="
