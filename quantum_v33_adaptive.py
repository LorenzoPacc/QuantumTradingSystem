#!/usr/bin/env python3
"""
🚀 QUANTUM TRADING SYSTEM V3.3 - ADAPTIVE MARKET LOGIC
All V3.2 features + Adaptive Fear/Greed Strategy
Compra in EXTREME FEAR quando RSI oversold - FA CASSA!
"""

import ccxt
import pandas as pd
import numpy as np
from datetime import datetime
import time
import requests
import logging
import sys
import json
import os
import atexit

# ============================================
# CONFIGURATION
# ============================================

LOCK_FILE = '/tmp/quantum_v33.lock'
PORTFOLIO_FILE = 'portfolio_v33.json'
LOG_FILE = 'quantum_v33.log'

# ============================================
# LOGGING SETUP
# ============================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================
# UTILITIES
# ============================================

def check_lock():
    """Prevent multiple instances"""
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, 'r') as f:
                old_pid = int(f.read().strip())
            os.kill(old_pid, 0)
            logger.error(f"❌ QUANTUM V3.3 already running! PID: {old_pid}")
            sys.exit(1)
        except OSError:
            pass
    
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))

def cleanup_lock():
    """Remove lock file on exit"""
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

atexit.register(cleanup_lock)

# ============================================
# QUANTUM TRADER V3.3 - ADAPTIVE
# ============================================

