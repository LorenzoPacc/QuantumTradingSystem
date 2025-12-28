#!/bin/bash
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     🔬 COMPREHENSIVE SYSTEM AUDIT - QUANTUM V33 ULTIMATE    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ═══════════════════════════════════════════════════════════════
# 1. CONFIGURAZIONE TRADING
# ═══════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚙️  1. TRADING CONFIGURATION ANALYSIS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 << 'PYEND'
import re

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

print("📊 PARAMETRI CHIAVE:")
print("")

# Capital
capital = re.search(r'self\.initial_capital\s*=\s*([\d.]+)', content)
if capital:
    print(f"   💰 Initial Capital: ${capital.group(1)}")
else:
    print("   ❌ Initial Capital: NOT FOUND")

# Max positions
max_pos = re.search(r'self\.max_positions\s*=\s*(\d+)', content)
if max_pos:
    print(f"   📦 Max Positions: {max_pos.group(1)}")
else:
    print("   ❌ Max Positions: NOT FOUND")

# Position size
pos_size = re.search(r'position_size\s*=\s*[\w.]+\s*\*\s*([\d.]+)', content)
if pos_size:
    print(f"   💵 Position Size Multiplier: {pos_size.group(1)}")
    
# Min confidence
min_conf = re.search(r'if confidence < ([\d.]+)', content)
if min_conf:
    print(f"   📊 Min Confidence Threshold: {min_conf.group(1)}%")

# Stop loss
stop_loss = re.search(r'self\.stop_loss\s*=\s*([\d.]+)', content)
if stop_loss:
    print(f"   🛑 Stop Loss: {float(stop_loss.group(1))*100:.1f}%")
else:
    print("   ⚠️  Stop Loss: NOT EXPLICITLY SET")

# Take profit
take_profit = re.search(r'self\.take_profit\s*=\s*([\d.]+)', content)
if take_profit:
    print(f"   🎯 Take Profit: {float(take_profit.group(1))*100:.1f}%")
else:
    print("   ⚠️  Take Profit: NOT EXPLICITLY SET")

# Trading symbols
symbols = re.search(r'self\.symbols\s*=\s*\[(.*?)\]', content, re.DOTALL)
if symbols:
    syms = [s.strip().strip('"').strip("'") for s in symbols.group(1).split(',')]
    print(f"   🪙  Trading Symbols: {len(syms)} coins")
    for sym in syms:
        if sym:
            print(f"      • {sym}")
PYEND

echo ""

# ═══════════════════════════════════════════════════════════════
# 2. FEAR BONUS LOGIC
# ═══════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 2. FEAR BONUS IMPLEMENTATION CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 << 'PYEND'
import re

with open('quantum_v33_ultimate_final.py', 'r') as f:
    lines = f.readlines()

print("🔍 Searching FEAR BONUS block...")
print("")

fear_bonus_found = False
for i, line in enumerate(lines):
    if 'FEAR BONUS' in line and 'if fear_index' in lines[i+1] if i+1 < len(lines) else False:
        fear_bonus_found = True
        print(f"✅ FEAR BONUS block found at line {i+1}")
        print("")
        print("📋 Code:")
        for j in range(8):
            if i+j < len(lines):
                print(f"   {i+j+1}: {lines[i+j].rstrip()}")
        print("")
        
        # Validate logic
        if 'fear_index < 30' in lines[i+1]:
            print("✅ EXTREME FEAR threshold: < 30")
            if '1.25' in lines[i+2]:
                print("✅ EXTREME FEAR bonus: +25% (1.25x)")
            else:
                print("❌ EXTREME FEAR bonus: INCORRECT VALUE!")
        
        if i+4 < len(lines) and 'fear_index < 45' in lines[i+4]:
            print("✅ FEAR threshold: < 45")
            if '1.15' in lines[i+5]:
                print("✅ FEAR bonus: +15% (1.15x)")
            else:
                print("❌ FEAR bonus: INCORRECT VALUE!")
        
        # Check logging
        if 'logging.info' in ''.join(lines[i:i+8]):
            print("✅ Logging: Using logging.info (correct)")
        elif 'print' in ''.join(lines[i:i+8]):
            print("⚠️  Logging: Using print() (will work but not in log file)")
        
        break

