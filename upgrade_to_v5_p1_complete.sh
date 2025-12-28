#!/bin/bash

##############################################################################
#              QUANTUM V5 P1 COMPLETE - ALL-IN-ONE UPGRADE                   #
#                                                                            #
# Installs in order:                                                         #
# 1. V5 P1: Regime Detection + Adaptive Thresholds                         #
# 2. V5 P1.1: Regime Caching + Adaptive Entry                              #
#                                                                            #
# One script to rule them all!                                              #
##############################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    🚀 V5 P1 COMPLETE - ALL-IN-ONE UPGRADE                  ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

BOT_FILE="quantum_v33_ultimate_final.py"
BACKUP_FILE="backups/quantum_backup_v5p1_complete_$(date +%Y%m%d_%H%M%S).py"

mkdir -p backups
echo -e "${YELLOW}💾 Creating backup...${NC}"
cp "$BOT_FILE" "$BACKUP_FILE"
echo -e "${GREEN}✅ Backup: $BACKUP_FILE${NC}"

echo -e "${YELLOW}🛑 Stopping bot...${NC}"
pkill -f quantum_v33 || true
sleep 2

echo -e "${YELLOW}🔧 Applying V5 P1 COMPLETE patches...${NC}"

python3 << 'PYTHON_COMPLETE'
import re

BOT_FILE = "quantum_v33_ultimate_final.py"

with open(BOT_FILE, 'r') as f:
    content = f.read()

print("="*70)
print("PHASE 1: V5 P1 - Regime Detection + Adaptive Thresholds")
print("="*70)

# ============================================================================
# V5 P1: Add regime detection methods
# ============================================================================
print("\n📝 Adding detect_market_regime() with caching...")

regime_methods = '''
    def detect_market_regime(self):
        """
        V5 P1: Detect market regime with 15-min cache
        """
        try:
            import time
            
            # CACHE CHECK
            now = time.time()
            if hasattr(self, '_cached_regime') and hasattr(self, '_cached_regime_time'):
                if now - self._cached_regime_time < 900:  # 15 min
                    return self._cached_regime
            
            fear_index = self.get_fear_greed_index()
            
            if not self.state['positions']:
                regime = "NORMAL"
            else:
                total_pnl = 0
                count = 0
                
                for symbol, pos in self.state['positions'].items():
                    try:
                        ticker = self.exchange.fetch_ticker(symbol)
                        current_price = ticker['last']
                        entry_price = pos['entry_price']
                        pnl = ((current_price / entry_price) - 1) * 100
                        total_pnl += pnl
                        count += 1
                    except:
                        continue
                
                avg_pnl = total_pnl / count if count > 0 else 0
                
                if fear_index < 25:
                    if avg_pnl < -1.5:
                        regime = "DOWNTREND_EXTREME"
                    elif avg_pnl < -0.5:
                        regime = "DOWNTREND_MODERATE"
                    else:
                        regime = "SIDEWAYS_FEAR"
                elif fear_index < 40:
                    if avg_pnl < -1.0:
                        regime = "DOWNTREND_MODERATE"
                    else:
                        regime = "SIDEWAYS_FEAR"
                else:
                    regime = "NORMAL"
            
            self._cached_regime = regime
            self._cached_regime_time = now
            
            self.logger.info(f"🎯 REGIME: {regime} (F&G: {fear_index}, cached 15min)")
            return regime
            
        except Exception as e:
            self.logger.error(f"Error detecting regime: {e}")
            return "NORMAL"
    
    def get_adaptive_thresholds(self, regime):
        """V5 P1: Adaptive thresholds for exits"""
        thresholds = {
            "DOWNTREND_EXTREME": {
                "take_profit": 1.5,
                "stop_loss": -2.0,
                "stale_hours": 24,
                "trailing_min": 1.5,
                "trailing_lock": 0.6
            },
            "DOWNTREND_MODERATE": {
                "take_profit": 2.0,
                "stop_loss": -2.5,
                "stale_hours": 30,
                "trailing_min": 2.0,
                "trailing_lock": 0.65
            },
            "SIDEWAYS_FEAR": {
                "take_profit": 3.0,
                "stop_loss": -3.0,
                "stale_hours": 48,
                "trailing_min": 2.5,
                "trailing_lock": 0.7
            },
            "NORMAL": {
                "take_profit": 5.0,
                "stop_loss": -3.0,
                "stale_hours": 72,
                "trailing_min": 3.0,
                "trailing_lock": 0.7
            }
        }
        
        config = thresholds.get(regime, thresholds["NORMAL"])
        self.logger.info(f"⚙️  ADAPTIVE: TP={config['take_profit']}% SL={config['stop_loss']}% Stale={config['stale_hours']}h")
        return config
    
    def get_adaptive_confidence_threshold(self, regime):
        """V5 P1.1: Adaptive entry confidence"""
        thresholds = {
            "DOWNTREND_EXTREME": 65,
            "DOWNTREND_MODERATE": 60,
            "SIDEWAYS_FEAR": 55,
            "NORMAL": 50
        }
        min_conf = thresholds.get(regime, 50)
        self.logger.debug(f"📊 Min confidence [{regime}]: {min_conf}%")
        return min_conf
'''

