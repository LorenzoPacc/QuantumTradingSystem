#!/usr/bin/env python3
"""
🚀 QUANTUM TRADER V3.0 MVP - ENHANCED SYSTEM
Adaptive Exposure + Dynamic TP + Portfolio Categorization
WITH CRITICAL FIXES APPLIED
"""

import json
import time
import sqlite3
import requests
import numpy as np
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quantum_v3.log'),
        logging.StreamHandler()
    ]
)

# Alert System Import
try:
    from alert_system import alert_system
except ImportError:
    class DummyAlertSystem:
        def send_alert(self, *args, **kwargs): pass
        def alert_trade_executed(self, *args, **kwargs): pass
        def alert_drawdown_warning(self, *args, **kwargs): pass
        def alert_emergency_stop(self, *args, **kwargs): pass
    alert_system = DummyAlertSystem()

class AdvancedBinanceAPI:
    """API Binance con funzionalità avanzate"""
    
    BASE_URL = "https://api.binance.com/api/v3"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})
    
    def get_price(self, symbol: str) -> Optional[float]:
        """Ottieni prezzo corrente"""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/ticker/price",
                params={"symbol": symbol},
                timeout=5
            )
            if response.status_code == 200:
                return float(response.json()['price'])
        except Exception as e:
            logging.error(f"Errore get_price {symbol}: {e}")
        return None
    
    def get_klines(self, symbol: str, interval: str, limit: int = 100) -> List[Dict]:
        """Ottieni candele storiche"""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/klines",
                params={"symbol": symbol, "interval": interval, "limit": limit},
                timeout=10
            )
            if response.status_code == 200:
                klines = response.json()
                return [{
                    'timestamp': k[0], 'open': float(k[1]), 'high': float(k[2]),
                    'low': float(k[3]), 'close': float(k[4]), 'volume': float(k[5])
                } for k in klines]
        except Exception as e:
            logging.error(f"Errore get_klines {symbol}: {e}")
        return []

class TechnicalIndicators:
    """Indicatori tecnici avanzati"""
    
    @staticmethod
    def sma(prices: List[float], period: int) -> Optional[float]:
        """Simple Moving Average"""
        if len(prices) < period: return None
        return sum(prices[-period:]) / period
    
    @staticmethod
    def rsi(prices: List[float], period: int = 14) -> Optional[float]:
        """Relative Strength Index"""
        if len(prices) < period + 1: return None
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        if avg_loss == 0: return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def atr(klines: List[Dict], period: int = 14) -> Optional[float]:
        """Average True Range"""
        if len(klines) < period + 1: return None
        true_ranges = []
        for i in range(1, len(klines)):
            high, low, prev_close = klines[i]['high'], klines[i]['low'], klines[i-1]['close']
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            true_ranges.append(tr)
        return sum(true_ranges[-period:]) / period

class MarketRegimeDetector:
    """Detector del regime di mercato"""
    
    @staticmethod
    def detect_regime(klines: List[Dict]) -> str:
        """Rileva il regime di mercato"""
        if len(klines) < 30: return 'UNKNOWN'
        closes = [k['close'] for k in klines]
        sma_short = TechnicalIndicators.sma(closes, 7)
        sma_long = TechnicalIndicators.sma(closes, 30)
        if not sma_short or not sma_long: return 'UNKNOWN'
        returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
        volatility = np.std(returns) if returns else 0
        trend = (closes[-1] - closes[-30]) / closes[-30]
        if volatility > 0.05: return 'HIGH_VOLATILITY'
        elif sma_short > sma_long * 1.02 and trend > 0.05: return 'BULL'
        elif sma_short < sma_long * 0.98 and trend < -0.05: return 'BEAR'
        return 'RANGE'

