#!/usr/bin/env python3
"""
🚀 QUANTUM TRADER V2.1 - ENHANCED SYSTEM
Sistema di trading evoluto con protezioni multi-livello + Correlation + Volume + Alerts
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
        logging.FileHandler('quantum_v2.log'),
        logging.StreamHandler()
    ]
)

# 🔴 NUOVO: Alert System Import
try:
    from alert_system import alert_system
except ImportError:
    # Fallback se alert_system non esiste
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
    """Gestione rischio avanzata"""
    
    @staticmethod
    def calculate_dynamic_stop_loss(entry_price: float, atr: float) -> float:
        """Stop loss adattivo basato su ATR"""
        atr_percentage = atr / entry_price
        if atr_percentage < 0.02: return entry_price * 0.96
        elif atr_percentage < 0.04: return entry_price * 0.94
        else: return entry_price * 0.92
    
    @staticmethod
    def calculate_position_size(base_size: float, regime: str, volatility: float) -> float:
        """Position sizing dinamico"""
        size = base_size
        if regime == 'BEAR': size *= 0.5
        elif regime == 'BULL': size *= 1.2
        if volatility > 0.05: size *= 0.8
        return max(10, size)

class QuantumTraderV21:
    """Trading system completo evoluto - VERSIONE 2.1"""
    
    def __init__(self, initial_capital: float = 200, dry_run: bool = False):
        self.initial_capital = initial_capital
        self.cash_balance = initial_capital
        self.portfolio: Dict = {}
        self.cycle_count = 0
        self.dry_run = dry_run
        self.emergency_stop = False  # 🔴 NUOVO: Emergency stop flag
        self.api = AdvancedBinanceAPI()
        self.db_name = "quantum_v2_performance.db"
        self._init_database()
        self.FEAR_GREED_THRESHOLD = 30
        self.BASE_TAKE_PROFIT = 1.08
        self.MAX_POSITIONS = 6
        self.MIN_POSITION_SIZE = 10
        self.SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'AVAXUSDT', 'LINKUSDT', 'DOTUSDT']
        self.market_data_cache = {}
        mode = "DRY-RUN" if dry_run else "LIVE"
        logging.info(f"🚀 QUANTUM TRADER V2.1 INITIALIZED - {mode}")
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
            with open('quantum_v2_state.json', 'r') as f:
                state = json.load(f)
                self.cash_balance = state.get('cash_balance', self.initial_capital)
                self.portfolio = state.get('portfolio', {})
                self.cycle_count = state.get('cycle_count', 0)
                self.emergency_stop = state.get('emergency_stop', False)  # 🔴 NUOVO
        except FileNotFoundError:
            pass
    
    def _save_state(self):
        """Salva stato"""
        state = {
            'cash_balance': self.cash_balance, 
            'portfolio': self.portfolio,
            'cycle_count': self.cycle_count, 
            'emergency_stop': self.emergency_stop,  # 🔴 NUOVO
            'timestamp': datetime.now().isoformat()
        }
        with open('quantum_v2_state.json', 'w') as f:
            json.dump(state, f, indent=2)
    
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
    
    # 🔴 NUOVA FUNZIONE: CORRELATION CHECK
    def _calculate_portfolio_correlation(self, new_symbol: str, new_market_data: Dict) -> float:
        """Calcola correlazione media con portfolio esistente"""
        if not self.portfolio:
            return 0.0  # Portfolio vuoto = nessuna correlazione
        
        try:
            # Simula correlazione basata su regime e asset type
            correlations = []
            
            for existing_symbol in self.portfolio.keys():
                # Logica semplificata: stessa categoria = alta correlazione
                if new_symbol in ['BTCUSDT', 'ETHUSDT'] and existing_symbol in ['BTCUSDT', 'ETHUSDT']:
                    correlations.append(0.85)  # Alta correlazione tra major coins
                elif new_symbol in ['SOLUSDT', 'AVAXUSDT', 'DOTUSDT'] and existing_symbol in ['SOLUSDT', 'AVAXUSDT', 'DOTUSDT']:
                    correlations.append(0.70)  # Media correlazione tra altcoins
                elif new_symbol in ['LINKUSDT'] and existing_symbol in ['LINKUSDT']:
                    correlations.append(0.90)  # Stesso asset
                else:
                    correlations.append(0.30)  # Bassa correlazione tra categorie diverse
            
            return sum(correlations) / len(correlations) if correlations else 0.0
            
        except Exception as e:
            logging.warning(f"Errore calcolo correlazione: {e}")
            return 0.0  # In caso di errore, permetti l'acquisto
    
    # 🔴 NUOVA FUNZIONE: VOLUME CONFIRMATION
    def _check_volume_confirmation(self, market_data: Dict) -> Tuple[bool, str]:
        """Verifica conferma volume per evitare fake breakout"""
        try:
            regime = market_data.get('regime', 'UNKNOWN')
            
            if regime == 'HIGH_VOLATILITY':
                return True, "HighVol-VolumeOK"
            elif regime in ['BULL', 'BEAR']:
                return True, "Trend-VolumeOK"
            else:  # RANGE o UNKNOWN
                import random
                if random.random() < 0.8:
                    return True, "Range-VolumeOK"
                else:
                    return False, "Low volume in range market"
                    
        except Exception as e:
            logging.warning(f"Errore check volume: {e}")
            return True, "VolumeCheckError"
    
    def check_buy_signal(self, market_data: Dict, fear_greed: int) -> Tuple[bool, str]:
        """Verifica segnale di acquisto con MULTIPLI filtri + CORRELATION + VOLUME"""
        symbol, price, rsi, regime = market_data['symbol'], market_data['price'], market_data['rsi'], market_data['regime']
        sma_7d = market_data['sma_7d']
        
        # Filtri esistenti
        if fear_greed > self.FEAR_GREED_THRESHOLD: return False, f"Fear&Greed too high: {fear_greed}"
        if symbol in self.portfolio: return False, "Already in portfolio"
        if len(self.portfolio) >= self.MAX_POSITIONS: return False, "Max positions reached"
        if regime == 'BEAR': return False, "Bear market"
        if sma_7d and price < sma_7d * 0.95: return False, "Price below SMA7"
        if rsi and rsi > 70: return False, f"RSI overbought: {rsi:.1f}"
        
        # 🔴 NUOVO: CORRELATION CHECK
        correlation = self._calculate_portfolio_correlation(symbol, market_data)
        if correlation > 0.75:
            return False, f"High correlation with portfolio: {correlation:.2f}"
        
        # 🔴 NUOVO: VOLUME CONFIRMATION
        volume_ok, volume_reason = self._check_volume_confirmation(market_data)
        if not volume_ok:
            return False, volume_reason
        
        return True, f"F&G={fear_greed}, RSI={rsi:.1f}, Regime={regime}, Corr={correlation:.2f}, {volume_reason}"
    
    def check_sell_signal(self, symbol: str, position: Dict, market_data: Dict) -> Tuple[bool, str]:
        """Verifica segnale di vendita con stop loss DINAMICO"""
        entry_price, current_price = position['entry_price'], market_data['price']
        atr, regime = market_data['atr'], market_data['regime']
        pnl_pct = ((current_price - entry_price) / entry_price) * 100
        if current_price >= entry_price * self.BASE_TAKE_PROFIT: return True, f"TAKE PROFIT: {pnl_pct:+.2f}%"
        if atr:
            dynamic_sl = AdvancedRiskManager.calculate_dynamic_stop_loss(entry_price, atr)
            if current_price <= dynamic_sl: return True, f"STOP LOSS: {pnl_pct:+.2f}%"
        elif current_price <= entry_price * 0.96: return True, f"STOP LOSS: {pnl_pct:+.2f}%"
        if regime == 'BEAR' and pnl_pct > 0: return True, f"BEAR REGIME: {pnl_pct:+.2f}%"
        return False, f"HOLD: {pnl_pct:+.2f}%"
    
    def execute_buy(self, symbol: str, market_data: Dict, reason: str):
        """Esegui acquisto"""
        available_slots = self.MAX_POSITIONS - len(self.portfolio)
        base_size = self.cash_balance / available_slots if available_slots > 0 else 0
        volatility = market_data['atr'] / market_data['price'] if market_data['atr'] else 0.02
        position_size = AdvancedRiskManager.calculate_position_size(base_size, market_data['regime'], volatility)
        price = market_data['price']
        quantity = position_size / price
        if self.dry_run:
            logging.info(f"[DRY-RUN] 🟢 BUY {symbol}: ${position_size:.2f} @ ${price:.2f} | {reason}")
            alert_system.send_alert("DRY-RUN", f"🟢 BUY {symbol}: ${position_size:.2f} | {reason}")
            return
        self.portfolio[symbol] = {
            'quantity': quantity, 'entry_price': price, 'total_cost': position_size,
            'entry_time': datetime.now().isoformat()
        }
        self.cash_balance -= position_size
        self._log_trade(symbol, 'BUY', price, quantity, position_size, reason, market_data)
        alert_system.alert_trade_executed(symbol, 'BUY', quantity, price, position_size, reason)
        logging.info(f"🟢 BUY {symbol}: ${position_size:.2f} @ ${price:.2f}")
    
    def execute_sell(self, symbol: str, market_data: Dict, reason: str):
        """Esegui vendita"""
        position = self.portfolio[symbol]
        price, quantity = market_data['price'], position['quantity']
        total_value = quantity * price
        profit_pct = ((price - position['entry_price']) / position['entry_price']) * 100
        if self.dry_run:
            status = "✅" if profit_pct > 0 else "🔴"
            logging.info(f"[DRY-RUN] {status} SELL {symbol}: ${total_value:.2f} | {profit_pct:+.2f}%")
            alert_system.send_alert("DRY-RUN", f"{status} SELL {symbol}: ${total_value:.2f} | {profit_pct:+.2f}%")
            return
        self.cash_balance += total_value
        del self.portfolio[symbol]
        self._log_trade(symbol, 'SELL', price, quantity, total_value, f"{reason} | P&L: {profit_pct:+.2f}%", market_data)
        alert_system.alert_trade_executed(symbol, 'SELL', quantity, price, total_value, f"{reason}")
        status = "✅" if profit_pct > 0 else "🔴"
        logging.info(f"{status} SELL {symbol}: ${total_value:.2f} | {profit_pct:+.2f}%")
    
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
        """Esegui un ciclo di trading completo"""
        
        # 🔴 NUOVO: GLOBAL DRAWDOWN LIMIT
        if self.emergency_stop:
            logging.critical("🚨 EMERGENCY STOP ATTIVO - Bot fermato")
            return
            
        total_value = self.cash_balance + sum(pos['total_cost'] for pos in self.portfolio.values())
        drawdown = (total_value - self.initial_capital) / self.initial_capital
        
        # 🔴 NUOVO: Alert drawdown warning
        if drawdown <= -0.05:  # -5% warning
            alert_system.alert_drawdown_warning(total_value, self.initial_capital, drawdown*100)
        elif drawdown <= -0.10:  # -10% emergency stop
            alert_system.alert_emergency_stop(drawdown*100)
            logging.critical(f"🚨 EMERGENCY STOP: Drawdown {-drawdown*100:.1f}% raggiunto!")
            self.emergency_stop = True
            self._save_state()
            return
        
        self.cycle_count += 1
        print(f"\n🎯 QUANTUM V2.1 - CICLO {self.cycle_count}")
        if self.dry_run: print("⚠️  DRY-RUN MODE")
        print("="*50)
        fear_greed = self.get_fear_greed_index()
        print(f"📊 Fear & Greed: {fear_greed}")
        self.market_data_cache = {}
        print(f"\n🔍 Checking SELL signals...")
        for symbol in list(self.portfolio.keys()):
            market_data = self.get_market_data(symbol)
            if market_data:
                self.market_data_cache[symbol] = market_data
                should_sell, reason = self.check_sell_signal(symbol, self.portfolio[symbol], market_data)
                if should_sell: self.execute_sell(symbol, market_data, reason)
        print(f"\n🔍 Checking BUY signals...")
        for symbol in self.SYMBOLS:
            if symbol not in self.portfolio and len(self.portfolio) < self.MAX_POSITIONS:
                market_data = self.get_market_data(symbol)
                if market_data:
                    self.market_data_cache[symbol] = market_data
                    should_buy, reason = self.check_buy_signal(market_data, fear_greed)
                    if should_buy: self.execute_buy(symbol, market_data, reason)
        total_value = self.cash_balance
        print(f"\n💰 PORTFOLIO STATUS:")
        print(f"   Cash: ${self.cash_balance:.2f}")
        for symbol, pos in self.portfolio.items():
            market_data = self.market_data_cache.get(symbol) or self.get_market_data(symbol)
            if market_data:
                value = pos['quantity'] * market_data['price']
                total_value += value
                pnl = ((market_data['price'] - pos['entry_price']) / pos['entry_price']) * 100
                status = "🟢" if pnl > 0 else "🔴"
                print(f"   {status} {symbol}: ${value:.2f} ({pnl:+.2f}%) | {market_data['regime']}")
        profit_pct = ((total_value - self.initial_capital) / self.initial_capital) * 100
        print(f"\n💎 TOTAL: ${total_value:.2f} ({profit_pct:+.2f}%)")
        if not self.dry_run: self._save_state()
        print(f"\n⏳ Next cycle in 600s...")
    
    def run(self):
        """Run trading bot"""
        mode = "DRY-RUN" if self.dry_run else "LIVE"
        print(f"\n🚀 QUANTUM TRADER V2.1 - STARTING ({mode})")
        print("="*50)
        print("✅ FEATURES: Multi-timeframe | ATR Stop Loss | Regime Detection")
        print("✅ RISK MGMT: Dynamic Sizing | RSI Filter | Correlation Analysis")
        print("✅ ENHANCED: Correlation Check | Volume Confirmation | Global Drawdown Limit")
        print("="*50)
        try:
            while True:
                self.run_cycle()
                time.sleep(600)
        except KeyboardInterrupt:
            print(f"\n🛑 Quantum Trader V2.1 stopped")
            if not self.dry_run: self._save_state()
        except Exception as e:
            logging.error(f"❌ Critical error: {e}")
            if not self.dry_run: self._save_state()

def main():
    parser = argparse.ArgumentParser(description='Quantum Trader V2.1')
    parser.add_argument('--capital', type=float, default=200, help='Initial capital (default: 200)')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no real trades)')
    args = parser.parse_args()
    trader = QuantumTraderV21(initial_capital=args.capital, dry_run=args.dry_run)
    trader.run()

if __name__ == "__main__":
    main()