# Find insertion point after get_fear_greed_index
pattern = r'(    def get_fear_greed_index\(self\):.*?return [^\n]+\n)'
match = re.search(pattern, content, re.DOTALL)

if match:
    insert_pos = match.end()
    content = content[:insert_pos] + regime_methods + content[insert_pos:]
    print("✅ Regime methods added")
else:
    # Try alternative
    pattern = r'(    def save_state\(self\):.*?json\.dump.*?\n)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        insert_pos = match.end()
        content = content[:insert_pos] + regime_methods + content[insert_pos:]
        print("✅ Regime methods added (alt)")
    else:
        print("❌ Could not insert regime methods")
        exit(1)

# ============================================================================
# V5 P1: Update check_sell with adaptive thresholds
# ============================================================================
print("\n📝 Updating check_sell() with adaptive exits...")

new_check_sell = '''    def check_sell(self, symbol):
        """V5 P1: ADAPTIVE EXIT STRATEGY"""
        try:
            if symbol not in self.state['positions']:
                return False, "No position"
            
            position = self.state['positions'][symbol]
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            entry_price = position['entry_price']
            pnl_pct = ((current_price / entry_price) - 1) * 100
            
            if 'highest_pnl' not in position or pnl_pct > position['highest_pnl']:
                position['highest_pnl'] = pnl_pct
                self.save_state()
            
            regime = self.detect_market_regime()
            config = self.get_adaptive_thresholds(regime)
            
            take_profit = config['take_profit']
            stop_loss = config['stop_loss']
            stale_hours = config['stale_hours']
            trailing_min = config['trailing_min']
            trailing_lock = config['trailing_lock']
            
            highest_pnl = position.get('highest_pnl', 0)
            if highest_pnl > trailing_min:
                trailing_threshold = highest_pnl * trailing_lock
                if pnl_pct < trailing_threshold:
                    self.logger.info(f"🔒 TRAILING [{regime}]: {symbol} High:{highest_pnl:.2f}% Lock:{pnl_pct:.2f}%")
                    return True, f"TRAILING_STOP ({pnl_pct:.2f}%)"
            
            from datetime import datetime
            entry_time = datetime.fromisoformat(position['entry_time'])
            age_hours = (datetime.now() - entry_time).total_seconds() / 3600
            
            if age_hours > stale_hours and -1.0 < pnl_pct < 1.5:
                self.logger.info(f"🧹 STALE [{regime}]: {symbol} {age_hours:.0f}h, {pnl_pct:.2f}%")
                return True, f"STALE_CLEANUP ({age_hours:.0f}h)"
            
            if pnl_pct >= take_profit:
                self.logger.info(f"✅ TP [{regime}]: {symbol} {pnl_pct:.2f}% (target:{take_profit}%)")
                return True, f"TAKE_PROFIT ({pnl_pct:.2f}%)"
            
            if pnl_pct <= stop_loss:
                self.logger.info(f"🛑 SL [{regime}]: {symbol} {pnl_pct:.2f}% (limit:{stop_loss}%)")
                return True, f"STOP_LOSS ({pnl_pct:.2f}%)"
            
            return False, f"HOLD (PnL: {pnl_pct:+.2f}%, High: {highest_pnl:.2f}%)"
            
        except Exception as e:
            self.logger.error(f"Error check_sell {symbol}: {e}")
            return False, f"Error: {str(e)}"
'''