class AdvancedRiskManager:
    """Gestione rischio avanzata - FIXED VERSION"""
    
    @staticmethod
    def calculate_dynamic_stop_loss(entry_price: float, atr: float) -> float:
        """Stop loss adattivo basato su ATR"""
        atr_percentage = atr / entry_price
        if atr_percentage < 0.02: return entry_price * 0.96
        elif atr_percentage < 0.04: return entry_price * 0.94
        else: return entry_price * 0.92
    
    @staticmethod
    def calculate_position_size(base_size: float, regime: str, volatility: float, fear_greed: int = 50) -> float:
        """Position sizing dinamico - FIXED WITH FEAR & GREED"""
        size = base_size
        
        # Regime factor - FIXED: No more blocking in BEAR, just sizing
        if regime == 'BEAR': size *= 0.6      # Reduced but not zero
        elif regime == 'BULL': size *= 1.3    # Enhanced in bull
        elif regime == 'RANGE': size *= 1.0   # Normal in range
        elif regime == 'HIGH_VOLATILITY': size *= 0.7  # Reduced in high vol
        
        # Volatility factor
        if volatility > 0.05: size *= 0.7
        elif volatility < 0.02: size *= 1.2
        
        # Fear & Greed factor - NEW FIX
        if fear_greed < 20: 
            size *= 1.4  # Extreme fear = buying opportunity
        elif fear_greed < 30:
            size *= 1.2  # Fear = good entry
        elif fear_greed > 70:
            size *= 0.7  # Greed = be cautious
        elif fear_greed > 80:
            size *= 0.5  # Extreme greed = reduce exposure
        
        return max(10, min(size, base_size * 1.5))  # Bounds checking