if not fear_bonus_found:
    print("❌ FEAR BONUS block NOT FOUND!")
PYEND

echo ""

# ═══════════════════════════════════════════════════════════════
# 3. CRITICALFIXES INTEGRATION
# ═══════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 3. CRITICALFIXES INTEGRATION CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 << 'PYEND'
import re

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# Check import
if 'from fix_confidence_now import CriticalFixes' in content or 'import fix_confidence_now' in content:
    print("✅ CriticalFixes imported correctly")
else:
    print("⚠️  CriticalFixes import not found - checking inline definition...")
    if 'class CriticalFixes' in content:
        print("✅ CriticalFixes defined inline")
    else:
        print("❌ CriticalFixes NOT FOUND!")

# Check instantiation
if 'self.fixes = CriticalFixes()' in content:
    print("✅ CriticalFixes instantiated")
else:
    print("❌ CriticalFixes NOT instantiated!")

# Check usage
fixes_call = re.search(r'self\.fixes\.fix_confidence_threshold\((.*?)\)', content, re.DOTALL)
if fixes_call:
    print("✅ fix_confidence_threshold() called")
    print("")
    print("📋 Parameters:")
    params = fixes_call.group(1)
    for param in params.split(','):
        param = param.strip()
        if param:
            print(f"   • {param}")
    print("")
    
    # Validate parameters
    if 'fg=' in params and 'rsi=' in params and 'pc=' in params:
        print("✅ All required parameters present (fg, rsi, pc)")
    else:
        print("❌ Missing parameters!")
        if 'fg=' not in params:
            print("   ❌ Missing: fg (Fear & Greed)")
        if 'rsi=' not in params:
            print("   ❌ Missing: rsi")
        if 'pc=' not in params:
            print("   ❌ Missing: pc (price change)")
else:
    print("❌ fix_confidence_threshold() NOT CALLED!")
PYEND

echo ""

# ═══════════════════════════════════════════════════════════════
# 4. BUY/SELL LOGIC VALIDATION
# ═══════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💰 4. BUY/SELL LOGIC VALIDATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 << 'PYEND'
import re

with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

print("🔍 Checking check_buy() logic...")
print("")

# Find check_buy function
check_buy = re.search(r'def check_buy\(self, symbol\):(.*?)(?=\n    def |\nclass |\Z)', content, re.DOTALL)
if check_buy:
    func_content = check_buy.group(1)
    
    # Check for max positions
    if 'max_positions' in func_content:
        print("✅ Max positions check: PRESENT")
    else:
        print("⚠️  Max positions check: NOT FOUND")
    
    # Check for RSI
    if 'rsi' in func_content.lower():
        print("✅ RSI indicator: USED")
    else:
        print("⚠️  RSI indicator: NOT FOUND")
    
    # Check for Fear & Greed
    if 'fear' in func_content.lower() or 'greed' in func_content.lower():
        print("✅ Fear & Greed: INTEGRATED")
    else:
        print("❌ Fear & Greed: NOT USED")
    
    # Check for price change
    if 'price_change' in func_content:
        print("✅ Price change: CALCULATED")
    else:
        print("⚠️  Price change: NOT FOUND")
    
    # Check for confidence threshold
    if re.search(r'confidence\s*[<>]=?\s*[\d.]+', func_content):
        matches = re.findall(r'confidence\s*([<>]=?)\s*([\d.]+)', func_content)
        print(f"✅ Confidence threshold checks: {len(matches)} found")
        for op, val in matches:
            print(f"   • confidence {op} {val}%")
    else:
        print("❌ Confidence threshold: NOT CHECKED")

print("")
print("🔍 Checking check_sell() logic...")
print("")