class QuantumTraderV33:
    """Adaptive trading system - Compra ai minimi, vende sui massimi"""
    
    def __init__(self, initial_capital=200, dry_run=True):
        self.capital_initial = initial_capital
        self.cash = initial_capital
        self.portfolio = {}
        self.cycle_count = 0
        self.dry_run = dry_run
        
        # RSI PARAMETERS
        self.RSI_PERIOD = 14
        self.RSI_OVERSOLD = 30
        self.RSI_OVERBOUGHT = 70
        self.RSI_EXTREME_LOW = 25      # Super oversold - BUY AGGRESSIVO
        self.RSI_EXTREME_HIGH = 75
        
        # 🆕 FEAR & GREED ADAPTIVE ZONES
        self.FG_PANIC = 10                # < 10 = Panico totale (aspetta)
        self.FG_EXTREME_FEAR = 25         # 10-25 = OPPORTUNITÀ! 🔥
        self.FG_FEAR = 45                 # 25-45 = Normale
        self.FG_NEUTRAL = 55              # 45-55 = Equilibrio
        self.FG_GREED = 70                # 55-70 = Rialzista
        self.FG_EXTREME_GREED = 75        # > 75 = SOLO VENDI!
        
        # PROFIT TARGETS - ADAPTIVE
        self.TAKE_PROFIT_MIN = 0.03       # +3% minimo
        self.TAKE_PROFIT_FEAR = 0.08      # +8% se comprato in FEAR
        self.TAKE_PROFIT_NORMAL = 0.05    # +5% normale
        self.STOP_LOSS = -0.05            # -5%
        
        # TRAILING STOP
        self.TRAILING_STOP_PCT = 0.03     # 3% trailing
        self.TRAILING_ACTIVATION = 0.02   # Attiva sopra +2%
        
        # 🆕 POSITION SIZING ADAPTIVE
        self.POSITION_BASE = 0.20         # 20% base
        self.POSITION_FEAR_BOOST = 1.5    # 1.5x in EXTREME FEAR
        self.POSITION_GREED_REDUCE = 0.5  # 0.5x in GREED
        
        # SYMBOLS
        self.symbols = ['BTC/USDT', 'ETH/USDT', 'AVAX/USDT', 'DOT/USDT']
        
        # Exchange
        self.exchange = ccxt.binance({'enableRateLimit': True})
        
        # Load portfolio
        if not self.load_portfolio():
            logger.info("📦 Starting with fresh portfolio")
        
        logger.info("="*70)
        logger.info("🚀 QUANTUM TRADING V3.3 INITIALIZED (ADAPTIVE)")
        logger.info(f"   Mode: {'🧪 DRY-RUN' if dry_run else '💰 LIVE TRADING'}")
        logger.info(f"   Capital: ${self.capital_initial:.2f}")
        logger.info(f"   🆕 ADAPTIVE: Compra in EXTREME FEAR quando RSI oversold")
        logger.info(f"   🆕 POSITION SIZING: 1.5x in Fear, 0.5x in Greed")
        logger.info("="*70)
    
    # ============================================
    # PERSISTENCE
    # ============================================
    
    def save_portfolio(self):
        """Save portfolio to disk"""
        try:
            data = {
                'cash': self.cash,
                'portfolio': {},
                'capital_initial': self.capital_initial,
                'cycle_count': self.cycle_count,
                'timestamp': datetime.now().isoformat()
            }
            
            for symbol, position in self.portfolio.items():
                data['portfolio'][symbol] = {
                    'amount': position['amount'],
                    'entry_price': position['entry_price'],
                    'entry_fear': position.get('entry_fear', 50),
                    'highest_price': position.get('highest_price', position['entry_price']),
                    'timestamp': position.get('timestamp', datetime.now().isoformat())
                }
            
            with open(PORTFOLIO_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving portfolio: {e}")
    
    def load_portfolio(self):
        """Load portfolio from disk"""
        try:
            if not os.path.exists(PORTFOLIO_FILE):
                return False
            
            with open(PORTFOLIO_FILE, 'r') as f:
                data = json.load(f)
            
            self.cash = data.get('cash', self.capital_initial)
            self.cycle_count = data.get('cycle_count', 0)
            
            for symbol, pos in data.get('portfolio', {}).items():
                self.portfolio[symbol] = {
                    'amount': pos['amount'],
                    'entry_price': pos['entry_price'],
                    'entry_fear': pos.get('entry_fear', 50),
                    'highest_price': pos.get('highest_price', pos['entry_price']),
                    'timestamp': pos.get('timestamp', datetime.now().isoformat())
                }
            
            logger.info(f"📂 Portfolio loaded: {len(self.portfolio)} positions")
            return True
        except Exception as e:
            logger.error(f"Error loading portfolio: {e}")
            return False
    
    # ============================================
    # MARKET DATA
    # ============================================
    
    def get_fear_greed_index(self):
        """Get Fear & Greed Index"""
        try:
            response = requests.get("https://api.alternative.me/fng/?limit=1", timeout=5)
            if response.status_code == 200:
                return int(response.json()['data'][0]['value'])
        except Exception as e:
            logger.warning(f"Failed to get Fear & Greed: {e}")
            return 50
        return 50
    
    def get_ticker(self, symbol):
        """Get current price"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return None
    
    def calculate_rsi(self, symbol, period=14):
        """Calculate RSI"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1h', limit=period+1)
            closes = [x[4] for x in ohlcv]
            
            deltas = np.diff(closes)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gain = np.mean(gains[-period:])
            avg_loss = np.mean(losses[-period:])
            
            if avg_loss == 0:
                return 100
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception as e:
            logger.error(f"Error calculating RSI for {symbol}: {e}")
            return 50
    
    # ============================================
    # 🆕 ADAPTIVE TRADING LOGIC
    # ============================================
    
    def calculate_position_size(self, fear_index, rsi):
        """🆕 ADAPTIVE POSITION SIZING"""
        base_size = self.cash * self.POSITION_BASE
        
        # EXTREME FEAR + OVERSOLD = AGGRESSIVO! 🔥
        if fear_index < self.FG_EXTREME_FEAR and rsi < self.RSI_EXTREME_LOW:
            size = base_size * self.POSITION_FEAR_BOOST
            logger.info(f"   🔥 AGGRESSIVE SIZE: {self.POSITION_FEAR_BOOST}x (Fear={fear_index}, RSI={rsi:.1f})")
            return size
        
        # EXTREME FEAR + OVERSOLD normale
        elif fear_index < self.FG_EXTREME_FEAR and rsi < self.RSI_OVERSOLD:
            size = base_size * 1.2
            logger.info(f"   📈 INCREASED SIZE: 1.2x (Fear={fear_index}, RSI={rsi:.1f})")
            return size
        
        # GREED = CAUTO
        elif fear_index > self.FG_GREED:
            size = base_size * self.POSITION_GREED_REDUCE
            logger.info(f"   ⚠️ REDUCED SIZE: {self.POSITION_GREED_REDUCE}x (Fear={fear_index})")
            return size
        
        return base_size
    
    def should_buy(self, symbol, fear_index, rsi, price):
        """🆕 ADAPTIVE BUY LOGIC"""
        
        # EXTREME GREED: MAI COMPRARE! 🚫
        if fear_index >= self.FG_EXTREME_GREED:
            logger.info(f"   ❌ NO BUY: EXTREME_GREED (Fear={fear_index})")
            return False
        
        # PANIC TOTALE: Aspetta stabilità
        if fear_index < self.FG_PANIC:
            logger.info(f"   ❌ NO BUY: PANIC (Fear={fear_index})")
            return False
        
        # 🔥 EXTREME FEAR (10-25): OPPORTUNITÀ!
        if fear_index < self.FG_EXTREME_FEAR:
            if rsi < self.RSI_EXTREME_LOW:
                logger.info(f"   🔥 BUY OPPORTUNITY! EXTREME_FEAR + SUPER_OVERSOLD (Fear={fear_index}, RSI={rsi:.1f})")
                return True
            elif rsi < self.RSI_OVERSOLD:
                logger.info(f"   ✅ BUY: EXTREME_FEAR + OVERSOLD (Fear={fear_index}, RSI={rsi:.1f})")
                return True
            else:
                logger.info(f"   ⏳ WAIT: EXTREME_FEAR but RSI={rsi:.1f} not oversold yet")
                return False
        
        # FEAR normale (25-45): Compra solo se oversold
        elif fear_index < self.FG_FEAR:
            if rsi < self.RSI_OVERSOLD:
                logger.info(f"   ✅ BUY: FEAR + OVERSOLD (Fear={fear_index}, RSI={rsi:.1f})")
                return True
            else:
                return False
        
        # NEUTRAL/GREED: Molto cauto
        elif fear_index < self.FG_GREED:
            if rsi < self.RSI_EXTREME_LOW:
                logger.info(f"   ✅ BUY: NEUTRAL but SUPER_OVERSOLD (RSI={rsi:.1f})")
                return True
            else:
                return False
        
        # GREED alto: Solo su dip estremo
        else:
            if rsi < self.RSI_EXTREME_LOW:
                logger.info(f"   ⚠️ BUY CAUTO: GREED but extreme dip (RSI={rsi:.1f})")
                return True
            else:
                return False
    
    def should_sell(self, symbol, position, current_price, fear_index, rsi):
        """🆕 ADAPTIVE SELL LOGIC"""
        entry_price = position['entry_price']
        entry_fear = position.get('entry_fear', 50)
        highest_price = position.get('highest_price', entry_price)
        
        # Aggiorna highest price
        if current_price > highest_price:
            position['highest_price'] = current_price
            highest_price = current_price
        
        profit_pct = (current_price - entry_price) / entry_price
        
        # TRAILING STOP (sempre attivo se profit > 2%)
        if profit_pct > self.TRAILING_ACTIVATION:
            trailing_stop = highest_price * (1 - self.TRAILING_STOP_PCT)
            if current_price <= trailing_stop:
                logger.info(f"   🎯 SELL: Trailing Stop hit (profit was {profit_pct*100:.2f}%)")
                return True, "TRAILING_STOP"
        
        # STOP LOSS
        if profit_pct <= self.STOP_LOSS:
            logger.info(f"   🛑 SELL: Stop Loss ({profit_pct*100:.2f}%)")
            return True, "STOP_LOSS"
        
        # RSI OVERBOUGHT
        if rsi >= self.RSI_EXTREME_HIGH:
            logger.info(f"   📈 SELL: RSI Extreme Overbought ({rsi:.1f})")
            return True, "RSI_OVERBOUGHT"
        
        # 🆕 EXTREME GREED: Vendi se in profit
        if fear_index >= self.FG_EXTREME_GREED and profit_pct > 0.03:
            logger.info(f"   ⚠️ SELL: EXTREME_GREED + profit {profit_pct*100:.2f}%")
            return True, "EXTREME_GREED"
        
        # 🆕 ADAPTIVE TAKE PROFIT (basato su entry_fear)
        if entry_fear < self.FG_EXTREME_FEAR:
            # Comprato in EXTREME FEAR: aspetta più gain!
            if profit_pct >= self.TAKE_PROFIT_FEAR:
                logger.info(f"   💰 SELL: Take Profit {profit_pct*100:.2f}% (bought in FEAR)")
                return True, "TAKE_PROFIT_FEAR"
        else:
            # Comprato in condizioni normali
            if profit_pct >= self.TAKE_PROFIT_NORMAL:
                logger.info(f"   💰 SELL: Take Profit {profit_pct*100:.2f}%")
                return True, "TAKE_PROFIT"
        
        return False, None
    
    # ============================================
    # TRADING EXECUTION
    # ============================================
    
    def buy(self, symbol, price, amount, fear_index):
        """Execute BUY"""
        cost = price * amount
        
        if self.dry_run:
            logger.info(f"   [DRY-RUN] 🟢 BUY {symbol}: ${cost:.2f} @ ${price:.2f} (Fear={fear_index})")
        else:
            logger.info(f"   💰 BUY {symbol}: ${cost:.2f} @ ${price:.2f} (Fear={fear_index})")
        
        self.cash -= cost
        self.portfolio[symbol] = {
            'amount': amount,
            'entry_price': price,
            'entry_fear': fear_index,
            'highest_price': price,
            'timestamp': datetime.now().isoformat()
        }
        
        self.save_portfolio()
    
    def sell(self, symbol, price, reason):
        """Execute SELL"""
        position = self.portfolio[symbol]
        amount = position['amount']
        value = price * amount
        profit = value - (position['entry_price'] * amount)
        profit_pct = (price - position['entry_price']) / position['entry_price']
        
        if self.dry_run:
            logger.info(f"   [DRY-RUN] 🔴 SELL {symbol}: ${value:.2f} | Profit: {profit_pct*100:.2f}% | Reason: {reason}")
        else:
            logger.info(f"   💸 SELL {symbol}: ${value:.2f} | Profit: {profit_pct*100:.2f}% | Reason: {reason}")
        
        self.cash += value
        del self.portfolio[symbol]
        
        self.save_portfolio()
    
    # ============================================
    # MAIN CYCLE
    # ============================================
    
    def run_cycle(self):
        """Execute one trading cycle"""
        self.cycle_count += 1
        
        logger.info("")
        logger.info("="*70)
        logger.info(f"🎯 CYCLE {self.cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*70)
        
        # Get market sentiment
        fear_index = self.get_fear_greed_index()
        
        if fear_index < self.FG_PANIC:
            sentiment = "PANIC"
        elif fear_index < self.FG_EXTREME_FEAR:
            sentiment = "EXTREME_FEAR 🔥"
        elif fear_index < self.FG_FEAR:
            sentiment = "FEAR"
        elif fear_index < self.FG_NEUTRAL:
            sentiment = "NEUTRAL"
        elif fear_index < self.FG_GREED:
            sentiment = "GREED"
        elif fear_index < self.FG_EXTREME_GREED:
            sentiment = "HIGH_GREED"
        else:
            sentiment = "EXTREME_GREED ⚠️"
        
        logger.info(f"📊 Fear & Greed: {fear_index} ({sentiment})")
        logger.info("")
        
        # Check SELL signals first
        for symbol in list(self.portfolio.keys()):
            logger.info(f"🔍 Checking SELL for {symbol}...")
            
            price = self.get_ticker(symbol)
            if not price:
                continue
            
            rsi = self.calculate_rsi(symbol)
            
            should_sell, reason = self.should_sell(
                symbol, self.portfolio[symbol], price, fear_index, rsi
            )
            
            if should_sell:
                self.sell(symbol, price, reason)
        
        logger.info("")
        
        # Check BUY signals
        available_cash = self.cash
        max_positions = 4
        current_positions = len(self.portfolio)
        
        if current_positions >= max_positions:
            logger.info(f"⏸️  Max positions reached ({current_positions}/{max_positions})")
        else:
            for symbol in self.symbols:
                if symbol in self.portfolio:
                    continue
                
                if available_cash < 15:
                    logger.info(f"⏸️  Insufficient cash (${available_cash:.2f})")
                    break
                
                logger.info(f"🔍 Analyzing {symbol}...")
                
                price = self.get_ticker(symbol)
                if not price:
                    continue
                
                rsi = self.calculate_rsi(symbol)
                logger.info(f"   RSI: {rsi:.1f} | Price: ${price:.2f}")
                
                if self.should_buy(symbol, fear_index, rsi, price):
                    position_size = self.calculate_position_size(fear_index, rsi)
                    
                    if position_size > available_cash:
                        position_size = available_cash * 0.9
                    
                    if position_size >= 15:
                        amount = position_size / price
                        self.buy(symbol, price, amount, fear_index)
                        available_cash = self.cash
                        
                        if len(self.portfolio) >= max_positions:
                            break
                
                logger.info("")
                time.sleep(1)
        
        # Portfolio summary
        logger.info("")
        logger.info("💰 PORTFOLIO STATUS:")
        logger.info(f"   Cash: ${self.cash:.2f}")
        
        total_value = self.cash
        
        for symbol, position in self.portfolio.items():
            current_price = self.get_ticker(symbol)
            if current_price:
                value = position['amount'] * current_price
                total_value += value
                profit_pct = (current_price - position['entry_price']) / position['entry_price']
                emoji = "🟢" if profit_pct > 0 else "🔴"
                
                logger.info(f"   {emoji} {symbol}: ${value:.2f} ({profit_pct:+.2f}%)")
                time.sleep(0.5)
        
        performance = (total_value - self.capital_initial) / self.capital_initial
        logger.info(f"💎 TOTAL: ${total_value:.2f} ({performance:+.2f}%)")
        logger.info(f"⏳ Next cycle in 10 minutes...")
        logger.info("="*70)
        
        self.save_portfolio()

# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    check_lock()
    
    trader = QuantumTraderV33(initial_capital=200, dry_run=True)
    
    logger.info("")
    logger.info("🔄 Starting trading loop...")
    logger.info("")
    
    while True:
        try:
            trader.run_cycle()
            time.sleep(600)  # 10 minutes
        except KeyboardInterrupt:
            logger.info("")
            logger.info("🛑 Shutting down gracefully...")
            cleanup_lock()
            break
        except Exception as e:
            logger.error(f"❌ Error in cycle: {e}")
            time.sleep(60)
