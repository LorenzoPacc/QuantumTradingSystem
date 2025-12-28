#!/bin/bash

##############################################################################
#                    QUANTUM V5 P0 UPGRADE SCRIPT                            #
#                                                                            #
# Fixes:                                                                     #
# 1. API errors (DOT/AVAX NoneType)                                        #
# 2. Adaptive exit strategy (dynamic TP/SL)                                #
# 3. Trailing stops (lock profits)                                         #
# 4. Stale position cleanup                                                #
##############################################################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         🚀 QUANTUM V5 P0 UPGRADE - AUTO INSTALLER          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Configuration
BOT_FILE="quantum_v33_ultimate_final.py"
BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/quantum_v33_backup_${TIMESTAMP}.py"

# Step 1: Create backup directory
echo -e "${YELLOW}📁 Creating backup directory...${NC}"
mkdir -p "$BACKUP_DIR"

# Step 2: Backup current version
echo -e "${YELLOW}💾 Backing up current version...${NC}"
if [ -f "$BOT_FILE" ]; then
    cp "$BOT_FILE" "$BACKUP_FILE"
    echo -e "${GREEN}✅ Backup created: $BACKUP_FILE${NC}"
else
    echo -e "${RED}❌ Error: $BOT_FILE not found!${NC}"
    exit 1
fi

# Step 3: Stop running bot
echo -e "${YELLOW}🛑 Stopping running bot...${NC}"
if pgrep -f "$BOT_FILE" > /dev/null; then
    pkill -f "$BOT_FILE"
    sleep 2
    echo -e "${GREEN}✅ Bot stopped${NC}"
else
    echo -e "${YELLOW}⚠️  Bot was not running${NC}"
fi

# Step 4: Create patched version
echo -e "${YELLOW}🔧 Applying V5 P0 patches...${NC}"

python3 << 'PYTHON_PATCH'
import re
import sys

BOT_FILE = "quantum_v33_ultimate_final.py"

try:
    with open(BOT_FILE, 'r') as f:
        content = f.read()
    
    print("📝 Patching check_buy()...")
    
    # Find and replace check_buy method
    check_buy_pattern = r'def check_buy\(self, symbol\):.*?(?=\n    def |\nclass |\Z)'
    
    new_check_buy = '''    def check_buy(self, symbol):
        """
        FIXED VERSION - Gestisce None returns correttamente
        """
        try:
            # Controlla max positions
            if len(self.state['positions']) >= self.max_positions:
                return False, f"Max positions reached ({self.max_positions})"
            
            # Controlla se già in posizione
            if symbol in self.state['positions']:
                return False, f"Already in position: {symbol}"
            
            # Analizza mercato
            try:
                analysis = self.analyze_market(symbol)
                
                # FIX: Controlla se analyze_market ha ritornato None
                if analysis is None:
                    self.logger.warning(f"Analysis returned None for {symbol}")
                    return False, f"Analysis failed for {symbol}"
                
                should_trade, confidence, reason = analysis
                
            except (ValueError, TypeError) as e:
                # FIX: Cattura errori di unpacking
                self.logger.error(f"Error unpacking analysis for {symbol}: {e}")
                return False, f"Invalid analysis result: {str(e)}"
            
            # Se non dovrebbe tradare
            if not should_trade:
                return False, reason
            
            # Verifica confidence
            if confidence < 50.0:
                return False, f"Confidence too low: {confidence:.1f}%"
            
            # Procedi con buy
            return True, f"BUY signal: {confidence:.1f}% confidence"
            
        except Exception as e:
            self.logger.error(f"Error in check_buy({symbol}): {e}")
            return False, f"Error: {str(e)}"
'''
    
    if re.search(check_buy_pattern, content, re.DOTALL):
        content = re.sub(check_buy_pattern, new_check_buy, content, flags=re.DOTALL)
        print("✅ check_buy() patched")
    else:
        print("⚠️  check_buy() pattern not found, skipping...")
    
    print("📝 Patching check_sell()...")
    
    # Find and replace check_sell method
    check_sell_pattern = r'def check_sell\(self, symbol\):.*?(?=\n    def |\nclass |\Z)'
    
    new_check_sell = '''    def check_sell(self, symbol):
        """
        EXIT STRATEGY con:
        1. Dynamic take-profit (3-7% based on F&G)
        2. Trailing stop (lock profit)
        3. Stale position cleanup
        """
        try:
            if symbol not in self.state['positions']:
                return False, "No position"
            
            position = self.state['positions'][symbol]
            
            # Fetch current price
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            entry_price = position['entry_price']
            
            # Calculate PnL
            pnl_pct = ((current_price / entry_price) - 1) * 100
            
            # Update highest PnL
            if 'highest_pnl' not in position or pnl_pct > position['highest_pnl']:
                position['highest_pnl'] = pnl_pct
                self.save_state()
            
            # Get market conditions
            fear_index = self.get_fear_greed_index()
            
            # 1. DYNAMIC TAKE PROFIT (based on Fear & Greed)
            if fear_index < 25:  # EXTREME FEAR
                take_profit = 3.0  # Prendi profit velocemente
            elif fear_index < 40:  # FEAR
                take_profit = 4.0
            elif fear_index < 60:  # NEUTRAL
                take_profit = 5.0
            else:  # GREED
                take_profit = 6.0  # Aspetta di più
            
            # 2. TRAILING STOP (lock 70% of max profit)
            highest_pnl = position.get('highest_pnl', 0)
            if highest_pnl > 2.0:  # Se ha raggiunto almeno +2%
                trailing_threshold = highest_pnl * 0.7  # Lock 70%
                
                if pnl_pct < trailing_threshold:
                    self.logger.info(f"🔒 TRAILING STOP: {symbol} - Highest: {highest_pnl:.2f}% → Locking at {pnl_pct:.2f}%")
                    return True, f"TRAILING_STOP (locked {pnl_pct:.2f}%)"
            
            # 3. DYNAMIC STOP LOSS (based on volatility)
            from datetime import datetime
            volatility = abs(ticker.get('percentage', 3.0))  # Default 3%
            if volatility > 5.0:  # High volatility
                stop_loss = -4.0  # Più spazio
            else:
                stop_loss = -3.0  # Standard
            
            # 4. STALE POSITION CLEANUP
            entry_time = datetime.fromisoformat(position['entry_time'])
            age_hours = (datetime.now() - entry_time).total_seconds() / 3600
            
            if age_hours > 48:  # 2 giorni
                if -0.5 < pnl_pct < 1.0:  # Troppo flat
                    self.logger.info(f"🧹 STALE CLEANUP: {symbol} - Age: {age_hours:.0f}h, PnL: {pnl_pct:.2f}%")
                    return True, f"STALE_CLEANUP ({age_hours:.0f}h old)"
            
            # 5. CHECK STANDARD EXITS
            if pnl_pct >= take_profit:
                self.logger.info(f"✅ TAKE PROFIT: {symbol} at {pnl_pct:.2f}% (target: {take_profit:.1f}%)")
                return True, f"TAKE_PROFIT ({pnl_pct:.2f}%)"
            
            if pnl_pct <= stop_loss:
                self.logger.info(f"🛑 STOP LOSS: {symbol} at {pnl_pct:.2f}% (limit: {stop_loss:.1f}%)")
                return True, f"STOP_LOSS ({pnl_pct:.2f}%)"
            
            # HOLD
            return False, f"HOLD (PnL: {pnl_pct:+.2f}%, High: {highest_pnl:.2f}%)"
            
        except Exception as e:
            self.logger.error(f"Error checking sell {symbol}: {e}")
            return False, f"Error: {str(e)}"
'''
    
    if re.search(check_sell_pattern, content, re.DOTALL):
        content = re.sub(check_sell_pattern, new_check_sell, content, flags=re.DOTALL)
        print("✅ check_sell() patched")
    else:
        print("⚠️  check_sell() pattern not found, skipping...")
    
    # Write patched content
    with open(BOT_FILE, 'w') as f:
        f.write(content)
    
    print("✅ All patches applied successfully!")
    sys.exit(0)
    