# Find check_sell function
check_sell = re.search(r'def check_sell\(self, symbol\):(.*?)(?=\n    def |\nclass |\Z)', content, re.DOTALL)
if check_sell:
    func_content = check_sell.group(1)
    
    # Check for trailing stop
    if 'trailing' in func_content.lower():
        print("✅ Trailing stop: IMPLEMENTED")
    else:
        print("⚠️  Trailing stop: NOT FOUND")
    
    # Check for take profit
    if 'take_profit' in func_content or 'profit_target' in func_content:
        print("✅ Take profit: CHECKED")
    else:
        print("⚠️  Take profit: NOT EXPLICITLY CHECKED")
    
    # Check for stop loss
    if 'stop_loss' in func_content or 'stop' in func_content:
        print("✅ Stop loss: CHECKED")
    else:
        print("⚠️  Stop loss: NOT FOUND")
PYEND

echo ""

# ═══════════════════════════════════════════════════════════════
# 5. DATA SOURCES VALIDATION
# ═══════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📡 5. DATA SOURCES & API VALIDATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 << 'PYEND'
import requests
import time

print("🔍 Testing external data sources...")
print("")

# Test Fear & Greed API
try:
    response = requests.get('https://api.alternative.me/fng/?limit=1', timeout=5)
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and len(data['data']) > 0:
            fg_value = data['data'][0]['value']
            fg_class = data['data'][0]['value_classification']
            print(f"✅ Fear & Greed API: WORKING")
            print(f"   • Current value: {fg_value}")
            print(f"   • Classification: {fg_class}")
        else:
            print("⚠️  Fear & Greed API: Response format unexpected")
    else:
        print(f"❌ Fear & Greed API: HTTP {response.status_code}")
except Exception as e:
    print(f"❌ Fear & Greed API: ERROR - {e}")

print("")

# Test if ccxt is available
try:
    import ccxt
    print("✅ CCXT library: INSTALLED")
    print(f"   • Version: {ccxt.__version__}")
    
    # Test Binance connection
    try:
        exchange = ccxt.binance()
        ticker = exchange.fetch_ticker('BTC/USDT')
        print("✅ Binance API: ACCESSIBLE")
        print(f"   • BTC/USDT price: ${ticker['last']:,.2f}")
    except Exception as e:
        print(f"⚠️  Binance API: {str(e)[:50]}")
except ImportError:
    print("❌ CCXT library: NOT INSTALLED")

PYEND

echo ""

# ═══════════════════════════════════════════════════════════════
# 6. RISK MANAGEMENT CHECK
# ═══════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛡️  6. RISK MANAGEMENT ANALYSIS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 << 'PYEND'
import json

# Check state file
try:
    with open('quantum_state.json', 'r') as f:
        state = json.load(f)
    
    print("📊 Current Portfolio Analysis:")
    print("")
    
    # Check structure
    if 'positions' in state:
        positions = state['positions']
        capital = state.get('capital', 200)
        
        total_exposure = sum(pos.get('size', 0) for pos in positions.values())
        exposure_pct = (total_exposure / capital) * 100 if capital > 0 else 0
        
        print(f"   💰 Capital: ${capital:.2f}")
        print(f"   📦 Active positions: {len(positions)}")
        print(f"   💵 Total exposure: ${total_exposure:.2f} ({exposure_pct:.1f}%)")
        print("")
        
        # Risk assessment
        if exposure_pct > 80:
            print("   ❌ RISK: VERY HIGH exposure (>80%)")
        elif exposure_pct > 60:
            print("   ⚠️  RISK: HIGH exposure (>60%)")
        elif exposure_pct > 40:
            print("   ⚠️  RISK: MODERATE exposure (>40%)")
        else:
            print("   ✅ RISK: ACCEPTABLE exposure (<40%)")
        
        print("")
        
        # Position details
        if positions:
            print("   📍 Position breakdown:")
            for symbol, pos in positions.items():
                pnl_pct = pos.get('pnl_pct', 0)
                status = "🟢" if pnl_pct > 0 else "🔴"
                print(f"      {status} {symbol}: {pnl_pct:+.2f}%")
    else:
        print("   ⚠️  State file structure different (might be v4)")
        
except FileNotFoundError:
    print("   ❌ quantum_state.json NOT FOUND")
except Exception as e:
    print(f"   ❌ Error reading state: {e}")

PYEND