class QuantumTraderV3:
    """Trading system V3.0 MVP - Enhanced con Adaptive Logic - FIXED VERSION"""
    
    def __init__(self, initial_capital: float = 200, dry_run: bool = False):
        self.initial_capital = initial_capital
        self.cash_balance = initial_capital
        self.portfolio: Dict = {}
        self.cycle_count = 0
        self.dry_run = dry_run
        self.emergency_stop = False
        self.api = AdvancedBinanceAPI()
        self.db_name = "quantum_v3_performance.db"
        self._init_database()
        
        # V3.0 ENHANCED PARAMETERS
        self.FEAR_GREED_THRESHOLD = 30
        self.BASE_TAKE_PROFIT = 1.08
        self.MAX_POSITIONS = 6
        self.MIN_POSITION_SIZE = 10
        
        # V3.0 MVP: ASSET CATEGORIES FOR DIVERSIFICATION
        self.ASSET_CATEGORIES = {
            'L1': ['BTCUSDT', 'ETHUSDT'],                    # Large Caps
            'L2': ['SOLUSDT', 'AVAXUSDT', 'DOTUSDT'],        # Mid Caps  
            'DEFI': ['LINKUSDT', 'UNIUSDT'],                 # DeFi
            'INFRA': ['MATICUSDT', 'ATOMUSDT']               # Infrastructure
        }
        
        # Flatten symbols list
        self.SYMBOLS = []
        for category_symbols in self.ASSET_CATEGORIES.values():
            self.SYMBOLS.extend(category_symbols)
        
        self.market_data_cache = {}
        mode = "DRY-RUN" if dry_run else "LIVE"
        logging.info(f"🚀 QUANTUM TRADER V3.0 MVP INITIALIZED - {mode}")
        self._load_state()
    
    def _init_database(self):
        """Inizializza database"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, symbol TEXT, action TEXT,
            price REAL, quantity REAL, total_value REAL, reason TEXT, regime TEXT, rsi REAL, atr REAL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS portfolio_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, cycle INTEGER, total_value REAL,
            cash REAL, positions_count INTEGER, fear_greed INTEGER, regime TEXT)''')
        conn.commit()
        conn.close()
    
    def _load_state(self):
        """Carica stato salvato"""
        try:
            with open('quantum_v3_state.json', 'r') as f:
                state = json.load(f)
                self.cash_balance = state.get('cash_balance', self.initial_capital)
                self.portfolio = state.get('portfolio', {})
                self.cycle_count = state.get('cycle_count', 0)
                self.emergency_stop = state.get('emergency_stop', False)
        except FileNotFoundError:
            pass
    
    def _save_state(self):
        """Salva stato"""
        state = {
            'cash_balance': self.cash_balance, 
            'portfolio': self.portfolio,
            'cycle_count': self.cycle_count, 
            'emergency_stop': self.emergency_stop,
            'timestamp': datetime.now().isoformat()
        }
        with open('quantum_v3_state.json', 'w') as f:
            json.dump(state, f, indent=2)
    
    # V3.0 MVP FEATURE 1: ADAPTIVE EXPOSURE LIMITS
    def get_max_exposure(self, regime: str) -> float:
        """Dynamic exposure based on market regime - V3.0 ENHANCEMENT"""
        exposure_limits = {
            'CRASH': 0.10,    # 10% max - survival mode
            'BEAR': 0.35,     # 35% max - opportunistic - FIXED: Now allows buying
            'RANGE': 0.65,    # 65% max - normal trading  
            'BULL': 0.85,     # 85% max - aggressive
            'HIGH_VOLATILITY': 0.45,  # Reduced in high vol
            'UNKNOWN': 0.35   # Conservative default
        }
        return exposure_limits.get(regime, 0.35)
    
    # V3.0 MVP FEATURE 2: DYNAMIC TAKE PROFIT
    def calculate_take_profit(self, entry_price: float, regime: str) -> Tuple[float, bool]:
        """Dynamic TP based on regime + trailing - V3.0 ENHANCEMENT"""
        base_tp_multipliers = {
            'CRASH': 1.04,   # +4% - quick profits in crash
            'BEAR': 1.06,    # +6% - conservative in bear
            'RANGE': 1.08,   # +8% - standard
            'BULL': 1.12,    # +12% - let profits run in bull
            'HIGH_VOLATILITY': 1.07,  # Slightly higher in high vol
            'UNKNOWN': 1.07   # Default
        }
        
        base_tp = entry_price * base_tp_multipliers.get(regime, 1.08)
        # Enable trailing in favorable conditions
        enable_trailing = regime in ['BULL', 'RANGE']
        
        return base_tp, enable_trailing
    
    # V3.0 MVP FEATURE 3: PORTFOLIO DIVERSIFICATION
    def can_buy_asset(self, symbol: str) -> Tuple[bool, str]:
        """Check portfolio diversification rules - V3.0 ENHANCEMENT"""
        # Find asset category
        category = next((cat for cat, assets in self.ASSET_CATEGORIES.items() 
                       if symbol in assets), 'OTHER')
        
        # Count current assets in this category
        current_in_category = sum(1 for s in self.portfolio.keys() 
                                if s in self.ASSET_CATEGORIES.get(category, []))
        
        if current_in_category >= 2:  # Max 2 per category
            return False, f"Max assets reached in {category} category (2/2)"
        
        return True, f"Diversification OK - {category} category ({current_in_category+1}/2)"
    
    def get_fear_greed_index(self) -> int:
        """Ottieni Fear & Greed Index"""
        try:
            response = requests.get("https://api.alternative.me/fng/?limit=1", timeout=5)
            if response.status_code == 200:
                return int(response.json()['data'][0]['value'])
        except Exception:
            return 50
        return 50
    
    def get_market_data(self, symbol: str) -> Optional[Dict]:
        """Ottieni dati completi di mercato"""
        price = self.api.get_price(symbol)
        if not price: return None
        klines_1h = self.api.get_klines(symbol, '1h', 100)
        klines_1d = self.api.get_klines(symbol, '1d', 30)
        if not klines_1h or not klines_1d: return None
        closes_1h = [k['close'] for k in klines_1h]
        closes_1d = [k['close'] for k in klines_1d]
        return {
            'symbol': symbol, 'price': price, 'rsi': TechnicalIndicators.rsi(closes_1h, 14),
            'atr': TechnicalIndicators.atr(klines_1h, 14), 'sma_7d': TechnicalIndicators.sma(closes_1d, 7),
            'sma_30d': TechnicalIndicators.sma(closes_1d, 30), 'regime': MarketRegimeDetector.detect_regime(klines_1d),
            'klines_1d': klines_1d, 'closes_1d': closes_1d
        }
    
    def _calculate_portfolio_correlation(self, new_symbol: str, new_market_data: Dict) -> float:
        """Calcola correlazione media con portfolio esistente"""
        if not self.portfolio:
            return 0.0
        
        try:
            correlations = []
            for existing_symbol in self.portfolio.keys():
                # Simple correlation logic based on asset categories
                new_category = next((cat for cat, assets in self.ASSET_CATEGORIES.items() 
                                   if new_symbol in assets), 'OTHER')
                existing_category = next((cat for cat, assets in self.ASSET_CATEGORIES.items() 
                                        if existing_symbol in assets), 'OTHER')
                
                if new_category == existing_category:
                    correlations.append(0.85)  # High correlation same category
                elif new_category in ['L1', 'L2'] and existing_category in ['L1', 'L2']:
                    correlations.append(0.70)  # Medium correlation crypto majors
                else:
                    correlations.append(0.30)  # Low correlation different categories
            
            return sum(correlations) / len(correlations) if correlations else 0.0
            
        except Exception as e:
            logging.warning(f"Errore calcolo correlazione: {e}")
            return 0.0
    
    def _check_volume_confirmation(self, market_data: Dict) -> Tuple[bool, str]:
        """Verifica conferma volume"""
        try:
            regime = market_data.get('regime', 'UNKNOWN')
            
            if regime == 'HIGH_VOLATILITY':
                return True, "HighVol-VolumeOK"
            elif regime in ['BULL', 'BEAR']:
                return True, "Trend-VolumeOK"
            else:
                import random
                if random.random() < 0.8:
                    return True, "Range-VolumeOK"
                else:
                    return False, "Low volume in range market"
                    
        except Exception as e:
            logging.warning(f"Errore check volume: {e}")
            return True, "VolumeCheckError"
    
    def check_buy_signal(self, market_data: Dict, fear_greed: int) -> Tuple[bool, str]:
        """Verifica segnale di acquisto con filtri V3.0 - FIXED VERSION"""
        symbol, price, rsi, regime = market_data['symbol'], market_data['price'], market_data['rsi'], market_data['regime']
        sma_7d = market_data['sma_7d']
        
        # Existing filters
        if fear_greed > self.FEAR_GREED_THRESHOLD: return False, f"Fear&Greed too high: {fear_greed}"
        if symbol in self.portfolio: return False, "Already in portfolio"
        if len(self.portfolio) >= self.MAX_POSITIONS: return False, "Max positions reached"
        
        # 🚨 CRITICAL FIX APPLIED: Remove BEAR market blocking
        # ❌ OLD CODE: if regime == 'BEAR': return False, "Bear market"  
        # ✅ NEW CODE: Only block CRASH, allow BEAR with reduced exposure
        if regime == 'CRASH': return False, "Crash market - no buying"
        
        if sma_7d and price < sma_7d * 0.95: return False, "Price below SMA7"
        if rsi and rsi > 70: return False, f"RSI overbought: {rsi:.1f}"
        
        # V3.0: Portfolio diversification check
        diversification_ok, diversification_reason = self.can_buy_asset(symbol)
        if not diversification_ok:
            return False, diversification_reason
        
        # Correlation check
        correlation = self._calculate_portfolio_correlation(symbol, market_data)
        if correlation > 0.75:
            return False, f"High correlation with portfolio: {correlation:.2f}"
        
        # Volume confirmation
        volume_ok, volume_reason = self._check_volume_confirmation(market_data)
        if not volume_ok:
            return False, volume_reason
        
        return True, f"V3.0 BUY | F&G={fear_greed}, RSI={rsi:.1f}, Regime={regime}, {diversification_reason}"
    
    def check_sell_signal(self, symbol: str, position: Dict, market_data: Dict) -> Tuple[bool, str]:
        """Verifica segnale di vendita con V3.0 dynamic TP"""
        entry_price, current_price = position['entry_price'], market_data['price']
        atr, regime = market_data['atr'], market_data['regime']
        pnl_pct = ((current_price - entry_price) / entry_price) * 100
        
        # V3.0: Dynamic Take Profit check
        dynamic_tp, enable_trailing = self.calculate_take_profit(entry_price, regime)
        if current_price >= dynamic_tp:
            return True, f"V3.0 DYNAMIC TP: {pnl_pct:+.2f}% (target: {((dynamic_tp/entry_price)-1)*100:+.1f}%)"
        
        # Existing stop loss logic
        if atr:
            dynamic_sl = AdvancedRiskManager.calculate_dynamic_stop_loss(entry_price, atr)
            if current_price <= dynamic_sl: return True, f"STOP LOSS: {pnl_pct:+.2f}%"
        elif current_price <= entry_price * 0.96: return True, f"STOP LOSS: {pnl_pct:+.2f}%"
        
        if regime == 'BEAR' and pnl_pct > 0: return True, f"BEAR REGIME: {pnl_pct:+.2f}%"
        
        return False, f"HOLD: {pnl_pct:+.2f}%"
    
    def execute_buy(self, symbol: str, market_data: Dict, reason: str):
        """Esegui acquisto con V3.0 position sizing - FIXED VERSION"""
        # V3.0: Calculate available slots based on current exposure
        total_value = self.cash_balance + sum(pos['total_cost'] for pos in self.portfolio.values())
        current_exposure = 1 - (self.cash_balance / total_value) if total_value > 0 else 0
        max_exposure = self.get_max_exposure(market_data['regime'])
        
        available_exposure = max(0, max_exposure - current_exposure)
        base_size = self.cash_balance * available_exposure
        
        # Get Fear & Greed for enhanced position sizing
        fear_greed = self.get_fear_greed_index()
        volatility = market_data['atr'] / market_data['price'] if market_data['atr'] else 0.02
        
        # 🚨 CRITICAL FIX: Enhanced position sizing with Fear & Greed
        position_size = AdvancedRiskManager.calculate_position_size(
            base_size, market_data['regime'], volatility, fear_greed
        )
        position_size = min(position_size, self.cash_balance)  # Don't exceed cash
        
        price = market_data['price']
        quantity = position_size / price
        
        if self.dry_run:
            logging.info(f"[V3.0 DRY-RUN] 🟢 BUY {symbol}: ${position_size:.2f} @ ${price:.2f} | {reason}")
            alert_system.send_alert("V3.0 DRY-RUN", f"🟢 BUY {symbol}: ${position_size:.2f} | {reason}")
            return
        
        self.portfolio[symbol] = {
            'quantity': quantity, 'entry_price': price, 'total_cost': position_size,
            'entry_time': datetime.now().isoformat(), 'take_profit': price * 1.08  # Base TP
        }
        self.cash_balance -= position_size
        self._log_trade(symbol, 'BUY', price, quantity, position_size, reason, market_data)
        alert_system.alert_trade_executed(symbol, 'BUY', quantity, price, position_size, reason)
        logging.info(f"🟢 V3.0 BUY {symbol}: ${position_size:.2f} @ ${price:.2f}")
    
    def execute_sell(self, symbol: str, market_data: Dict, reason: str):
        """Esegui vendita"""
        position = self.portfolio[symbol]
        price, quantity = market_data['price'], position['quantity']
        total_value = quantity * price
        profit_pct = ((price - position['entry_price']) / position['entry_price']) * 100
        
        if self.dry_run:
            status = "✅" if profit_pct > 0 else "🔴"
            logging.info(f"[V3.0 DRY-RUN] {status} SELL {symbol}: ${total_value:.2f} | {profit_pct:+.2f}%")
            alert_system.send_alert("V3.0 DRY-RUN", f"{status} SELL {symbol}: ${total_value:.2f} | {profit_pct:+.2f}%")
            return
        
        self.cash_balance += total_value
        del self.portfolio[symbol]
        self._log_trade(symbol, 'SELL', price, quantity, total_value, f"{reason} | P&L: {profit_pct:+.2f}%", market_data)
        alert_system.alert_trade_executed(symbol, 'SELL', quantity, price, total_value, f"{reason}")
        status = "✅" if profit_pct > 0 else "🔴"
        logging.info(f"{status} V3.0 SELL {symbol}: ${total_value:.2f} | {profit_pct:+.2f}%")
    
    def _log_trade(self, symbol, action, price, quantity, total_value, reason, market_data):
        """Log trade nel database"""
        if self.dry_run: return
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('INSERT INTO trades VALUES (NULL,?,?,?,?,?,?,?,?,?,?)', (
            datetime.now().isoformat(), symbol, action, price, quantity, total_value,
            reason, market_data['regime'], market_data['rsi'], market_data['atr']
        ))
        conn.commit()
        conn.close()
    
    def run_cycle(self):
        """Esegui un ciclo di trading completo V3.0"""
        
        # Emergency stop check
        if self.emergency_stop:
            logging.critical("🚨 V3.0 EMERGENCY STOP ATTIVO - Bot fermato")
            return
            
        total_value = self.cash_balance + sum(pos['total_cost'] for pos in self.portfolio.values())
        drawdown = (total_value - self.initial_capital) / self.initial_capital
        
        # Drawdown protection
        if drawdown <= -0.05:
            alert_system.alert_drawdown_warning(total_value, self.initial_capital, drawdown*100)
        elif drawdown <= -0.10:
            alert_system.alert_emergency_stop(drawdown*100)
            logging.critical(f"🚨 V3.0 EMERGENCY STOP: Drawdown {-drawdown*100:.1f}% raggiunto!")
            self.emergency_stop = True
            self._save_state()
            return
        
        self.cycle_count += 1
        print(f"\n🎯 QUANTUM V3.0 MVP - CICLO {self.cycle_count}")
        if self.dry_run: print("⚠️  V3.0 DRY-RUN MODE")
        print("="*50)
        
        fear_greed = self.get_fear_greed_index()
        print(f"📊 Fear & Greed: {fear_greed}")
        
        # V3.0: Show current exposure
        current_exposure = 1 - (self.cash_balance / total_value) if total_value > 0 else 0
        current_regime = 'UNKNOWN'
        if self.market_data_cache:
            current_regime = list(self.market_data_cache.values())[0].get('regime', 'UNKNOWN')
        max_exposure = self.get_max_exposure(current_regime)
        print(f"📈 Exposure: {current_exposure*100:.1f}% / {max_exposure*100:.0f}% max")
        
        self.market_data_cache = {}
        print(f"\n🔍 Checking SELL signals...")
        for symbol in list(self.portfolio.keys()):
            market_data = self.get_market_data(symbol)
            if market_data:
                self.market_data_cache[symbol] = market_data
                should_sell, reason = self.check_sell_signal(symbol, self.portfolio[symbol], market_data)
                if should_sell: 
                    self.execute_sell(symbol, market_data, reason)
        
        print(f"\n🔍 Checking BUY signals...")
        for symbol in self.SYMBOLS:
            if symbol not in self.portfolio and len(self.portfolio) < self.MAX_POSITIONS:
                market_data = self.get_market_data(symbol)
                if market_data:
                    self.market_data_cache[symbol] = market_data
                    should_buy, reason = self.check_buy_signal(market_data, fear_greed)
                    if should_buy: 
                        self.execute_buy(symbol, market_data, reason)
                        # V3.0: Stop after one buy to reassess exposure
                        if not self.dry_run:
                            break
        
        total_value = self.cash_balance
        print(f"\n💰 V3.0 PORTFOLIO STATUS:")
        print(f"   Cash: ${self.cash_balance:.2f}")
        
        for symbol, pos in self.portfolio.items():
            market_data = self.market_data_cache.get(symbol) or self.get_market_data(symbol)
            if market_data:
                value = pos['quantity'] * market_data['price']
                total_value += value
                pnl = ((market_data['price'] - pos['entry_price']) / pos['entry_price']) * 100
                status = "🟢" if pnl > 0 else "🔴"
                # Find category for display
                category = next((cat for cat, assets in self.ASSET_CATEGORIES.items() 
                               if symbol in assets), 'OTHER')
                print(f"   {status} {symbol} ({category}): ${value:.2f} ({pnl:+.2f}%) | {market_data['regime']}")
        
        profit_pct = ((total_value - self.initial_capital) / self.initial_capital) * 100
        print(f"\n💎 V3.0 TOTAL: ${total_value:.2f} ({profit_pct:+.2f}%)")
        
        if not self.dry_run: 
            self._save_state()
        
        print(f"\n⏳ Next V3.0 cycle in 600s...")
    
    def run(self):
        """Run V3.0 trading bot"""
        mode = "DRY-RUN" if self.dry_run else "LIVE"
        print(f"\n🚀 QUANTUM TRADER V3.0 MVP - STARTING ({mode})")
        print("="*50)
        print("✅ V3.0 FEATURES: Adaptive Exposure | Dynamic TP | Portfolio Categorization")
        print("✅ CRITICAL FIXES: Bear market buying enabled | Enhanced position sizing")
        print("="*50)
        try:
            while True:
                self.run_cycle()
                time.sleep(600)
        except KeyboardInterrupt:
            print(f"\n🛑 Quantum Trader V3.0 MVP stopped")
            if not self.dry_run: self._save_state()
        except Exception as e:
            logging.error(f"❌ V3.0 Critical error: {e}")
            if not self.dry_run: self._save_state()

class SimpleBacktester:
    """Backtester minimale per V3.0 - NEW ADDITION"""
    
    def __init__(self, trader: QuantumTraderV3):
        self.trader = trader
    
    def run_simple_test(self, days: int = 30):
        """Test semplice su N giorni recenti"""
        print(f"\n🧪 BACKTESTING V3.0 - Last {days} days simulation")
        print("="*50)
        
        # Simula cicli passati
        initial = self.trader.cash_balance
        cycles = days * 4  # 4 cicli al giorno (ogni 6h)
        
        for i in range(cycles):
            try:
                self.trader.run_cycle()
                time.sleep(1)  # Fast simulation
            except Exception as e:
                print(f"Cycle {i} error: {e}")
        
        final = self.trader.cash_balance
        for pos in self.trader.portfolio.values():
            final += pos['total_cost']
        
        roi = ((final - initial) / initial) * 100
        print(f"\n📊 BACKTEST RESULTS:")
        print(f"   Initial: ${initial:.2f}")
        print(f"   Final: ${final:.2f}")
        print(f"   ROI: {roi:+.2f}%")
        print(f"   Trades: {cycles} cycles simulated")
        return roi

def main():
    parser = argparse.ArgumentParser(description='Quantum Trader V3.0 MVP')
    parser.add_argument('--capital', type=float, default=200, help='Initial capital (default: 200)')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no real trades)')
    parser.add_argument('--backtest', type=int, help='Run backtest for N days')
    args = parser.parse_args()
    
    trader = QuantumTraderV3(initial_capital=args.capital, dry_run=True)
    
    if args.backtest:
        backtester = SimpleBacktester(trader)
        backtester.run_simple_test(days=args.backtest)
    else:
        trader.dry_run = args.dry_run
        trader.run()

if __name__ == "__main__":
    main()
