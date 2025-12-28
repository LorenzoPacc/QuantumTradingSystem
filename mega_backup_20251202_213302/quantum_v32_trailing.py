#!/usr/bin/env python3
"""
🚀 QUANTUM TRADING SYSTEM V3.2 - WITH TRAILING STOP
All V3.1 features + Trailing Stop Loss
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
from functools import wraps

# ============================================
# CONFIGURATION
# ============================================

LOCK_FILE = '/tmp/quantum_v32.lock'
PORTFOLIO_FILE = 'portfolio_v32.json'
LOG_FILE = 'quantum_v32.log'

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
            logger.error(f"❌ QUANTUM V3.2 already running! PID: {old_pid}")
            sys.exit(1)
        except (OSError, ValueError):
            os.remove(LOCK_FILE)
    
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))
    
    logger.info(f"🔒 Lock acquired: PID {os.getpid()}")
    atexit.register(lambda: os.remove(LOCK_FILE) if os.path.exists(LOCK_FILE) else None)

def retry_on_error(max_retries=3, delay=2):
    """Decorator for automatic retry on network errors"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (ccxt.NetworkError, ccxt.ExchangeError, requests.RequestException) as e:
                    if attempt == max_retries - 1:
                        logger.error(f"❌ {func.__name__} failed after {max_retries} attempts: {e}")
                        return None
                    wait_time = delay * (attempt + 1)
                    logger.warning(f"⚠️ {func.__name__} failed (attempt {attempt+1}/{max_retries}), retry in {wait_time}s")
                    time.sleep(wait_time)
            return None
        return wrapper
    return decorator

# ============================================
# QUANTUM TRADING V3.2 CLASS
# ============================================