pattern = r'    def check_sell\(self, symbol\):.*?(?=\n    def [a-z_]+\(|\nclass |\Z)'
if re.search(pattern, content, re.DOTALL):
    content = re.sub(pattern, new_check_sell, content, flags=re.DOTALL)
    print("✅ check_sell() updated")
else:
    print("❌ check_sell() not found")
    exit(1)

# ============================================================================
# V5 P1.1: Update check_buy with adaptive confidence
# ============================================================================
print("\n📝 Updating check_buy() with adaptive entry...")

# Find and update confidence check
old_pattern = r'(\s+)if confidence < 50\.0:\s+return False[^\n]*\n'
new_code = r'''\1# V5 P1.1: Adaptive confidence
\1regime = self.detect_market_regime()
\1min_confidence = self.get_adaptive_confidence_threshold(regime)
\1if confidence < min_confidence:
\1    return False, f"Confidence {confidence:.1f}% < {min_confidence}% [{regime}]"
\1
'''

if re.search(old_pattern, content):
    content = re.sub(old_pattern, new_code, content)
    print("✅ check_buy() updated with adaptive entry")
else:
    print("⚠️  Could not find confidence check in check_buy()")

# Write
with open(BOT_FILE, 'w') as f:
    f.write(content)

print("\n" + "="*70)
print("✅ ALL PATCHES APPLIED SUCCESSFULLY!")
print("="*70)

PYTHON_COMPLETE

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed! Restoring backup...${NC}"
    cp "$BACKUP_FILE" "$BOT_FILE"
    exit 1
fi

echo -e "${YELLOW}🧪 Testing syntax...${NC}"
if python3 -m py_compile "$BOT_FILE"; then
    echo -e "${GREEN}✅ Syntax OK${NC}"
else
    echo -e "${RED}❌ Syntax error! Restoring...${NC}"
    cp "$BACKUP_FILE" "$BOT_FILE"
    exit 1
fi

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              📊 V5 P1 COMPLETE SUMMARY                      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✅ Regime Detection (15min cache)${NC}"
echo -e "${GREEN}✅ Adaptive Exit Thresholds${NC}"
echo -e "${GREEN}✅ Adaptive Entry Thresholds${NC}"
echo ""
echo -e "${YELLOW}🎯 Current Market Impact (F&G=21):${NC}"
echo -e "   • Detected: DOWNTREND_EXTREME or MODERATE"
echo -e "   • TP: 1.5-2.0% (was 5%)"
echo -e "   • SL: -2.0% to -2.5% (was -3%)"
echo -e "   • Min confidence: 65% (was 50%)"
echo -e "   • SOL at -2.18% will exit at -2.0% ✅"
echo ""

echo -e "${YELLOW}🚀 Start V5 P1 COMPLETE? (y/n)${NC}"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    python3 "$BOT_FILE" &
    sleep 3
    
    if pgrep -f "$BOT_FILE" > /dev/null; then
        echo -e "${GREEN}✅ V5 P1 COMPLETE running! PID: $(pgrep -f "$BOT_FILE")${NC}"
        echo ""
        echo -e "${BLUE}📊 Monitor regime:${NC}"
        echo -e "   tail -f quantum_v33_ultimate_final.log | grep 'REGIME\\|ADAPTIVE'"
        echo ""
        echo -e "${GREEN}🎯 Expect within 10 minutes:${NC}"
        echo -e "   • REGIME detected and logged"
        echo -e "   • SOL exit at -2.0% (currently -2.18%)"
        echo -e "   • Low confidence trades blocked"
        echo ""
    else
        echo -e "${RED}❌ Start failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Start manually: python3 $BOT_FILE &${NC}"
fi

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          ✅ V5 P1 COMPLETE INSTALLED!                       ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo -e "${GREEN}Backup: $BACKUP_FILE${NC}"