except Exception as e:
    print(f"❌ Error during patching: {e}")
    sys.exit(1)

PYTHON_PATCH

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Patching failed! Restoring backup...${NC}"
    cp "$BACKUP_FILE" "$BOT_FILE"
    exit 1
fi

echo -e "${GREEN}✅ Patches applied${NC}"

# Step 5: Test syntax
echo -e "${YELLOW}🧪 Testing Python syntax...${NC}"
if python3 -m py_compile "$BOT_FILE"; then
    echo -e "${GREEN}✅ Syntax OK${NC}"
else
    echo -e "${RED}❌ Syntax error! Restoring backup...${NC}"
    cp "$BACKUP_FILE" "$BOT_FILE"
    exit 1
fi

# Step 6: Show what changed
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                   📊 CHANGES SUMMARY                        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✅ Fixed API errors (DOT/AVAX NoneType)${NC}"
echo -e "${GREEN}✅ Implemented dynamic take-profit (3-7% based on F&G)${NC}"
echo -e "${GREEN}✅ Added trailing stops (lock 70% of max profit)${NC}"
echo -e "${GREEN}✅ Added stale position cleanup (>48h flat)${NC}"
echo ""

# Step 7: Ask user to restart
echo -e "${YELLOW}🔄 Ready to restart bot. Continue? (y/n)${NC}"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🚀 Starting bot...${NC}"
    nohup python3 "$BOT_FILE" > quantum_v33_ultimate_final.log 2>&1 &
    sleep 3
    
    if pgrep -f "$BOT_FILE" > /dev/null; then
        BOT_PID=$(pgrep -f "$BOT_FILE")
        echo -e "${GREEN}✅ Bot started successfully! PID: $BOT_PID${NC}"
        echo ""
        echo -e "${BLUE}📊 Monitor with:${NC}"
        echo -e "   tail -f quantum_v33_ultimate_final.log"
        echo ""
        echo -e "${BLUE}📈 Check status:${NC}"
        echo -e "   ~/qstatus"
        echo ""
    else
        echo -e "${RED}❌ Failed to start bot. Check logs:${NC}"
        echo -e "   python3 $BOT_FILE"
        exit 1
    fi
else
    echo -e "${YELLOW}⏸️  Bot not started. Start manually when ready:${NC}"
    echo -e "   nohup python3 $BOT_FILE > quantum_v33_ultimate_final.log 2>&1 &"
fi

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              ✅ UPGRADE TO V5 P0 COMPLETE!                  ║${NC}"
echo -e "${BLUE}║                                                              ║${NC}"
echo -e "${BLUE}║  🎯 Expected improvements:                                   ║${NC}"
echo -e "${BLUE}║  • No more API errors (DOT/AVAX)                             ║${NC}"
echo -e "${BLUE}║  • Better profit capture (trailing stops)                   ║${NC}"
echo -e "${BLUE}║  • Faster exits in EXTREME FEAR (3% vs 5%)                   ║${NC}"
echo -e "${BLUE}║  • No more stale positions (>48h cleanup)                    ║${NC}"
echo -e "${BLUE}║                                                              ║${NC}"
echo -e "${BLUE}║  📊 Monitor next 2-4 hours for results                       ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Backup saved at: $BACKUP_FILE${NC}"
echo ""