class QuantumTradingV32:
    
    def __init__(self, dry_run=True):
        """Initialize Quantum Trading System V3.2"""
        
        check_lock()
        
        # SYSTEM CONFIG
        self.dry_run = dry_run
        self.capital_initial = 200.0
        self.cash = 200.0
        self.portfolio = {}
        self.trade_history = []
        self.cycle_count = 0
        
        # EXCHANGE
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'},
            'timeout': 30000
        })
        
        # TRADING PARAMETERS
        self.max_positions = 4
        self.position_size_base = 0.20
        
        # RSI PARAMETERS
        self.RSI_PERIOD = 14
        self.RSI_OVERSOLD = 30
        self.RSI_OVERBOUGHT = 70
        self.RSI_EXTREME_LOW = 20
        self.RSI_EXTREME_HIGH = 80
        
        # FEAR & GREED ZONES
        self.FG_EXTREME_FEAR = 25
        self.FG_FEAR = 45
        self.FG_GREED = 55
        self.FG_EXTREME_GREED = 75
        
        # PROFIT TARGETS
        self.TAKE_PROFIT_MIN = 0.03
        self.TAKE_PROFIT_TARGET = 0.05
        self.STOP_LOSS = -0.05
        
        # 🆕 TRAILING STOP
        self.TRAILING_STOP_PCT = 0.03      # 3% trailing
        self.TRAILING_ACTIVATION = 0.02    # Attiva sopra +2%
        
        # SYMBOLS
        self.symbols = ['BTC/USDT', 'ETH/USDT', 'AVAX/USDT', 'DOT/USDT']
        
        # Load portfolio
        if not self.load_portfolio():
            logger.info("📦 Starting with fresh portfolio")
        
        logger.info("="*70)
        logger.info("🚀 QUANTUM TRADING V3.2 INITIALIZED (WITH TRAILING STOP)")
        logger.info(f"   Mode: {'🧪 DRY-RUN' if dry_run else '💰 LIVE TRADING'}")
        logger.info(f"   Capital: ${self.capital_initial:.2f}")
        logger.info(f"   Trailing Stop: {self.TRAILING_STOP_PCT*100}% (activates at +{self.TRAILING_ACTIVATION*100}%)")
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
            
            for symbol, pos in self.portfolio.items():
                data['portfolio'][symbol] = {
                    'entry_price': pos['entry_price'],
                    'amount': pos['amount'],
                    'entry_time': pos['entry_time'].isoformat(),
                    'signal_strength': pos['signal_strength'],
                    'highest_price': pos.get('highest_price', pos['entry_price'])
                }
            
            with open(PORTFOLIO_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"💾 Portfolio saved")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save portfolio: {e}")
            return False
    
    def load_portfolio(self):
        """Load portfolio from disk"""
        if not os.path.exists(PORTFOLIO_FILE):
            return False
        
        try:
            with open(PORTFOLIO_FILE, 'r') as f:
                data = json.load(f)
            
            self.cash = data['cash']
            self.capital_initial = data['capital_initial']
            self.cycle_count = data.get('cycle_count', 0)
            
            for symbol, pos in data['portfolio'].items():
                self.portfolio[symbol] = {
                    'entry_price': pos['entry_price'],
                    'amount': pos['amount'],
                    'entry_time': datetime.fromisoformat(pos['entry_time']),
                    'signal_strength': pos['signal_strength'],
                    'highest_price': pos.get('highest_price', pos['entry_price'])
                }
            
            logger.info(f"✅ Portfolio loaded: {len(self.portfolio)} positions, ${self.cash:.2f} cash")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load portfolio: {e}")
            return False
    
    # ============================================
    # LAYER 1: MARKET SENTIMENT
    # ============================================
    
    @retry_on_error(max_retries=5, delay=1)
    def get_fear_greed_index(self):
        """Fetch Fear & Greed Index with retry"""
        response = requests.get('https://api.alternative.me/fng/?limit=1', timeout=10)
        data = response.json()
        value = int(data['data'][0]['value'])
        return value
    
    def get_market_regime(self, fear_greed):
        """Determine market regime"""
        if fear_greed < self.FG_EXTREME_FEAR:
            return "EXTREME_FEAR"
        elif fear_greed < self.FG_FEAR:
            return "FEAR"
        elif fear_greed < self.FG_GREED:
            return "NEUTRAL"
        elif fear_greed < self.FG_EXTREME_GREED:
            return "GREED"
        else:
            return "EXTREME_GREED"
    
    # ============================================
    # LAYER 2: TECHNICAL ANALYSIS
    # ============================================
    
    @retry_on_error(max_retries=3, delay=2)
    def calculate_rsi(self, symbol, timeframe='15m', limit=100):
        """Calculate RSI"""
        ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        closes = [x[4] for x in ohlcv]
        
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-self.RSI_PERIOD:])
        avg_loss = np.mean(losses[-self.RSI_PERIOD:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def get_rsi_signal(self, rsi):
        """Classify RSI signal"""
        if rsi < self.RSI_EXTREME_LOW:
            return "STRONG_BUY"
        elif rsi < self.RSI_OVERSOLD:
            return "BUY"
        elif rsi > self.RSI_EXTREME_HIGH:
            return "STRONG_SELL"
        elif rsi > self.RSI_OVERBOUGHT:
            return "SELL"
        else:
            return "NEUTRAL"
    
    @retry_on_error(max_retries=3, delay=2)
    def get_current_price(self, symbol):
        """Get current price"""
        ticker = self.exchange.fetch_ticker(symbol)
        return ticker['last']
    
    # ============================================
    # LAYER 3: DECISION MATRIX
    # ============================================
    
    def should_buy(self, symbol, rsi, fear_greed, current_price):
        """Multi-layer BUY decision"""
        
        if symbol in self.portfolio:
            return False, 0, "Already in position"
        
        if len(self.portfolio) >= self.max_positions:
            return False, 0, "Max positions reached"
        
        if self.cash < 15:
            return False, 0, "Insufficient cash"
        
        market_regime = self.get_market_regime(fear_greed)
        rsi_signal = self.get_rsi_signal(rsi)
        
        # DECISION MATRIX
        if market_regime == "EXTREME_FEAR" and rsi_signal == "STRONG_BUY":
            return True, 1.0, f"🔥 MAX OPPORTUNITY: {market_regime} + RSI<20"
        
        if market_regime in ["EXTREME_FEAR", "FEAR"] and rsi_signal in ["STRONG_BUY", "BUY"]:
            strength = 0.9 if rsi_signal == "STRONG_BUY" else 0.8
            return True, strength, f"✅ GOOD: {market_regime} + {rsi_signal}"
        
        if market_regime == "NEUTRAL" and rsi_signal == "STRONG_BUY":
            return True, 0.6, f"⚖️ MODERATE: NEUTRAL + RSI<20"
        
        if market_regime in ["GREED", "EXTREME_GREED"] and rsi_signal == "STRONG_BUY":
            return True, 0.4, f"⚠️ CONTRARIAN: {market_regime} but RSI<20"
        
        return False, 0, f"❌ NO BUY: {market_regime} + RSI:{rsi:.1f}"
    
    def should_sell(self, symbol, rsi, fear_greed, entry_price, current_price):
        """Multi-layer SELL decision with TRAILING STOP"""
        
        if symbol not in self.portfolio:
            return False, 0, "Not in position"
        
        profit_pct = (current_price - entry_price) / entry_price
        market_regime = self.get_market_regime(fear_greed)
        rsi_signal = self.get_rsi_signal(rsi)
        
        # 🆕 UPDATE HIGHEST PRICE
        if current_price > self.portfolio[symbol]['highest_price']:
            self.portfolio[symbol]['highest_price'] = current_price
            self.save_portfolio()
            logger.debug(f"📈 {symbol} new peak: ${current_price:.2f}")
        
        highest = self.portfolio[symbol]['highest_price']
        trailing_stop_price = highest * (1 - self.TRAILING_STOP_PCT)
        
        # 🆕 TRAILING STOP (if activated and in profit)
        if profit_pct >= self.TRAILING_ACTIVATION:
            if current_price <= trailing_stop_price:
                profit_from_peak = ((current_price - highest) / highest) * 100
                return True, 1.0, f"📉 TRAILING STOP: Peak ${highest:.2f} → ${current_price:.2f} ({profit_from_peak:.2f}% from peak, +{profit_pct*100:.2f}% total)"
        
        # STOP LOSS (fixed)
        if profit_pct <= self.STOP_LOSS:
            return True, 1.0, f"🛑 STOP LOSS: {profit_pct*100:.2f}%"
        
        # TAKE PROFIT scenarios
        if (market_regime == "EXTREME_GREED" and 
            rsi_signal in ["STRONG_SELL", "SELL"] and 
            profit_pct >= self.TAKE_PROFIT_MIN):
            return True, 1.0, f"🎯 PERFECT EXIT: {market_regime} + RSI>70 + {profit_pct*100:.2f}%"
        
        if profit_pct >= self.TAKE_PROFIT_TARGET:
            return True, 0.9, f"💰 TARGET: {profit_pct*100:.2f}%"
        
        if (market_regime in ["GREED", "EXTREME_GREED"] and 
            rsi_signal == "STRONG_SELL" and 
            profit_pct >= self.TAKE_PROFIT_MIN):
            return True, 0.8, f"⚠️ {market_regime} + RSI>80: {profit_pct*100:.2f}%"
        
        if rsi_signal in ["STRONG_SELL", "SELL"] and profit_pct >= self.TAKE_PROFIT_MIN:
            return True, 0.7, f"📊 RSI OVERBOUGHT: {profit_pct*100:.2f}%"
        
        if market_regime in ["FEAR", "EXTREME_FEAR"] and rsi_signal == "STRONG_SELL":
            return True, 0.5, f"⚡ ANOMALY: {market_regime} but RSI>80"
        
        # HOLD
        trailing_info = f" | Trail: ${trailing_stop_price:.2f}" if profit_pct >= self.TRAILING_ACTIVATION else ""
        return False, 0, f"✋ HOLD: {market_regime} + RSI:{rsi:.1f} + {profit_pct*100:.2f}%{trailing_info}"
    
    # ============================================
    # LAYER 4: POSITION SIZING
    # ============================================
    
    def calculate_position_size(self, signal_strength):
        """Calculate position size"""
        base_size = self.cash * self.position_size_base
        
        if signal_strength >= 0.9:
            multiplier = 1.5
        elif signal_strength >= 0.7:
            multiplier = 1.2
        elif signal_strength >= 0.5:
            multiplier = 1.0
        else:
            multiplier = 0.7
        
        size = base_size * multiplier
        max_size = self.cash * 0.3
        
        return min(size, max_size, self.cash)
    
    # ============================================
    # EXECUTION
    # ============================================
    
    def execute_buy(self, symbol, price, position_size, signal_strength):
        """Execute BUY"""
        if self.dry_run:
            self.portfolio[symbol] = {
                'entry_price': price,
                'amount': position_size,
                'entry_time': datetime.now(),
                'signal_strength': signal_strength,
                'highest_price': price  # 🆕 Track peak
            }
            self.cash -= position_size
            self.save_portfolio()
            logger.info(f"[DRY-RUN] 🟢 BUY {symbol}: ${position_size:.2f} @ ${price:.2f} | Strength: {signal_strength*100:.0f}%")
    
    def execute_sell(self, symbol, price, signal_strength):
        """Execute SELL"""
        if symbol not in self.portfolio:
            return
        
        position = self.portfolio[symbol]
        entry_price = position['entry_price']
        amount = position['amount']
        profit_pct = ((price - entry_price) / entry_price) * 100
        
        if self.dry_run:
            self.cash += amount * (price / entry_price)
            del self.portfolio[symbol]
            self.save_portfolio()
            logger.info(f"[DRY-RUN] 🔴 SELL {symbol}: ${amount:.2f} → ${amount * (price/entry_price):.2f} | {profit_pct:+.2f}%")
    
    # ============================================
    # MAIN CYCLE
    # ============================================
    
    def run_cycle(self):
        """Execute trading cycle"""
        self.cycle_count += 1
        
        logger.info("\n" + "="*70)
        logger.info(f"🎯 CYCLE {self.cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*70)
        
        fear_greed = self.get_fear_greed_index()
        if fear_greed is None:
            fear_greed = 50
        
        market_regime = self.get_market_regime(fear_greed)
        logger.info(f"📊 Fear & Greed: {fear_greed} ({market_regime})")
        logger.info("")
        
        for symbol in self.symbols:
            try:
                logger.info(f"🔍 Analyzing {symbol}...")
                
                rsi = self.calculate_rsi(symbol)
                price = self.get_current_price(symbol)
                
                if rsi is None or price is None:
                    logger.warning(f"   ⚠️ Failed to fetch data, skipping")
                    continue
                
                logger.info(f"   RSI: {rsi:.1f} | Price: ${price:.2f}")
                
                # SELL check
                if symbol in self.portfolio:
                    entry_price = self.portfolio[symbol]['entry_price']
                    should_sell, strength, reason = self.should_sell(
                        symbol, rsi, fear_greed, entry_price, price
                    )
                    
                    if should_sell:
                        logger.info(f"   🔴 {reason}")
                        self.execute_sell(symbol, price, strength)
                    else:
                        logger.info(f"   {reason}")
                
                # BUY check
                else:
                    should_buy, strength, reason = self.should_buy(
                        symbol, rsi, fear_greed, price
                    )
                    
                    if should_buy:
                        position_size = self.calculate_position_size(strength)
                        logger.info(f"   🟢 {reason}")
                        logger.info(f"      Size: ${position_size:.2f} | Strength: {strength*100:.0f}%")
                        self.execute_buy(symbol, price, position_size, strength)
                    else:
                        logger.info(f"   {reason}")
                
                logger.info("")
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Error: {e}")
                continue
        
        self.print_portfolio_summary()
        logger.info(f"⏳ Next cycle in 10 minutes...")
        logger.info("="*70 + "\n")
    
    def print_portfolio_summary(self):
        """Print portfolio"""
        logger.info("\n💰 PORTFOLIO STATUS:")
        logger.info(f"   Cash: ${self.cash:.2f}")
        
        total_value = self.cash
        
        for symbol, pos in self.portfolio.items():
            try:
                current_price = self.get_current_price(symbol)
                if current_price:
                    current_value = pos['amount'] * (current_price / pos['entry_price'])
                    profit_pct = ((current_price - pos['entry_price']) / pos['entry_price']) * 100
                    total_value += current_value
                    
                    status = "🟢" if profit_pct > 0 else "🔴"
                    
                    # 🆕 Show trailing stop info
                    highest = pos.get('highest_price', pos['entry_price'])
                    trailing_price = highest * (1 - self.TRAILING_STOP_PCT)
                    trailing_info = f" | Trail@${trailing_price:.2f}" if profit_pct >= self.TRAILING_ACTIVATION*100 else ""
                    
                    logger.info(f"   {status} {symbol}: ${current_value:.2f} ({profit_pct:+.2f}%){trailing_info}")
            except:
                pass
        
        total_pnl = ((total_value - self.capital_initial) / self.capital_initial) * 100
        logger.info(f"💎 TOTAL: ${total_value:.2f} ({total_pnl:+.2f}%)")
    
    def run(self, cycle_interval=600):
        """Main loop"""
        logger.info("🚀 Starting Quantum V3.2...")
        
        try:
            while True:
                self.run_cycle()
                time.sleep(cycle_interval)
        except KeyboardInterrupt:
            logger.info("\n⚠️ Shutdown requested...")
            self.save_portfolio()
            self.print_portfolio_summary()
            logger.info("✅ Quantum V3.2 stopped")

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    bot = QuantumTradingV32(dry_run=True)
    bot.run(cycle_interval=600)