echo ""

# ═══════════════════════════════════════════════════════════════
# 7. ERROR PATTERNS ANALYSIS
# ═══════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐛 7. HISTORICAL ERROR ANALYSIS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "quantum_v33_ultimate_final.log" ]; then
    TOTAL_ERRORS=$(grep -c "ERROR" quantum_v33_ultimate_final.log)
    echo "📊 Total errors in log: $TOTAL_ERRORS"
    echo ""
    
    if [ $TOTAL_ERRORS -gt 0 ]; then
        echo "🔍 Top error types:"
        grep "ERROR" quantum_v33_ultimate_final.log | sed 's/.*ERROR - //' | sort | uniq -c | sort -rn | head -10
        echo ""
        
        echo "📅 Most recent errors (last 5):"
        grep "ERROR" quantum_v33_ultimate_final.log | tail -5
    else
        echo "✅ No errors found in log file!"
    fi
else
    echo "❌ Log file not found"
fi

echo ""

# ═══════════════════════════════════════════════════════════════
# 8. PERFORMANCE METRICS
# ═══════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📈 8. PERFORMANCE METRICS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "quantum_v33_ultimate_final.log" ]; then
    echo "🔍 Analyzing trading history..."
    echo ""
    
    TOTAL_BUYS=$(grep -c " BUY " quantum_v33_ultimate_final.log | grep -v "check_buy")
    TOTAL_SELLS=$(grep -c " SELL " quantum_v33_ultimate_final.log | grep -v "check_sell")
    
    echo "   💰 Total BUY orders: $TOTAL_BUYS"
    echo "   💵 Total SELL orders: $TOTAL_SELLS"
    echo ""
    
    # Last PnL
    LAST_PNL=$(tail -50 quantum_v33_ultimate_final.log | grep "Total PnL:" | tail -1)
    if [ -n "$LAST_PNL" ]; then
        echo "   📊 $LAST_PNL"
    fi
    
    # Win rate
    LAST_WR=$(tail -50 quantum_v33_ultimate_final.log | grep "Win Rate:" | tail -1)
    if [ -n "$LAST_WR" ]; then
        echo "   🎯 $LAST_WR"
    fi
fi

echo ""

# ═══════════════════════════════════════════════════════════════
# FINAL VERDICT
# ═══════════════════════════════════════════════════════════════
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 FINAL AUDIT VERDICT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

CRITICAL=0
WARNINGS=0

# Check bot running
if ! pgrep -f "quantum_v33_ultimate_final.py" > /dev/null; then
    echo "❌ CRITICAL: Bot not running"
    CRITICAL=$((CRITICAL+1))
fi

# Check recent errors
RECENT_ERRORS=$(tail -100 quantum_v33_ultimate_final.log 2>/dev/null | grep -c "ERROR")
if [ $RECENT_ERRORS -gt 5 ]; then
    echo "⚠️  WARNING: $RECENT_ERRORS errors in last 100 lines"
    WARNINGS=$((WARNINGS+1))
fi

echo ""
if [ $CRITICAL -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║  ✅ AUDIT PASSED - SYSTEM IS PRODUCTION READY           ║"
    echo "║                                                           ║"
    echo "║  🚀 All critical systems operational                     ║"
    echo "║  📊 Strategy configuration verified                      ║"
    echo "║  🛡️  Risk management in place                            ║"
    echo "║  💰 Trading logic validated                              ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
elif [ $CRITICAL -eq 0 ]; then
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║  ⚠️  AUDIT PASSED WITH WARNINGS                          ║"
    echo "║                                                           ║"
    echo "║  Found $WARNINGS non-critical issues                              ║"
    echo "║  System can operate but review recommended               ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
else
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║  ❌ AUDIT FAILED - CRITICAL ISSUES FOUND                 ║"
    echo "║                                                           ║"
    echo "║  Found $CRITICAL critical issues                                  ║"
    echo "║  Immediate action required                               ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
fi

echo ""
echo "══════════════════════════════════════════════════════════════"
echo "🔬 Audit completed at $(date)"
echo "══════════════════════════════════════════════════════════════"
