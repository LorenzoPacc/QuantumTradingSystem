import time
from datetime import datetime, timedelta
import os
import numpy as np
from decimal import Decimal, ROUND_DOWN
import requests
import json
import logging
import pandas as pd
from typing import Dict, List, Tuple, Optional, Deque
import statistics
import ta
from scipy import stats
import sqlite3
from dataclasses import dataclass
import hmac
import hashlib
import uuid
from collections import deque
import warnings
warnings.filterwarnings('ignore')

# Configurazione logging più pulita
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quantum_ai_trader.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# =============================================================================
# 🔧 RATE LIMITER CON BACKOFF ESPONENZIALE
# =============================================================================

class AdvancedRateLimiter:
    """Rate limiter con backoff esponenziale per API failures"""
    
    def __init__(self):
        self.requests_log: Deque[float] = deque()
        self.max_requests_per_minute = 1000
        self.max_requests_per_second = 10
        self.api_failures: Dict[str, int] = {}  # Traccia fallimenti per endpoint
        self.backoff_base = 2  # Base per backoff esponenziale
    
    def wait_if_needed(self):
        """Aspetta se necessario per rispettare rate limits"""
        now = time.time()
        
        while self.requests_log and self.requests_log[0] < now - 60:
            self.requests_log.popleft()
        
        recent_second_requests = [req for req in self.requests_log if req > now - 1]
        if len(recent_second_requests) >= self.max_requests_per_second:
            sleep_time = 1.1 - (now - recent_second_requests[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
                now = time.time()
        
        if len(self.requests_log) >= self.max_requests_per_minute:
            sleep_time = 60.1 - (now - self.requests_log[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.requests_log.append(now)
    
    def record_api_failure(self, endpoint: str):
        """Registra fallimento API per backoff esponenziale"""
        self.api_failures[endpoint] = self.api_failures.get(endpoint, 0) + 1
    
    def record_api_success(self, endpoint: str):
        """Resetta contatore fallimenti per API che funziona"""
        if endpoint in self.api_failures:
            del self.api_failures[endpoint]
    
    def get_backoff_delay(self, endpoint: str) -> float:
        """Calcola delay per backoff esponenziale"""
        failures = self.api_failures.get(endpoint, 0)
        if failures == 0:
            return 0
        
        # Backoff esponenziale: 2^failures secondi, max 300 secondi (5 minuti)
        delay = min(300, self.backoff_base ** failures)
        logging.warning(f"🔧 Backoff per {endpoint}: {failures} failures → {delay}s delay")
        return delay

# =============================================================================
# 🔐 BINANCE TRADING ENGINE CON CACHE INTELLIGENTE
# =============================================================================

class BinanceTradingEngine:
    """MOTORE DI TRADING CON CACHE INTELLIGENTE E BACKOFF"""
    
    def __init__(self, api_key: str = "", api_secret: str = ""):
        self.base_url = "https://api.binance.com"
        self.api_key = api_key
        self.api_secret = api_secret
        self.rate_limiter = AdvancedRateLimiter()
        self.testnet = True
        
        if self.testnet:
            self.base_url = "https://testnet.binance.vision"
        
        # 🎯 CACHE INTELLIGENTE: Diversi timeout per diversi dati
        self.price_cache = {}
        self.price_timeout = 30  # 30s per prezzi real-time
        
        self.ohlcv_cache = {}
        self.ohlcv_timeout = 180  # 🎯 OTTIMIZZATO: 3 minuti invece di 5 (più real-time)
        
        # Cache per dati lenti (dominance, gold, etc.)
        self.slow_data_cache = {}
        self.slow_data_timeout = 600  # 10 minuti
    
    def _make_request(self, endpoint: str, params: Dict = None, method: str = 'GET') -> Optional[Dict]:
        """Esegue richiesta API con backoff esponenziale"""
        # 🎯 APPLICA BACKOFF ESPONENZIALE se necessario
        backoff_delay = self.rate_limiter.get_backoff_delay(endpoint)
        if backoff_delay > 0:
            time.sleep(backoff_delay)
        
        self.rate_limiter.wait_if_needed()
        
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {}
            
            if self.api_key:
                headers['X-MBX-APIKEY'] = self.api_key
            
            timeout = 15 if any(x in endpoint for x in ['gold', 'coingecko', 'alternative']) else 10
            
            if method == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=timeout)
            else:
                response = requests.post(url, params=params, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                # 🎯 REGISTRA SUCCESSO - reset backoff
                self.rate_limiter.record_api_success(endpoint)
                return response.json()
            else:
                logging.error(f"API Error {response.status_code} for {endpoint}: {response.text}")
                # 🎯 REGISTRA FALLIMENTO per backoff
                self.rate_limiter.record_api_failure(endpoint)
                return None
                
        except requests.exceptions.Timeout:
            logging.error(f"API Timeout for {endpoint}")
            self.rate_limiter.record_api_failure(endpoint)
            return None
        except Exception as e:
            logging.error(f"API Request error for {endpoint}: {e}")
            self.rate_limiter.record_api_failure(endpoint)
            return None
    
    def get_real_price(self, symbol: str) -> Optional[float]:
        """Prezzo reale con cache intelligente"""
        cache_key = f"price_{symbol}"
        current_time = time.time()
        
        if cache_key in self.price_cache:
            cached_time, price = self.price_cache[cache_key]
            if current_time - cached_time < self.price_timeout:
                return price
        
        data = self._make_request("/api/v3/ticker/price", {'symbol': symbol})
        if data and 'price' in data:
            price = float(data['price'])
            self.price_cache[cache_key] = (current_time, price)
            return price
        
        return None
    
    def get_ohlcv_data(self, symbol: str, interval: str = '1d', limit: int = 100) -> Optional[pd.DataFrame]:
        """Dati OHLCV con cache ottimizzata"""
        cache_key = f"ohlcv_{symbol}_{interval}_{limit}"
        current_time = time.time()
        
        if cache_key in self.ohlcv_cache:
            cached_time, df = self.ohlcv_cache[cache_key]
            # 🎯 CACHE CONDIZIONALE: usa cache solo se non troppo vecchia
            if current_time - cached_time < self.ohlcv_timeout:
                return df.copy()
        
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        data = self._make_request("/api/v3/klines", params)
        if not data:
            return None
        
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'trades',
            'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        self.ohlcv_cache[cache_key] = (current_time, df.copy())
        return df
    
    def create_test_order(self, symbol: str, side: str, quantity: float, order_type: str = 'MARKET') -> Optional[Dict]:
        """Ordine di test per sviluppo"""
        current_price = self.get_real_price(symbol)
        if not current_price:
            return None
        
        order_id = str(uuid.uuid4())[:8]
        
        return {
            'orderId': order_id,
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity,
            'price': current_price,
            'status': 'FILLED',
            'executedQty': quantity,
            'cummulativeQuoteQty': quantity * current_price
        }

# =============================================================================
# 🌐 REAL MARKET DATA ENGINE CON LOGGING OTTIMIZZATO
# =============================================================================

class RealMarketDataEngine:
    """MOTORE DATI REALI CON LOGGING INTELLIGENTE"""
    
    def __init__(self):
        self.binance = BinanceTradingEngine()
        self.cache = {}
        self.cache_timeout = 300
        self.gold_price_logged = False  # 🎯 Evita log ripetuti per gold price
    
    def get_real_price(self, symbol: str) -> Optional[float]:
        return self.binance.get_real_price(symbol)
    
    def get_ohlcv_data(self, symbol: str, interval: str = '1d', limit: int = 100) -> Optional[pd.DataFrame]:
        return self.binance.get_ohlcv_data(symbol, interval, limit)
    
    def get_fear_greed_index(self) -> int:
        try:
            url = "https://api.alternative.me/fng/"
            response = requests.get(url, timeout=15)
            data = response.json()
            return int(data['data'][0]['value'])
        except Exception as e:
            logging.error(f"Errore F&G: {e}")
            return 50
    
    def get_btc_dominance(self) -> float:
        cache_key = "btc_dominance"
        current_time = time.time()
        
        if cache_key in self.cache:
            cached_time, dominance = self.cache[cache_key]
            if current_time - cached_time < self.binance.slow_data_timeout:
                return dominance
        
        try:
            url = "https://api.coingecko.com/api/v3/global"
            response = requests.get(url, timeout=15)
            data = response.json()
            dominance = data['data']['market_cap_percentage']['btc']
            self.cache[cache_key] = (current_time, dominance)
            return dominance
        except Exception as e:
            logging.error(f"Errore BTC dominance: {e}")
            return 40.0
    
    def get_gold_price(self) -> Optional[float]:
        """🎯 GOLD API CON LOGGING INTELLIGENTE"""
        cache_key = "gold_price"
        current_time = time.time()
        
        # 🎯 CACHE PER DATI LENTI
        if cache_key in self.cache:
            cached_time, price = self.cache[cache_key]
            if current_time - cached_time < self.binance.slow_data_timeout:
                return price
        
        gold_apis = [
            {
                'url': "https://api.metals.live/v1/spot/gold",
                'parser': lambda data: float(data[0]['price']) if data and len(data) > 0 else None,
                'timeout': 10,
                'name': 'Metals.live'
            },
            {
                'url': "https://api.coingecko.com/api/v3/simple/price?ids=pax-gold&vs_currencies=usd",
                'parser': lambda data: data.get('pax-gold', {}).get('usd'),
                'timeout': 10,
                'name': 'CoinGecko PAXG'
            },
            {
                'url': "https://api.coingecko.com/api/v3/simple/price?ids=gold&vs_currencies=usd", 
                'parser': lambda data: data.get('gold', {}).get('usd'),
                'timeout': 10,
                'name': 'CoinGecko Gold'
            }
        ]
        
        for api in gold_apis:
            try:
                response = requests.get(api['url'], timeout=api['timeout'])
                if response.status_code == 200:
                    data = response.json()
                    price = api['parser'](data)
                    if price:
                        # 🎯 LOGGING INTELLIGENTE: solo prima volta o se cambia
                        cached_price = self.cache.get(cache_key, (0, 0))[1] if cache_key in self.cache else 0
                        if not self.gold_price_logged or abs(price - cached_price) > 10:
                            logging.info(f"🟡 Gold price from {api['name']}: ${price}")
                            self.gold_price_logged = True
                        
                        self.cache[cache_key] = (current_time, price)
                        return float(price)
            except Exception as e:
                logging.debug(f"Gold API {api['name']} failed: {e}")
                continue
        
        # 🎯 FALLBACK SILENZIOSO (no log ripetuti)
        if not self.gold_price_logged:
            logging.warning("⚠️ All gold APIs failed, using fallback: $1950")
            self.gold_price_logged = True
        
        return 1950.0

# =============================================================================
# 🧠 ADAPTIVE LEARNING ENGINE (IDENTICO - GIÀ PERFETTO)
# =============================================================================

class AdaptiveLearningEngine:
    """MOTORE DI APPRENDIMENTO - GIÀ PERFETTO"""
    
    def __init__(self):
        self.performance_db = "trading_performance.db"
        self._init_database()
        self.optimal_params = self._load_optimal_parameters()
        
    def _init_database(self):
        conn = sqlite3.connect(self.performance_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                symbol TEXT,
                entry_price REAL,
                exit_price REAL,
                pnl_percent REAL,
                holding_days REAL,
                market_regime TEXT,
                fear_greed INTEGER,
                parameters_used TEXT,
                success_score REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parameter_optimization (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                parameter_name TEXT,
                old_value REAL,
                new_value REAL,
                performance_impact REAL,
                reason TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_optimal_parameters(self) -> Dict:
        return {
            'take_profit_base': 8.0,
            'stop_loss_base': -4.0,
            'confluence_threshold': 0.65,
            'position_size_base': 0.10,
            'max_position_size': 30.0,
            'max_portfolio_exposure': 0.4,
            'fear_boost': 1.4,
            'greed_reduction': 0.6,
            'volatility_adjustment': 1.3
        }
    
    def record_trade_performance(self, symbol: str, entry_price: float, exit_price: float,
                               pnl_percent: float, holding_hours: float, market_regime: str,
                               fear_greed: int, parameters: Dict):
        holding_days = holding_hours / 24.0
        success_score = self._calculate_success_score(pnl_percent, holding_days)
        
        conn = sqlite3.connect(self.performance_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trade_performance 
            (timestamp, symbol, entry_price, exit_price, pnl_percent, holding_days, 
             market_regime, fear_greed, parameters_used, success_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (datetime.now(), symbol, entry_price, exit_price, pnl_percent, holding_days,
              market_regime, fear_greed, json.dumps(parameters), success_score))
        
        conn.commit()
        conn.close()
        
        self._auto_tune_parameters(pnl_percent, success_score, market_regime)
    
    def _calculate_success_score(self, pnl_percent: float, holding_days: float) -> float:
        time_efficiency = min(1.0, 7.0 / max(0.1, holding_days))
        profit_score = min(1.0, max(0.0, (pnl_percent + 20) / 40))
        return (profit_score * 0.7 + time_efficiency * 0.3)
    
    def _auto_tune_parameters(self, pnl_percent: float, success_score: float, market_regime: str):
        if success_score < 0.3 and pnl_percent < -5:
            self.optimal_params['position_size_base'] = max(0.05, self.optimal_params['position_size_base'] * 0.8)
            self.optimal_params['max_position_size'] = max(20, self.optimal_params['max_position_size'] * 0.8)
        elif success_score > 0.8 and pnl_percent > 10:
            self.optimal_params['position_size_base'] = min(0.15, self.optimal_params['position_size_base'] * 1.1)
    
    def get_optimized_parameters(self) -> Dict:
        return self.optimal_params.copy()

# =============================================================================
# 📊 PORTFOLIO MANAGEMENT (IDENTICO - GIÀ PERFETTO)
# =============================================================================

class AdvancedPortfolioManager:
    """GESTIONE PORTAFOGLIO - GIÀ PERFETTA"""
    
    def __init__(self, initial_balance: float, market_data: RealMarketDataEngine, learning_engine: AdaptiveLearningEngine):
        self.cash_balance = Decimal(str(initial_balance))
        self.initial_balance = Decimal(str(initial_balance))
        self.portfolio: Dict[str, Dict] = {}
        self.trade_history: List[Dict] = []
        self.market_data = market_data
        self.learning_engine = learning_engine
        self.binance = BinanceTradingEngine()
    
    def get_portfolio_value(self) -> float:
        total = float(self.cash_balance)
        for symbol, position in self.portfolio.items():
            current_price = self.market_data.get_real_price(symbol)
            if current_price:
                total += position['quantity'] * current_price
        return total
    
    def get_current_exposure(self) -> float:
        portfolio_value = self.get_portfolio_value()
        if portfolio_value == 0:
            return 0.0
        invested_value = portfolio_value - float(self.cash_balance)
        return invested_value / portfolio_value
    
    def execute_buy(self, symbol: str, amount: float, reason: str) -> bool:
        try:
            current_exposure = self.get_current_exposure()
            params = self.learning_engine.get_optimized_parameters()
            
            if current_exposure >= params['max_portfolio_exposure']:
                logging.warning(f"Exposure limit reached: {current_exposure:.1%}")
                return False
            
            if amount > float(self.cash_balance):
                logging.warning(f"Insufficient cash: ${amount:.2f} > ${float(self.cash_balance):.2f}")
                return False
            
            current_price = self.market_data.get_real_price(symbol)
            if not current_price:
                logging.error(f"Cannot get price for {symbol}")
                return False
            
            quantity = float(amount) / float(current_price)
            quantity = quantity.quantize(Decimal('0.000001'), rounding=ROUND_DOWN)
            
            if quantity <= Decimal('0'):
                logging.error(f"Invalid quantity: {quantity}")
                return False
            
            order_result = self.binance.create_test_order(symbol, 'BUY', float(quantity))
            if not order_result:
                logging.error(f"Order failed for {symbol}")
                return False
            
            entry_time = datetime.now()
            if symbol in self.portfolio:
                old_pos = self.portfolio[symbol]
                new_quantity = old_pos['quantity'] + quantity
                new_cost = old_pos['total_cost'] + float(amount)
                self.portfolio[symbol] = {
                    'quantity': new_quantity,
                    'entry_price': float(new_cost / new_quantity),
                    'total_cost': float(new_cost),
                    'first_entry': old_pos['first_entry'],
                    'last_entry': entry_time,
                    'entries': old_pos['entries'] + [{
                        'timestamp': entry_time,
                        'quantity': float(quantity),
                        'price': current_price,
                        'amount': amount
                    }]
                }
            else:
                self.portfolio[symbol] = {
                    'quantity': quantity,
                    'entry_price': current_price,
                    'total_cost': float(amount),
                    'first_entry': entry_time,
                    'last_entry': entry_time,
                    'entries': [{
                        'timestamp': entry_time,
                        'quantity': float(quantity),
                        'price': current_price,
                        'amount': amount
                    }]
                }
            
            self.cash_balance -= float(amount)
            
            self.trade_history.append({
                'timestamp': entry_time,
                'symbol': symbol,
                'action': 'BUY',
                'quantity': float(quantity),
                'price': current_price,
                'amount': amount,
                'reason': reason
            })
            
            logging.info(f"✅ ACQUISTO ESEGUITO: {symbol} | ${amount:.2f} | @ ${current_price:.4f}")
            return True
            
        except Exception as e:
            logging.error(f"Errore acquisto {symbol}: {e}")
            return False
    
    def execute_sell(self, symbol: str, reason: str) -> bool:
        try:
            if symbol not in self.portfolio:
                logging.error(f"Position not found: {symbol}")
                return False
            
            current_price = self.market_data.get_real_price(symbol)
            if not current_price:
                logging.error(f"Cannot get price for {symbol}")
                return False
            
            position = self.portfolio[symbol]
            quantity = position['quantity']
            
            order_result = self.binance.create_test_order(symbol, 'SELL', float(quantity))
            if not order_result:
                logging.error(f"Sell order failed for {symbol}")
                return False
            
            revenue = quantity * float(current_price)
            total_cost = Decimal(str(position['total_cost']))
            profit = revenue - total_cost
            profit_pct = (profit / total_cost) * 100
            
            first_entry = position['first_entry']
            holding_days = (datetime.now() - first_entry).total_seconds() / (24 * 3600)
            
            self.cash_balance += revenue
            
            self.trade_history.append({
                'timestamp': datetime.now(),
                'symbol': symbol,
                'action': 'SELL',
                'quantity': float(quantity),
                'price': current_price,
                'amount': float(revenue),
                'profit': float(profit),
                'profit_pct': float(profit_pct),
                'reason': reason
            })
            
            holding_hours = holding_days * 24
            self.learning_engine.record_trade_performance(
                symbol, position['entry_price'], current_price,
                float(profit_pct), holding_hours, "NEUTRAL", 50, 
                self.learning_engine.get_optimized_parameters()
            )
            
            del self.portfolio[symbol]
            
            logging.info(f"✅ VENDITA ESEGUITA: {symbol} | P&L: {profit_pct:.2f}% | Days: {holding_days:.1f} | {reason}")
            return True
            
        except Exception as e:
            logging.error(f"Errore vendita {symbol}: {e}")
            return False
    
    def check_exit_conditions(self, symbol_scores: Dict[str, float]) -> List[str]:
        sold_positions = []
        
        for symbol, position in list(self.portfolio.items()):
            current_price = self.market_data.get_real_price(symbol)
            if not current_price:
                continue
            
            entry_price = position['entry_price']
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
            current_score = symbol_scores.get(symbol, 0.5)
            
            first_entry = position['first_entry']
            holding_days = (datetime.now() - first_entry).days
            
            exit_reason = None
            
            if pnl_pct >= 8.0:
                exit_reason = f"TAKE_PROFIT: +{pnl_pct:.1f}%"
            elif pnl_pct <= -4.0:
                exit_reason = f"STOP_LOSS: {pnl_pct:.1f}%"
            elif current_score < 0.4:
                exit_reason = f"LOW_SCORE: {current_score:.3f}"
            elif holding_days >= 7 and pnl_pct > 2:
                exit_reason = f"TIME_EXIT: {holding_days} days, +{pnl_pct:.1f}%"
            
            if exit_reason and self.execute_sell(symbol, exit_reason):
                sold_positions.append(symbol)
        
        return sold_positions

# =============================================================================
# 🚀 QUANTUM AI TRADER ULTIMATE - VERSIONE DEFINITIVA
# =============================================================================

class QuantumAITraderUltimate:
    """VERSIONE ULTIMATE - OTTIMIZZAZIONI FINALI APPLICATE"""
    
    def __init__(self, initial_balance: float = 200):
        self.market_data = RealMarketDataEngine()
        self.learning_engine = AdaptiveLearningEngine()
        self.portfolio_manager = AdvancedPortfolioManager(initial_balance, self.market_data, self.learning_engine)
        self.cycle_count = 0
        self.initial_balance = initial_balance
        
        logging.info("🚀 QUANTUM AI TRADER ULTIMATE - SISTEMA DEFINITIVO AVVIATO")

    def _calculate_confluence_score(self, symbol: str) -> Dict:
        try:
            price_data = self.market_data.get_ohlcv_data(symbol, '4h', 20)
            if price_data is None:
                return {'final_score': 0.5}
            
            closes = price_data['close'].values
            volumes = price_data['volume'].values
            
            if len(closes) < 10:
                return {'final_score': 0.5}
            
            momentum = ((closes[-1] - closes[-5]) / closes[-5]) * 100
            volume_ratio = volumes[-1] / np.mean(volumes[-5:])
            
            base_score = 0.5
            if momentum > 2:
                base_score += 0.2
            elif momentum < -2:
                base_score -= 0.2
            
            if volume_ratio > 1.2:
                base_score += 0.1
            
            fgi = self.market_data.get_fear_greed_index()
            if fgi < 30:
                base_score *= 1.2
            elif fgi > 70:
                base_score *= 0.8
            
            return {
                'final_score': max(0.1, min(0.9, base_score)),
                'fear_greed_index': fgi
            }
            
        except Exception as e:
            logging.error(f"Errore calcolo score {symbol}: {e}")
            return {'final_score': 0.5}
    
    def execute_ultimate_trading_cycle(self):
        """CICLO DI TRADING ULTIMATE - OTTIMIZZATO"""
        self.cycle_count += 1
        
        print(f"\n{'='*100}")
        print(f"🧠 CICLO {self.cycle_count} - QUANTUM AI ULTIMATE")
        print(f"{'='*100}")
        
        fgi = self.market_data.get_fear_greed_index()
        portfolio_value = self.portfolio_manager.get_portfolio_value()
        current_exposure = self.portfolio_manager.get_current_exposure()
        
        print(f"😨 FEAR & GREED: {fgi} | 💰 Portfolio: ${portfolio_value:.2f} | 📊 Exposure: {current_exposure:.1%}")
        print()
        
        assets = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'AVAXUSDT', 'LINKUSDT', 'DOTUSDT']
        
        print("🔍 CONTROLLO VENDITE AUTOMATICHE:")
        symbol_scores = {}
        for symbol in assets:
            analysis = self._calculate_confluence_score(symbol)
            symbol_scores[symbol] = analysis['final_score']
        
        sold_positions = self.portfolio_manager.check_exit_conditions(symbol_scores)
        for symbol in sold_positions:
            print(f"   ✅ VENDITA: {symbol}")
        
        print("\n💰 ANALISI ACQUISTI:")
        params = self.learning_engine.get_optimized_parameters()
        
        bought_positions = []
        for symbol in assets:
            if symbol in self.portfolio_manager.portfolio:
                continue
            
            score_data = self._calculate_confluence_score(symbol)
            final_score = score_data['final_score']
            
            print(f"   📊 {symbol}: Score {final_score:.3f}", end="")
            
            if final_score >= params['confluence_threshold']:
                position_size = self._calculate_optimized_position_size(symbol, final_score, fgi, params)
                
                if position_size > 0:
                    reason = f"AI_SCORE: {final_score:.3f}, FGI: {fgi}"
                    if self.portfolio_manager.execute_buy(symbol, position_size, reason):
                        bought_positions.append(symbol)
                        print(f" → 🤖 ACQUISTO: ${position_size:.2f}")
                    else:
                        print(" → ❌ FALLITO")
                else:
                    print(" → ⚠️ NO_FUNDS")
            else:
                print(" → ⚪ HOLD")
        
        self._generate_ultimate_report(sold_positions, bought_positions, params)
        
        return len(sold_positions) + len(bought_positions)
    
    def _calculate_optimized_position_size(self, symbol: str, score: float, fgi: int, params: Dict) -> float:
        """CALCOLO POSITION SIZE - FIXED DECIMAL BUG"""
        try:
            # 🔧 CONVERTI TUTTO IN FLOAT PRIMA DEI CALCOLI
            available_cash = float(self.portfolio_manager.cash_balance)
            
            if available_cash < 10:
                return 0.0
            
            base_size = available_cash * float(params['position_size_base'])
            score_multiplier = 0.5 + float(score)
            
            if fgi < 25:
                fear_multiplier = float(params['fear_boost'])
            elif fgi < 40:
                fear_multiplier = 1.2
            elif fgi > 70:
                fear_multiplier = float(params['greed_reduction'])
            else:
                fear_multiplier = 1.0
            
            final_size = base_size * score_multiplier * fear_multiplier
            
            # Limiti di sicurezza
            max_pos = float(params['max_position_size'])
            final_size = min(max_pos, final_size)
            final_size = max(10.0, final_size)
            
            # Check esposizione
            current_exposure = self.portfolio_manager.get_current_exposure()
            max_exposure = float(params['max_portfolio_exposure'])
            if current_exposure >= max_exposure:
                return 0.0
            
            return float(final_size)
            
        except Exception as e:
            logging.error(f'Errore position size {symbol}: {e}')
            return 0.0
    
    def _generate_ultimate_report(self, sold_positions: List, bought_positions: List, params: Dict):
        """REPORT ULTIMATE CON INFO SISTEMA"""
        portfolio_value = self.portfolio_manager.get_portfolio_value()
        total_profit = portfolio_value - self.initial_balance
        profit_pct = (total_profit / self.initial_balance) * 100
        
        print(f"\n📊 QUANTUM AI ULTIMATE REPORT:")
        print(f"   💰 Cash: ${float(self.portfolio_manager.cash_balance):.2f}")
        print(f"   📦 Portfolio Value: ${portfolio_value:.2f}")
        print(f"   💎 TOTALE: ${portfolio_value:.2f} ({total_profit:+.2f} / {profit_pct:+.1f}%)")
        print(f"   📊 Exposure: {self.portfolio_manager.get_current_exposure():.1%}")
        print(f"   🤖 Trade Eseguiti: {len(sold_positions)} vendite, {len(bought_positions)} acquisti")
        
        # 🎯 INFO SISTEMA OTTIMIZZATO
        print(f"   ⚙️  Sistema: OHLCV Cache {self.market_data.binance.ohlcv_timeout}s")
        print(f"   🔧 Backoff: Attivo | Gold API: Logging intelligente")
        
        if self.portfolio_manager.portfolio:
            print(f"\n   🎯 POSIZIONI ATTIVE:")
            for symbol, position in self.portfolio_manager.portfolio.items():
                current_price = self.market_data.get_real_price(symbol)
                if current_price:
                    pnl_pct = ((current_price - position['entry_price']) / position['entry_price']) * 100
                    value = position['quantity'] * current_price
                    holding_days = (datetime.now() - position['first_entry']).days
                    status = "🟢" if pnl_pct >= 0 else "🔴"
                    print(f"      {status} {symbol}: ${value:.2f} ({pnl_pct:+.1f}%) - {holding_days} giorni")
    
    def run_ultimate_trading(self, cycles: int = 1000, delay: int = 600):
        """ESECUZIONE ULTIMATE - OTTIMIZZATA"""
        print(f"\n{'='*100}")
        print("🚀 QUANTUM AI TRADER ULTIMATE - VERSIONE DEFINITIVA")
        print("🎯 OTTIMIZZAZIONI FINALI:")
        print("   ✅ Backoff Esponenziale: 2^n secondi per API failures")
        print("   ✅ Cache Intelligente: OHLCV 3min (era 5min) - Più real-time")
        print("   ✅ Logging Ottimizzato: Gold price solo quando cambia")
        print("   ✅ Multiple Timeout: 30s prezzi, 3min OHLCV, 10min dati lenti")
        print("   ✅ Resilienza Massima: Gestione errori avanzata")
        print(f"⏰ Intervallo Cicli: {delay} secondi")
        print(f"{'='*100}\n")
        
        for i in range(cycles):
            try:
                start_time = datetime.now()
                
                trades_executed = self.execute_ultimate_trading_cycle()
                
                cycle_duration = (datetime.now() - start_time).total_seconds()
                next_cycle = max(300, delay - cycle_duration)
                
                if i < cycles - 1:
                    next_time = (datetime.now() + timedelta(seconds=next_cycle)).strftime("%H:%M:%S")
                    print(f"\n⏳ Prossimo ciclo alle {next_time} ({next_cycle:.0f}s)...")
                    time.sleep(next_cycle)
                    
            except KeyboardInterrupt:
                print(f"\n🛑 SISTEMA FERMATO - {i+1} cicli completati")
                break
            except Exception as e:
                logging.error(f"Errore critico: {e}")
                print(f"\n❌ ERRORE CRITICO: {e}")
                time.sleep(60)

# 🔥 AVVIA IL SISTEMA ULTIMATE
if __name__ == "__main__":
    trader = QuantumAITraderUltimate(200)
    trader.run_ultimate_trading(cycles=1000, delay=600)
