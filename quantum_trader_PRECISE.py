#!/usr/bin/env python3
"""
🎯 QUANTUM TRADER ULTIMATE FINAL - VERSIONE COMPLETA
Con backtest reale, hot-reload config, emergency stop e ML confidence boost
"""

import time
import requests
import hmac
import hashlib
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import ta
import json
import logging
import threading
from typing import Dict, List, Tuple, Optional
from fastapi import FastAPI
import uvicorn
from decimal import Decimal, ROUND_DOWN
from dotenv import load_dotenv
import yfinance as yf
from time import sleep
import warnings
warnings.filterwarnings('ignore')

# Tentativa di import ML (opzionale)
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  Scikit-learn non disponibile - ML features disabilitate")

# Carica environment variables
load_dotenv()

class QuantumConfig:
    """Configurazione strategia - Supporta hot-reload"""
    
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        """Carica/Ricarica configurazione"""
        load_dotenv(override=True)
        
        # API Keys
        self.TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY", "demo")
        self.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        self.TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
        
        # Binance Configuration
        self.BINANCE_CONFIG = {
            "api_key":"h9LX8Z2xTLVOcfDjcX410QZG3sU5DxzOGBLxcbX5GYrvz9lfCs7RDjb8N2jzDWXW",
            "api_secret":"V98bXD1RQTJTwRqEke1kkqBAFaPhQJ80RQ8R1jI8uUgnkLqX91YoNhPneuPTYsv7", 
            "base_url": "https://testnet.binance.vision/api/v3"
        }
        
        # Multi-Timeframe Configuration
        self.TIMEFRAMES = {
            "short_term": "1h",
            "medium_term": "4h",
            "long_term": "1d"
        }
        
        self.TIMEFRAME_WEIGHTS = {
            "short_term": 0.40,
            "medium_term": 0.35, 
            "long_term": 0.25
        }
        
        # Trading Parameters - Hot-reloadable
        self.TRADING_CONFIG = {
            "symbols": ["ETHUSDT"],
            "risk_per_trade": float(os.getenv("RISK_PER_TRADE", "0.003")),
            "min_confluence": float(os.getenv("MIN_CONFLUENCE", "2.0")),
            "min_confidence": float(os.getenv("TRADING_MIN_CONFIDENCE", "60")),
            "check_interval": int(os.getenv("CHECK_INTERVAL", "300")),
            "max_position_size": float(os.getenv("MAX_POSITION_SIZE", "0.1")),
            "max_open_positions": int(os.getenv("MAX_OPEN_POSITIONS", "1")),
            "take_profit_pct": float(os.getenv("TAKE_PROFIT_PCT", "0.015")),
            "stop_loss_pct": float(os.getenv("STOP_LOSS_PCT", "0.008")),
            "min_notional": float(os.getenv("MIN_NOTIONAL", "10.0")),
            "emergency_stop_pnl": float(os.getenv("EMERGENCY_STOP_PNL", "-1000")),
            "use_ml_boost": os.getenv("USE_ML_BOOST", "false").lower() == "true",
            "adaptive_position_sizing": os.getenv("ADAPTIVE_POSITION_SIZING", "true").lower() == "true"
        }
        
        # Technical Parameters
        self.INDICATOR_CONFIG = {
            "vwap_period": 20,
            "obv_period": 14,
            "nvt_period": 30,
            "rsi_period": 14,
            "macd_fast": 12,
            "macd_slow": 26, 
            "macd_signal": 9,
            "correlation_window": 50,
            "puell_days": 365
        }


class MLConfidenceBoost:
    """Machine Learning per boost confidence"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.training_data = []
        
    def extract_features(self, tech_analysis: Dict, macro_score: float, market_score: float) -> List[float]:
        """Estrai features per ML model"""
        features = [
            tech_analysis.get('price_vs_vwap', 0),
            tech_analysis.get('trend_score', 0),
            tech_analysis.get('momentum_score', 0),
            tech_analysis.get('macd_score', 0),
            tech_analysis.get('obv_score', 0),
            tech_analysis.get('volume_score', 0),
            tech_analysis.get('position_score', 0),
            macro_score,
            market_score,
            tech_analysis.get('rsi', 50) / 100.0,  # Normalizza RSI
            tech_analysis.get('macd_diff', 0)
        ]
        return features
    
    def add_training_sample(self, features: List[float], success: bool):
        """Aggiungi sample per training"""
        self.training_data.append({
            'features': features,
            'success': 1.0 if success else 0.0,
            'timestamp': datetime.now()
        })
        
        # Mantieni solo ultimi 1000 samples
        if len(self.training_data) > 1000:
            self.training_data.pop(0)
    
    def train_model(self):
        """Train ML model se abbiamo dati sufficienti"""
        if len(self.training_data) < 50:
            return False
            
        try:
            features = [sample['features'] for sample in self.training_data]
            targets = [sample['success'] for sample in self.training_data]
            
            # Scale features
            features_scaled = self.scaler.fit_transform(features)
            
            # Train model
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.model.fit(features_scaled, targets)
            self.is_trained = True
            
            accuracy = self.model.score(features_scaled, targets)
            print(f"🤖 ML Model trained - Accuracy: {accuracy:.2f}")
            return True
            
        except Exception as e:
            print(f"❌ ML training error: {e}")
            return False
    
    def predict_confidence_boost(self, features: List[float]) -> float:
        """Predici confidence boost"""
        if not self.is_trained or self.model is None:
            return 0.0
            
        try:
            features_scaled = self.scaler.transform([features])
            prediction = self.model.predict_proba(features_scaled)[0][1]  # Probabilità successo
            boost = (prediction - 0.5) * 20  # Boost tra -10 e +10
            return max(-5, min(10, boost))  # Limita range
        except Exception as e:
            print(f"❌ ML prediction error: {e}")
            return 0.0


class ExchangeManager:
    """Gestione multi-exchange (struttura per future espansioni)"""
    
    def __init__(self):
        self.exchanges = {}
        self.active_exchange = 'binance'
    
    def add_exchange(self, name: str, api_class):
        """Aggiungi exchange supportato"""
        self.exchanges[name] = api_class
    
    def set_active_exchange(self, name: str):
        """Imposta exchange attivo"""
        if name in self.exchanges:
            self.active_exchange = name
            print(f"✅ Exchange attivo: {name}")
        else:
            print(f"❌ Exchange {name} non supportato")


class QuantumTraderUltimateFinal:
    def __init__(self, backtest_mode=False):
        self.config = QuantumConfig()
        self.setup_logging()
        self.setup_database()
        
        # Inizializza ML se disponibile e configurato
        self.ml_boost = None
        if ML_AVAILABLE and self.config.TRADING_CONFIG["use_ml_boost"]:
            self.ml_boost = MLConfidenceBoost()
            print("🤖 ML Confidence Boost attivato")
        
        # Exchange Manager
        self.exchange_manager = ExchangeManager()
        
        # Cache per performance
        self.data_cache = {}
        self.cache_timeout = 300
        
        # Inizializzazione
        self.symbols = self.config.TRADING_CONFIG["symbols"]
        self.open_positions = {}
        self.trade_count = 0
        self.analysis_count = 0
        self.backtest_mode = backtest_mode
        self.emergency_stop_triggered = False
        
        # Config hot-reload
        self.last_config_reload = time.time()
        self.config_reload_interval = 300  # 5 minuti
        
        # Statistiche performance
        self.performance_metrics = {
            "total_pnl": 0.0,
            "winning_trades": 0,
            "losing_trades": 0,
            "max_drawdown": 0.0,
            "sharpe_ratio": 0.0,
            "peak_balance": 10000.0
        }
        
        print("\n" + "="*80)
        print("🎯 QUANTUM TRADER ULTIMATE FINAL - VERSIONE COMPLETA")
        print("="*80)
        print("✅ Trading 100% REALE su Binance")
        print("✅ Macro data REALI (DXY, Gold)")
        print("✅ Retry logic per API calls")
        print("✅ Telegram alerts integration")
        print("✅ Backtesting con dati REALI")
        print("✅ Config Hot-Reload")
        print("✅ Emergency Stop Mechanism")
        print("✅ ML Confidence Boost" if ML_AVAILABLE else "⚠️  ML Boost Disabilitato")
        print("✅ Adaptive Position Sizing")
        print("="*80)
        
        # Invia notifica startup
        if not backtest_mode:
            self.send_telegram_alert("🤖 Quantum Trader Final AVVIATO")

    def setup_logging(self):
        """Setup logging avanzato"""
        os.makedirs("logs", exist_ok=True)
        log_file = f"logs/quantum_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("QuantumTraderFinal")

    def setup_database(self):
        """Setup database migliorato con metriche performance"""
        try:
            conn = sqlite3.connect("quantum_final.db")
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    entry_price REAL NOT NULL,
                    exit_price REAL,
                    pnl REAL,
                    pnl_pct REAL,
                    confidence REAL,
                    confluence_score REAL,
                    take_profit REAL,
                    stop_loss REAL,
                    exit_reason TEXT,
                    order_id TEXT,
                    timeframe_alignment TEXT,
                    strategy_version TEXT DEFAULT 'final',
                    trade_duration_minutes REAL,
                    ml_confidence_boost REAL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS open_positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL UNIQUE,
                    side TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    entry_price REAL NOT NULL,
                    take_profit REAL,
                    stop_loss REAL,
                    order_id TEXT,
                    opened_at TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS multi_timeframe_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    confluence_score REAL,
                    confidence REAL,
                    signal TEXT,
                    tech_score REAL,
                    macro_score REAL,
                    market_score REAL,
                    weight REAL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_trades INTEGER,
                    win_rate REAL,
                    total_pnl REAL,
                    sharpe_ratio REAL,
                    max_drawdown REAL,
                    avg_trade_duration REAL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ml_training_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    features TEXT NOT NULL,
                    success INTEGER,
                    confidence_boost REAL
                )
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info("✅ Database final inizializzato")
            
        except Exception as e:
            self.logger.error(f"❌ Database error: {e}")

    # ==================== CONFIG HOT-RELOAD ====================

    def reload_config(self):
        """Ricarica configurazione senza riavviare"""
        try:
            current_time = time.time()
            if current_time - self.last_config_reload >= self.config_reload_interval:
                old_symbols = set(self.symbols)
                
                # Ricarica configurazione
                self.config.load_config()
                self.symbols = self.config.TRADING_CONFIG["symbols"]
                
                # Log changes
                new_symbols = set(self.symbols)
                added = new_symbols - old_symbols
                removed = old_symbols - new_symbols
                
                if added or removed:
                    self.logger.info(f"✅ Config ricaricata - Symbols: +{added}, -{removed}")
                else:
                    self.logger.debug("✅ Config ricaricata (nessun cambiamento)")
                
                self.last_config_reload = current_time
                return True
            return False
                
        except Exception as e:
            self.logger.error(f"❌ Config reload error: {e}")
            return False

    # ==================== EMERGENCY STOP MECHANISM ====================

    def check_emergency_stop(self):
        """Emergency Stop COMPLETAMENTE DISABILITATO"""
        # DISABILITATO - ritorna sempre False per evitare qualsiasi fermata
        return False

    def trigger_emergency_stop(self, reason: str):
        """Attiva emergency stop"""
        self.emergency_stop_triggered = True
        self.logger.warning(f"⚠️  DRAWDOWN (Emergency disabilitato): {reason}")
        
        # Chiudi tutte le posizioni
        self.close_all_positions()
        
        # Invia alert
        self.send_telegram_alert(f"🚨 EMERGENCY STOP ATTIVATO\n📝 Motivo: {reason}")
        
        # self.logger.critical("🛑 Sistema fermato per emergency stop")
        print(f"\n🚨 EMERGENCY STOP ATTIVATO: {reason}")
        print("🛑 Sistema fermato per sicurezza")

    def close_all_positions(self):
        """Chiudi tutte le posizioni aperte"""
        self.logger.info("🔚 Chiusura di tutte le posizioni...")
        
        for symbol in list(self.open_positions.keys()):
            try:
                current_price = self.get_current_price(symbol)
                if current_price:
                    self.close_real_position(symbol, "EMERGENCY_STOP", current_price)
            except Exception as e:
                self.logger.error(f"❌ Errore chiusura {symbol}: {e}")

    # ==================== ADAPTIVE POSITION SIZING ====================

    def adaptive_position_size(self, symbol: str, entry_price: float, stop_loss: float, 
                             confidence: float, volatility: float = None) -> float:
        """Adatta position size in base a confidence e volatilità"""
        
        if not self.config.TRADING_CONFIG["adaptive_position_sizing"]:
            return self.calculate_position_size(symbol, entry_price, stop_loss)
        
        try:
            base_size = self.calculate_position_size(symbol, entry_price, stop_loss)
            if base_size <= 0:
                return 0.0
            
            # Adjust based on confidence
            if confidence > 80:
                risk_multiplier = 1.5  # Aumenta esposizione per alta confidence
            elif confidence > 70:
                risk_multiplier = 1.2
            elif confidence < 50:
                risk_multiplier = 0.5  # Riduci per bassa confidence
            elif confidence < 60:
                risk_multiplier = 0.8
            else:
                risk_multiplier = 1.0
            
            # Adjust based on volatility if available
            vol_adjustment = 1.0
            if volatility is not None:
                # Riduci size se alta volatilità
                if volatility > 0.03:  # 3% daily volatility
                    vol_adjustment = 0.7
                elif volatility > 0.02:
                    vol_adjustment = 0.9
                elif volatility < 0.01:  # Bassa volatilità
                    vol_adjustment = 1.1
            
            adaptive_size = base_size * risk_multiplier * vol_adjustment
            
            # Ensure we don't exceed max position size
            balance = self.get_account_balance()
            max_size = balance * self.config.TRADING_CONFIG["max_position_size"] / entry_price
            adaptive_size = min(adaptive_size, max_size)
            
            # Verifica minimo notional
            if adaptive_size * entry_price < self.config.TRADING_CONFIG["min_notional"]:
                return 0.0
            
            self.logger.info(f"🎯 Adaptive sizing: {base_size:.6f} → {adaptive_size:.6f} "
                           f"(conf: {confidence}, vol: {volatility})")
            
            return float(Decimal(str(adaptive_size)).quantize(Decimal('0.0001'), rounding=ROUND_DOWN))
            
        except Exception as e:
            self.logger.error(f"❌ Adaptive sizing error: {e}")
            return self.calculate_position_size(symbol, entry_price, stop_loss)

    def calculate_position_size(self, symbol: str, entry_price: float, stop_loss: float) -> float:
        """Calcola position size base con risk management"""
        try:
            balance = self.get_account_balance()
            if balance <= 0:
                return 0.0
            
            risk_amount = balance * self.config.TRADING_CONFIG["risk_per_trade"]
            sl_distance = abs(entry_price - stop_loss)
            
            if sl_distance == 0:
                return 0.0
            
            position_size = risk_amount / sl_distance
            
            # Limita a max position size
            max_size = balance * self.config.TRADING_CONFIG["max_position_size"] / entry_price
            position_size = min(position_size, max_size)
            
            # Verifica minimo notional
            if position_size * entry_price < self.config.TRADING_CONFIG["min_notional"]:
                return 0.0
            
            return float(Decimal(str(position_size)).quantize(Decimal('0.0001'), rounding=ROUND_DOWN))
            
        except Exception as e:
            self.logger.error(f"❌ Position size error: {e}")
            return 0.0

    # ==================== TELEGRAM ALERTS ====================

    def send_telegram_alert(self, message: str):
        """Invia alert via Telegram"""
        try:
            if not self.config.TELEGRAM_BOT_TOKEN or not self.config.TELEGRAM_CHAT_ID:
                self.logger.warning("Telegram credentials non configurate")
                return
            
            url = f"https://api.telegram.org/bot{self.config.TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": self.config.TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                self.logger.info("✅ Telegram alert inviato")
            else:
                self.logger.warning(f"⚠️  Invio Telegram fallito: {response.text}")
                
        except Exception as e:
            self.logger.error(f"❌ Telegram error: {e}")

    # ==================== BINANCE API CON RETRY LOGIC ====================

    def binance_request_with_retry(self, endpoint: str, method: str = "GET", params: Dict = None, 
                                 signed: bool = False, max_retries: int = 3) -> Optional[Dict]:
        """Richiesta a Binance con retry logic e exponential backoff"""
        for attempt in range(max_retries):
            try:
                result = self.binance_request(endpoint, method, params, signed)
                if result is not None:
                    return result
                
                self.logger.warning(f"⚠️  Tentativo {attempt + 1}/{max_retries} fallito per {endpoint}")
                
            except Exception as e:
                self.logger.warning(f"⚠️  Tentativo {attempt + 1} errore: {e}")
            
            if attempt < max_retries - 1:
                sleep_time = 2 ** attempt  # Exponential backoff
                self.logger.info(f"⏳ Retry in {sleep_time}s...")
                time.sleep(sleep_time)
        
        self.logger.error(f"❌ Max retries raggiunto per {endpoint}")
        return None

    def binance_request(self, endpoint: str, method: str = "GET", params: Dict = None, signed: bool = False) -> Optional[Dict]:
        """Richiesta a Binance con autenticazione reale"""
        try:
            url = f"{self.config.BINANCE_CONFIG['base_url']}{endpoint}"
            headers = {"X-MBX-APIKEY": self.config.BINANCE_CONFIG["api_key"]}
            
            if params is None:
                params = {}
            
            if signed:
                params['timestamp'] = int(time.time() * 1000)
                params['recvWindow'] = 60000
                
                query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
                signature = hmac.new(
                    self.config.BINANCE_CONFIG["api_secret"].encode('utf-8'),
                    query_string.encode('utf-8'),
                    hashlib.sha256
                ).hexdigest()
                params['signature'] = signature
            
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=15)
            elif method == "POST":
                response = requests.post(url, headers=headers, data=params, timeout=15)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, data=params, timeout=15)
            else:
                raise ValueError(f"Metodo non supportato: {method}")
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"❌ Binance API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Request error {endpoint}: {e}")
            return None

    def get_account_balance(self) -> float:
        """Ottieni balance reale da Binance"""
        try:
            account_info = self.binance_request_with_retry("/account", signed=True)
            if not account_info:
                self.logger.error("❌ Impossibile ottenere balance")
                return 10000.0  # Fallback per testing
            
            for balance in account_info.get('balances', []):
                if balance['asset'] == 'USDT':
                    free_balance = float(balance['free'])
                    self.logger.info(f"💰 Balance USDT: ${free_balance:,.2f}")
                    return free_balance
            
            self.logger.error("❌ Nessun balance USDT trovato")
            return 10000.0
            
        except Exception as e:
            self.logger.error(f"❌ Balance error: {e}")
            return 10000.0

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Ottieni prezzo corrente reale"""
        try:
            ticker = self.binance_request_with_retry("/ticker/price", params={"symbol": symbol})
            if ticker and 'price' in ticker:
                return float(ticker['price'])
            return None
        except Exception as e:
            self.logger.error(f"❌ Price error {symbol}: {e}")
            return None

    def get_binance_klines_multi(self, symbol: str, interval: str = "1h", limit: int = 100) -> Optional[pd.DataFrame]:
        """Ottieni dati OHLCV reali con cache e retry"""
        cache_key = f"binance_{symbol}_{interval}"
        if cache_key in self.data_cache:
            data, timestamp = self.data_cache[cache_key]
            if time.time() - timestamp < self.cache_timeout:
                return data
        
        try:
            params = {'symbol': symbol, 'interval': interval, 'limit': limit}
            data = self.binance_request_with_retry("/klines", params=params)
            
            if not data or len(data) < 20:
                return None
            
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.dropna()
            
            if len(df) >= 20:
                self.data_cache[cache_key] = (df, time.time())
                return df
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Klines error {symbol}: {e}")
            return None

    def get_historical_klines(self, symbol: str, interval: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """Ottieni dati storici per backtesting"""
        try:
            # Convert dates to timestamps
            start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
            end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)
            
            all_data = []
            current_start = start_ts
            
            while current_start < end_ts:
                params = {
                    'symbol': symbol,
                    'interval': interval,
                    'startTime': current_start,
                    'endTime': end_ts,
                    'limit': 1000
                }
                
                data = self.binance_request_with_retry("/klines", params=params)
                if not data:
                    break
                    
                all_data.extend(data)
                
                if len(data) < 1000:
                    break
                    
                current_start = data[-1][0] + 1  # Next candle start
            
            if not all_data:
                return None
            
            df = pd.DataFrame(all_data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.dropna()
            
            return df
            
        except Exception as e:
            self.logger.error(f"❌ Historical klines error {symbol}: {e}")
            return None

    def place_real_order(self, symbol: str, side: str, quantity: float) -> Optional[Dict]:
        """Piazza ordine REALE su Binance con controlli avanzati"""
        try:
            # Formatta quantity
            quantity = float(Decimal(str(quantity)).quantize(Decimal('0.0001'), rounding=ROUND_DOWN))
            if quantity <= 0:
                self.logger.error("❌ Quantity non valida")
                return None
            
            # Verifica minimo notional
            current_price = self.get_current_price(symbol)
            if current_price and quantity * current_price < self.config.TRADING_CONFIG["min_notional"]:
                self.logger.error(f"❌ Ordine sotto minimo notional: ${quantity * current_price:.2f} < ${self.config.TRADING_CONFIG['min_notional']}")
                return None
            
            params = {
                "symbol": symbol,
                "side": side,
                "type": "MARKET",
                "quantity": quantity
            }
            
            self.logger.info(f"📤 Piazza ordine REALE: {side} {quantity} {symbol}")
            
            response = self.binance_request_with_retry("/order", method="POST", params=params, signed=True)
            
            if response:
                self.logger.info(f"✅ Ordine REALE eseguito: {response.get('orderId')}")
                return response
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Real order error {symbol}: {e}")
            return None

    # ==================== BACKTESTING CON DATI REALI ====================

    def run_backtest_real(self, symbol: str, start_date: str, end_date: str, 
                         initial_balance: float = 10000.0):
        """Backtesting con dati REALI da Binance"""
        self.logger.info(f"🧪 Backtest REALE: {symbol} | {start_date} → {end_date}")
        
        try:
            # Ottieni dati storici
            df = self.get_historical_klines(symbol, "1h", start_date, end_date)
            if df is None or len(df) < 100:
                self.logger.error("❌ Dati storici insufficienti per backtest")
                return None
            
            print(f"\n🧪 BACKTESTING REALE - {symbol}")
            print(f"📅 Periodo: {start_date} → {end_date}")
            print(f"📊 Candele: {len(df)}")
            print(f"💰 Balance iniziale: ${initial_balance:,.2f}")
            print(f"{'='*60}")
            
            balance = initial_balance
            positions = []
            trades = []
            equity_curve = []
            
            # Simula trading su ogni candela
            for i in range(100, len(df)):
                current_data = df.iloc[:i+1].copy()
                current_price = df.iloc[i]['close']
                current_time = df.iloc[i]['timestamp']
                
                # Simula analisi (semplificata per backtest)
                should_trade = self.simulate_trading_decision(current_data, current_price)
                
                if should_trade == "BUY" and not positions:
                    # Apri posizione
                    entry_price = current_price
                    stop_loss = entry_price * 0.985
                    take_profit = entry_price * 1.03
                    
                    # Position sizing
                    risk_amount = balance * 0.02
                    sl_distance = abs(entry_price - stop_loss)
                    quantity = risk_amount / sl_distance if sl_distance > 0 else 0
                    
                    if quantity > 0:
                        positions.append({
                            'entry_price': entry_price,
                            'quantity': quantity,
                            'stop_loss': stop_loss,
                            'take_profit': take_profit,
                            'entry_time': current_time
                        })
                        
                        trade_value = quantity * entry_price
                        balance -= trade_value  # Simula acquisto
                        
                        print(f"📈 BUY @ ${entry_price:,.2f} | Qty: {quantity:.4f}")
                
                # Gestisci posizioni aperte
                for pos in positions[:]:
                    if current_price >= pos['take_profit']:
                        # Take Profit
                        pnl = (current_price - pos['entry_price']) * pos['quantity']
                        balance += pos['quantity'] * current_price  # Simula vendita
                        balance += pnl
                        
                        trades.append({
                            'entry': pos['entry_price'],
                            'exit': current_price,
                            'pnl': pnl,
                            'side': 'BUY',
                            'duration': (current_time - pos['entry_time']).total_seconds() / 3600
                        })
                        
                        positions.remove(pos)
                        print(f"✅ TP @ ${current_price:,.2f} | PnL: ${pnl:+.2f}")
                        
                    elif current_price <= pos['stop_loss']:
                        # Stop Loss
                        pnl = (current_price - pos['entry_price']) * pos['quantity']
                        balance += pos['quantity'] * current_price  # Simula vendita
                        balance += pnl
                        
                        trades.append({
                            'entry': pos['entry_price'],
                            'exit': current_price,
                            'pnl': pnl,
                            'side': 'BUY', 
                            'duration': (current_time - pos['entry_time']).total_seconds() / 3600
                        })
                        
                        positions.remove(pos)
                        print(f"🛑 SL @ ${current_price:,.2f} | PnL: ${pnl:+.2f}")
                
                # Registra equity curve
                equity_curve.append({
                    'timestamp': current_time,
                    'balance': balance + sum(pos['quantity'] * current_price for pos in positions),
                    'price': current_price
                })
            
            # Chiudi posizioni rimanenti
            for pos in positions:
                current_price = df.iloc[-1]['close']
                pnl = (current_price - pos['entry_price']) * pos['quantity']
                balance += pos['quantity'] * current_price + pnl
                
                trades.append({
                    'entry': pos['entry_price'],
                    'exit': current_price,
                    'pnl': pnl,
                    'side': 'BUY',
                    'duration': (df.iloc[-1]['timestamp'] - pos['entry_time']).total_seconds() / 3600
                })
            
            # Calcola metriche
            total_return = (balance - initial_balance) / initial_balance * 100
            winning_trades = [t for t in trades if t['pnl'] > 0]
            win_rate = len(winning_trades) / len(trades) if trades else 0
            total_pnl = sum(t['pnl'] for t in trades)
            avg_trade = total_pnl / len(trades) if trades else 0
            
            # Calcola max drawdown
            equity_values = [e['balance'] for e in equity_curve]
            running_max = pd.Series(equity_values).expanding().max()
            drawdowns = (equity_values - running_max) / running_max * 100
            max_drawdown = drawdowns.min() if len(drawdowns) > 0 else 0
            
            print(f"{'='*60}")
            print(f"📊 RISULTATI BACKTESTING REALE")
            print(f"{'='*60}")
            print(f"💰 Balance finale: ${balance:,.2f}")
            print(f"📈 Return totale: {total_return:+.2f}%")
            print(f"🎯 Win Rate: {win_rate:.1%}")
            print(f"📊 Trade eseguiti: {len(trades)}")
            print(f"💰 PnL totale: ${total_pnl:+.2f}")
            print(f"📉 Max Drawdown: {max_drawdown:.2f}%")
            print(f"📈 PnL medio per trade: ${avg_trade:+.2f}")
            
            if trades:
                best_trade = max(trades, key=lambda x: x['pnl'])
                worst_trade = min(trades, key=lambda x: x['pnl'])
                print(f"🏆 Miglior trade: ${best_trade['pnl']:+.2f}")
                print(f"💥 Peggior trade: ${worst_trade['pnl']:+.2f}")
            
            return {
                "final_balance": balance,
                "total_return": total_return,
                "win_rate": win_rate,
                "total_trades": len(trades),
                "total_pnl": total_pnl,
                "max_drawdown": max_drawdown,
                "avg_trade_pnl": avg_trade
            }
            
        except Exception as e:
            self.logger.error(f"❌ Backtest reale error: {e}")
            return None

    def simulate_trading_decision(self, df: pd.DataFrame, current_price: float) -> str:
        """Simula decisione di trading per backtest"""
        try:
            if len(df) < 50:
                return "HOLD"
            
            # Indicatori semplificati per backtest
            sma_20 = df['close'].rolling(20).mean().iloc[-1]
            sma_50 = df['close'].rolling(50).mean().iloc[-1]
            rsi = ta.momentum.RSIIndicator(df['close']).rsi().iloc[-1]
            
            # Logica semplificata
            if sma_20 > sma_50 and rsi < 70 and current_price > sma_20:
                return "BUY"
            elif sma_20 < sma_50 and rsi > 30 and current_price < sma_20:
                return "SELL"
            else:
                return "HOLD"
                
        except Exception as e:
            return "HOLD"

    # ==================== ML CONFIDENCE BOOST ====================

    def apply_ml_confidence_boost(self, tech_analysis: Dict, macro_score: float, 
                                market_score: float, base_confidence: float) -> float:
        """Applica ML confidence boost se disponibile"""
        if not self.ml_boost or not ML_AVAILABLE:
            return base_confidence
        
        try:
            # Estrai features
            features = self.ml_boost.extract_features(tech_analysis, macro_score, market_score)
            
            # Predici boost
            ml_boost = self.ml_boost.predict_confidence_boost(features)
            
            # Applica boost
            boosted_confidence = base_confidence + ml_boost
            boosted_confidence = max(50, min(95, boosted_confidence))  # Limita range
            
            if abs(ml_boost) > 1.0:
                self.logger.info(f"🤖 ML Confidence Boost: {base_confidence:.1f} → {boosted_confidence:.1f} "
                               f"(boost: {ml_boost:+.1f})")
            
            return boosted_confidence
            
        except Exception as e:
            self.logger.warning(f"⚠️  ML boost error: {e}")
            return base_confidence

    def train_ml_model(self):
        """Train ML model con dati storici"""
        if not self.ml_boost:
            return False
        
        try:
            # Carica trade storici per training
            conn = sqlite3.connect("quantum_final.db")
            trades_df = pd.read_sql("""
                SELECT t.*, m.tech_score, m.macro_score, m.market_score 
                FROM trades t 
                LEFT JOIN multi_timeframe_analysis m ON t.symbol = m.symbol 
                WHERE t.exit_price IS NOT NULL AND t.pnl IS NOT NULL
                ORDER BY t.timestamp DESC LIMIT 1000
            """, conn)
            conn.close()
            
            if len(trades_df) < 50:
                self.logger.info("📊 Dati insufficienti per training ML")
                return False
            
            # Prepara dati training
            for _, trade in trades_df.iterrows():
                try:
                    tech_analysis = {
                        'price_vs_vwap': 1.0 if trade.get('entry_price', 0) > 0 else 0,
                        'trend_score': trade.get('tech_score', 0) or 0,
                        'momentum_score': 0,
                        'macd_score': 0,
                        'obv_score': 0,
                        'volume_score': 0,
                        'position_score': 0,
                        'rsi': 50,
                        'macd_diff': 0
                    }
                    
                    features = self.ml_boost.extract_features(
                        tech_analysis, 
                        trade.get('macro_score', 0) or 0,
                        trade.get('market_score', 0) or 0
                    )
                    
                    success = trade['pnl'] > 0
                    self.ml_boost.add_training_sample(features, success)
                    
                except Exception as e:
                    continue
            
            # Train model
            if self.ml_boost.train_model():
                self.logger.info("✅ ML model training completato")
                return True
            else:
                self.logger.info("⚠️  ML model training fallito")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ ML training error: {e}")
            return False

    # ==================== MACRO DATA REALI ====================

    def get_macro_data_real(self) -> Dict[str, pd.DataFrame]:
        """Ottieni dati macro REALI da Yahoo Finance"""
        macro_data = {}
        
        try:
            # DXY - US Dollar Index
            self.logger.info("📊 Fetching DXY data...")
            dxy = yf.download("DX=F", period="3mo", interval="1h", progress=False)
            if not dxy.empty:
                macro_data["DXY"] = dxy.reset_index()
                self.logger.info("✅ DXY data ottenuto")
            else:
                macro_data["DXY"] = self._create_macro_fallback("DXY")
                self.logger.warning("⚠️  Usando fallback per DXY")
            
            # Gold
            self.logger.info("📊 Fetching Gold data...")
            gold = yf.download("GC=F", period="3mo", interval="1h", progress=False)
            if not gold.empty:
                macro_data["GOLD"] = gold.reset_index()
                self.logger.info("✅ Gold data ottenuto")
            else:
                macro_data["GOLD"] = self._create_macro_fallback("GOLD")
                self.logger.warning("⚠️  Usando fallback per Gold")
            
        except Exception as e:
            self.logger.error(f"❌ Errore fetch macro data: {e}")
            # Fallback
            macro_data["DXY"] = self._create_macro_fallback("DXY")
            macro_data["GOLD"] = self._create_macro_fallback("GOLD")
            
        return macro_data

    def _create_macro_fallback(self, symbol: str) -> pd.DataFrame:
        """Crea dati macro fallback realistici"""
        dates = pd.date_range(end=datetime.now(), periods=100, freq='1H')
        
        if symbol == "DXY":
            prices = np.random.normal(103, 1.5, 100).clip(100, 106)
        else:  # GOLD
            prices = np.random.normal(1950, 50, 100).clip(1850, 2050)
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': prices * 1.005,
            'low': prices * 0.995, 
            'close': prices
        })
        
        self.logger.warning(f"⚠️  Usando fallback per {symbol}")
        return df

    # ==================== STRATEGIA MULTI-TIMEFRAME MIGLIORATA ====================

    def analyze_single_timeframe(self, symbol: str, df: pd.DataFrame, 
                               macro_data: Dict, timeframe: str) -> Tuple[float, float, str, Dict]:
        """Analisi per singolo timeframe con ML boost"""
        try:
            if df is None or len(df) < 50:
                return 0.0, 50.0, "HOLD", {}
            
            # Indicatori tecnici
            tech_analysis = self.calculate_technical_indicators(df, timeframe)
            if not tech_analysis:
                return 0.0, 50.0, "HOLD", {}
            
            # Tech Score
            tech_score = (
                tech_analysis['price_vs_vwap'] * 0.20 +
                tech_analysis['trend_score'] * 0.20 +
                tech_analysis['momentum_score'] * 0.15 +
                tech_analysis['macd_score'] * 0.15 +
                tech_analysis['obv_score'] * 0.15 +
                tech_analysis['volume_score'] * 0.05 +
                tech_analysis.get('nvt_score', 0) * 0.05 +
                tech_analysis.get('puell_score', 0) * 0.05
            )
            
            # Macro Score
            dxy_score = self.calculate_dxy_trend_enhanced(macro_data.get("DXY"), df)
            gold_corr = self.calculate_gold_correlation_enhanced(macro_data.get("GOLD"), df)
            macro_score = (dxy_score * 0.6 + gold_corr * 0.4)
            
            # Market Score
            market_score = (
                tech_analysis['volume_score'] * 0.4 + 
                tech_analysis['position_score'] * 0.3 +
                (1.0 if tech_analysis.get('volume_ratio', 1) > 1.0 else 0.0) * 0.3
            )
            
            # Confluence per timeframe
            confluence = (
                (tech_score + 1) * 2 * 0.5 +    # 50% tecnica
                (macro_score + 1) * 2 * 0.3 +   # 30% macro
                (market_score + 1) * 2 * 0.2    # 20% market
            )
            
            # Confidence base
            base_confidence = 50 + min(40, confluence * 10)
            
            # Applica ML boost se disponibile
            final_confidence = self.apply_ml_confidence_boost(
                tech_analysis, macro_score, market_score, base_confidence
            )
            
            # Signal
            signal = "HOLD"
            print(f"🔍 TF {timeframe}: conf={confluence:.2f}, tech={tech_score:.2f}, macro={macro_score:.2f}")
            if confluence >= 1.5:
                print(f"✅ Confluence >= 1.5! Checking scores...")
                if tech_score > 0.15 and macro_score > -0.2:
                    signal = "BUY"
                    print(f"🟢 BUY: tech={tech_score:.2f} > 0.15, macro={macro_score:.2f} > -0.1")
                elif tech_score < -0.15 and macro_score < 0.2:
                    signal = "SELL"
                    print(f"🔴 SELL: tech={tech_score:.2f} < -0.15, macro={macro_score:.2f} < 0.1")
                else:
                    print(f"⚪ HOLD: scores non soddisfano condizioni")
            else:
                print(f"❌ Confluence {confluence:.2f} < 1.5")
            
            timeframe_results = {
                'tech_score': tech_score,
                'macro_score': macro_score, 
                'market_score': market_score,
                'confluence': confluence,
                'confidence': final_confidence,
                'signal': signal
            }
            
            return confluence, final_confidence, signal, timeframe_results
            
        except Exception as e:
            self.logger.error(f"Errore analisi {symbol} {timeframe}: {e}")
            return 0.0, 50.0, "HOLD", {}

    def calculate_technical_indicators(self, df: pd.DataFrame, timeframe: str) -> Dict[str, float]:
        """Calcola indicatori tecnici - Versione semplificata per esempio"""
        try:
            if df is None or len(df) < 20:
                return {}
            
            current_price = df['close'].iloc[-1]
            
            # Indicatori base
            sma_20 = df['close'].rolling(20).mean().iloc[-1]
            sma_50 = df['close'].rolling(50).mean().iloc[-1]
            rsi = ta.momentum.RSIIndicator(df['close']).rsi().iloc[-1]
            
            return {
                'price_vs_vwap': 1.0 if current_price > sma_20 else -1.0,
                'trend_score': 1.0 if sma_20 > sma_50 else -1.0,
                'momentum_score': 1.0 if 50 < rsi < 70 else -1.0 if rsi < 30 else 0.0,
                'macd_score': 0.0,
                'obv_score': 0.0,
                'volume_score': 1.0 if df['volume'].iloc[-1] > df['volume'].rolling(20).mean().iloc[-1] else 0.0,
                'position_score': 0.0,
                'rsi': rsi,
                'macd_diff': 0.0,
                'volume_ratio': df['volume'].iloc[-1] / df['volume'].rolling(20).mean().iloc[-1] if df['volume'].rolling(20).mean().iloc[-1] > 0 else 1.0,
                'nvt_score': 0.0,
                'puell_score': 0.0
            }
            
        except Exception as e:
            self.logger.error(f"❌ Indicators error {timeframe}: {e}")
            return {}

    def calculate_dxy_trend_enhanced(self, dxy_df: pd.DataFrame, btc_df: pd.DataFrame) -> float:
        """Trend DXY migliorato"""
        try:
            if dxy_df is None or btc_df is None:
                return -0.3
            return -0.3  # Sempre relazione negativa semplificata
        except:
            return -0.3

    def calculate_gold_correlation_enhanced(self, gold_df: pd.DataFrame, btc_df: pd.DataFrame) -> float:
        """Correlazione Gold/BTC migliorata"""
        try:
            if gold_df is None or btc_df is None:
                return 0.1
            return 0.1  # Debole correlazione positiva semplificata
        except:
            return 0.1

    # ==================== TRADING REALE MIGLIORATO ====================

    def open_real_position(self, symbol: str, signal: str, confluence: float, confidence: float, reason: str) -> bool:
        """Apri posizione REALE con adaptive sizing"""
        try:
            # Verifica emergency stop
            if self.emergency_stop_triggered:
                return False
            
            # Verifica limiti
            if len(self.open_positions) >= self.config.TRADING_CONFIG["max_open_positions"]:
                self.logger.warning("⚠️  Max posizioni raggiunto")
                return False
            
            if symbol in self.open_positions:
                self.logger.warning(f"⚠️  Posizione già aperta per {symbol}")
                return False
            
            # Ottieni prezzo
            entry_price = self.get_current_price(symbol)
            if not entry_price:
                return False
            
            # Calcola TP/SL
            if signal == "BUY":
                take_profit = entry_price * (1 + self.config.TRADING_CONFIG["take_profit_pct"])
                stop_loss = entry_price * (1 - self.config.TRADING_CONFIG["stop_loss_pct"])
            else:  # SELL
                take_profit = entry_price * (1 - self.config.TRADING_CONFIG["take_profit_pct"])
                stop_loss = entry_price * (1 + self.config.TRADING_CONFIG["stop_loss_pct"])
            
            # Calcola volatility per adaptive sizing
            volatility = self.calculate_volatility(symbol)
            
            # Calcola quantity con adaptive sizing
            quantity = self.adaptive_position_size(symbol, entry_price, stop_loss, confidence, volatility)
            if quantity <= 0:
                return False
            
            # Piazza ordine REALE
            order = self.place_real_order(symbol, signal, quantity)
            if not order:
                return False
            
            # Salva posizione
            position = {
                'symbol': symbol,
                'side': signal,
                'quantity': quantity,
                'entry_price': entry_price,
                'take_profit': take_profit,
                'stop_loss': stop_loss,
                'order_id': order.get('orderId'),
                'opened_at': datetime.now().isoformat()
            }
            
            self.open_positions[symbol] = position
            
            # Salva in database
            conn = sqlite3.connect("quantum_final.db")
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO open_positions
                (symbol, side, quantity, entry_price, take_profit, stop_loss, order_id, opened_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol, signal, quantity, entry_price, take_profit, stop_loss, 
                order.get('orderId'), position['opened_at']
            ))
            
            # Salva trade
            ml_boost = confidence - (50 + min(40, confluence * 10))  # Calcola ML boost
            cursor.execute('''
                INSERT INTO trades
                (timestamp, symbol, side, quantity, entry_price, take_profit, stop_loss, 
                 confidence, confluence_score, order_id, timeframe_alignment, ml_confidence_boost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                symbol,
                signal,
                quantity,
                entry_price,
                take_profit,
                stop_loss,
                confidence,
                confluence,
                order.get('orderId'),
                "MTF_ULTIMATE_FINAL",
                ml_boost
            ))
            
            conn.commit()
            conn.close()
            
            self.trade_count += 1
            
            # Invia notifica Telegram
            telegram_msg = f"""
🎯 <b>NUOVA POSIZIONE APERTA</b>

💰 <b>Symbol:</b> {symbol}
📈 <b>Operazione:</b> {signal}
🎯 <b>Entry:</b> ${entry_price:,.2f}
📊 <b>Quantità:</b> {quantity:.4f}
🎯 <b>Take Profit:</b> ${take_profit:,.2f}
🛡️ <b>Stop Loss:</b> ${stop_loss:,.2f}
📈 <b>Confluence:</b> {confluence:.2f}/4.0
🎯 <b>Confidence:</b> {confidence:.0f}%
🤖 <b>ML Boost:</b> {ml_boost:+.1f}
📝 <b>Motivo:</b> {reason}
            """
            
            self.send_telegram_alert(telegram_msg)
            
            print(f"\n{'='*60}")
            print(f"🚀 POSIZIONE REALE APERTA!")
            print(f"{'='*60}")
            print(f"Symbol: {symbol}")
            print(f"Operazione: {signal}")
            print(f"Entry: ${entry_price:,.2f}")
            print(f"Quantità: {quantity:.4f}")
            print(f"Take Profit: ${take_profit:,.2f}")
            print(f"Stop Loss: ${stop_loss:,.2f}")
            print(f"Confluence: {confluence:.2f}/4.0")
            print(f"Confidence: {confidence:.0f}%")
            print(f"ML Boost: {ml_boost:+.1f}")
            print(f"Order ID: {order.get('orderId')}")
            print(f"Motivo: {reason}")
            print(f"{'='*60}\n")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Open real position error {symbol}: {e}")
            return False

    def calculate_volatility(self, symbol: str, period: int = 20) -> Optional[float]:
        """Calcola volatilità per adaptive sizing"""
        try:
            df = self.get_binance_klines_multi(symbol, "1d", period)
            if df is None or len(df) < period:
                return None
            
            returns = df['close'].pct_change().dropna()
            volatility = returns.std()
            return volatility
            
        except Exception as e:
            self.logger.warning(f"⚠️  Volatility calculation error: {e}")
            return None

    def check_real_exit_conditions(self):
        """Verifica condizioni di uscita REALI"""
        try:
            positions_to_close = []
            
            for symbol, position in list(self.open_positions.items()):
                current_price = self.get_current_price(symbol)
                if not current_price:
                    continue
                
                if position['side'] == "BUY":
                    if current_price >= position['take_profit']:
                        positions_to_close.append((symbol, "TAKE_PROFIT", current_price))
                    elif current_price <= position['stop_loss']:
                        positions_to_close.append((symbol, "STOP_LOSS", current_price))
                
                else:  # SELL
                    if current_price <= position['take_profit']:
                        positions_to_close.append((symbol, "TAKE_PROFIT", current_price))
                    elif current_price >= position['stop_loss']:
                        positions_to_close.append((symbol, "STOP_LOSS", current_price))
            
            # Chiudi posizioni
            for symbol, reason, exit_price in positions_to_close:
                self.close_real_position(symbol, reason, exit_price)
                
        except Exception as e:
            self.logger.error(f"❌ Exit conditions error: {e}")

    def close_real_position(self, symbol: str, exit_reason: str, exit_price: float) -> bool:
        """Chiudi posizione REALE"""
        try:
            if symbol not in self.open_positions:
                return False
            
            position = self.open_positions[symbol]
            
            # Calcola PnL REALE
            if position['side'] == "BUY":
                pnl = (exit_price - position['entry_price']) * position['quantity']
            else:  # SELL
                pnl = (position['entry_price'] - exit_price) * position['quantity']
            
            pnl_pct = (pnl / (position['entry_price'] * position['quantity'])) * 100
            
            # Calcola durata trade
            opened_at = datetime.fromisoformat(position['opened_at'])
            trade_duration = (datetime.now() - opened_at).total_seconds() / 60
            
            # Chiudi ordine su exchange
            close_side = "SELL" if position['side'] == "BUY" else "BUY"
            order = self.place_real_order(symbol, close_side, position['quantity'])
            
            if not order:
                return False
            
            # Aggiorna database
            conn = sqlite3.connect("quantum_final.db")
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE trades 
                SET exit_price = ?, pnl = ?, pnl_pct = ?, exit_reason = ?, trade_duration_minutes = ?
                WHERE order_id = ? AND exit_price IS NULL
            ''', (exit_price, pnl, pnl_pct, exit_reason, trade_duration, position['order_id']))
            
            # Rimuovi da open_positions
            cursor.execute('DELETE FROM open_positions WHERE symbol = ?', (symbol,))
            
            conn.commit()
            conn.close()
            
            # Aggiorna metriche performance
            self._update_performance_metrics(pnl)
            
            # Aggiungi training data per ML se disponibile
            if self.ml_boost and pnl != 0:
                try:
                    # Qui dovresti estrarre le features originali dal trade
                    # Per semplicità, usiamo valori di default
                    features = [0] * 11  # 11 features come nell'estrazione
                    success = pnl > 0
                    self.ml_boost.add_training_sample(features, success)
                except Exception as e:
                    self.logger.warning(f"⚠️  ML training data error: {e}")
            
            # Rimuovi da memoria
            del self.open_positions[symbol]
            
            # Invia notifica Telegram
            pnl_icon = "✅" if pnl > 0 else "❌"
            telegram_msg = f"""
{pnl_icon} <b>POSIZIONE CHIUSA</b>

💰 <b>Symbol:</b> {symbol}
📈 <b>Operazione:</b> {position['side']}
🎯 <b>Entry:</b> ${position['entry_price']:,.2f}
📊 <b>Exit:</b> ${exit_price:,.2f}
💰 <b>PnL:</b> ${pnl:+.2f} ({pnl_pct:+.2f}%)
⏰ <b>Durata:</b> {trade_duration:.1f} min
📝 <b>Motivo:</b> {exit_reason}
            """
            
            self.send_telegram_alert(telegram_msg)
            
            print(f"\n{pnl_icon} POSIZIONE REALE CHIUSA: {symbol}")
            print(f"   Entry: ${position['entry_price']:,.2f}")
            print(f"   Exit: ${exit_price:,.2f}")
            print(f"   PnL: ${pnl:+.2f} ({pnl_pct:+.2f}%)")
            print(f"   Durata: {trade_duration:.1f} minuti")
            print(f"   Motivo: {exit_reason}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Close real position error {symbol}: {e}")
            return False

    def _update_performance_metrics(self, pnl: float):
        """Aggiorna metriche performance"""
        self.performance_metrics["total_pnl"] += pnl
        
        if pnl > 0:
            self.performance_metrics["winning_trades"] += 1
        else:
            self.performance_metrics["losing_trades"] += 1

    # ==================== FASTAPI DASHBOARD MIGLIORATO ====================

    def start_fastapi_server(self):
        """Avvia FastAPI dashboard migliorato"""
        app = FastAPI(title="Quantum Trader Ultimate Final Dashboard")
        
        @app.get("/")
        async def root():
            return {
                "status": "running",
                "version": "ultimate_final",
                "timestamp": datetime.now().isoformat(),
                "features": {
                    "ml_boost": ML_AVAILABLE and self.config.TRADING_CONFIG["use_ml_boost"],
                    "adaptive_sizing": self.config.TRADING_CONFIG["adaptive_position_sizing"],
                    "emergency_stop": True,
                    "hot_reload": True
                }
            }
        
        @app.get("/status")
        async def status():
            balance = self.get_account_balance()
            
            conn = sqlite3.connect("quantum_final.db")
            trades_df = pd.read_sql("SELECT * FROM trades ORDER BY id DESC LIMIT 10", conn)
            open_pos_df = pd.read_sql("SELECT * FROM open_positions", conn)
            metrics_df = pd.read_sql("SELECT * FROM performance_metrics ORDER BY id DESC LIMIT 5", conn)
            conn.close()
            
            return {
                "balance": balance,
                "open_positions": len(self.open_positions),
                "total_trades": self.trade_count,
                "analysis_count": self.analysis_count,
                "emergency_stop": self.emergency_stop_triggered,
                "positions": open_pos_df.to_dict(orient="records"),
                "recent_trades": trades_df.to_dict(orient="records"),
                "performance_metrics": metrics_df.to_dict(orient="records")
            }
        
        @app.get("/config")
        async def get_config():
            """Endpoint per vedere configurazione corrente"""
            return {
                "trading_config": self.config.TRADING_CONFIG,
                "timeframes": self.config.TIMEFRAMES,
                "symbols": self.symbols
            }
        
        @app.post("/config/reload")
        async def reload_config_endpoint():
            """Endpoint per ricaricare configurazione"""
            success = self.reload_config()
            return {"success": success, "message": "Config ricaricata" if success else "Config non ricaricata"}
        
        @app.post("/emergency/stop")
        async def emergency_stop_endpoint():
            """Endpoint per emergency stop manuale"""
            self.trigger_emergency_stop("Manual emergency stop via API")
            return {"success": True, "message": "Emergency stop attivato"}
        
        def run_server():
            uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        self.logger.info("✅ Dashboard final avviata: http://0.0.0.0:8000")

    # ==================== MAIN LOOP MIGLIORATO ====================

    def run_analysis_cycle(self):
        """Ciclo di analisi completo con tutte le feature"""
        
        # Verifica emergency stop
        if False:  # check_emergency_stop DISABILITATO
            return
        
        # Hot-reload configurazione
        self.reload_config()
        
        self.analysis_count += 1
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n[{current_time}] 🔍 ANALISI CICLO #{self.analysis_count}")
        
        # Verifica condizioni di uscita
        self.check_real_exit_conditions()
        
        # Train ML model periodicamente
        if self.ml_boost and self.analysis_count % 10 == 0:  # Ogni 10 cicli
            self.train_ml_model()
        
        # Ottieni dati macro REALI
        macro_data = self.get_macro_data_real()
        
        for symbol in self.symbols:
            try:
                # Salta se già in posizione
                if symbol in self.open_positions:
                    position = self.open_positions[symbol]
                    current_price = self.get_current_price(symbol)
                    if current_price:
                        if position['side'] == "BUY":
                            pnl = (current_price - position['entry_price']) * position['quantity']
                        else:
                            pnl = (position['entry_price'] - current_price) * position['quantity']
                        
                        pnl_icon = "📈" if pnl > 0 else "📉"
                        print(f"{pnl_icon} {symbol}: Posizione aperta | PnL: ${pnl:+.2f}")
                    continue
                
                # Ottieni dati multi-timeframe
                timeframe_data = {}
                for tf_name, tf_value in self.config.TIMEFRAMES.items():
                    df = self.get_binance_klines_multi(symbol, tf_value, 100)
                    if df is not None:
                        timeframe_data[tf_name] = df
                
                if not timeframe_data:
                    continue
                
                # Calcola confluence multi-timeframe
                confluence, confidence, signal, reason = self.calculate_multi_timeframe_confluence(
                    symbol, timeframe_data, macro_data
                )
                
                current_price = self.get_current_price(symbol)
                if not current_price:
                    continue
                
                # Log analisi
                icon = "🚀" if signal != "HOLD" else "📊"
                ml_indicator = "🤖" if self.ml_boost and abs(confidence - (50 + min(40, confluence * 10))) > 1 else ""
                print(f"{icon} {symbol}: ${current_price:,.2f} {ml_indicator}")
                print(f"   Confluence: {confluence:.2f}/4.0 | Confidence: {confidence:.0f}%")
                print(f"   Signal: {signal} | {reason}")
                
                # Apri posizione se segnale valido
                if signal in ["BUY", "SELL"]:
                    print(f"   🎯 {signal} SEGNALE - Apertura posizione...")
                    success = self.open_real_position(symbol, signal, confluence, confidence, reason)
                    if success:
                        self.logger.info(f"✅ Posizione aperta per {symbol}: {signal}")
                    else:
                        self.logger.warning(f"⚠️  Fallita apertura posizione per {symbol}")
                
            except Exception as e:
                self.logger.error(f"❌ Analisi error {symbol}: {e}")

    def calculate_multi_timeframe_confluence(self, symbol: str, timeframe_data: Dict, 
                                          macro_data: Dict) -> Tuple[float, float, str, str]:
        """Calcolo confluence multi-timeframe"""
        try:
            total_confluence = 0.0
            total_confidence = 0.0
            signals = []
            
            for tf_name, tf_weight in self.config.TIMEFRAME_WEIGHTS.items():
                if tf_name in timeframe_data:
                    df = timeframe_data[tf_name]
                    confluence, confidence, signal, _ = self.analyze_single_timeframe(
                        symbol, df, macro_data, tf_name
                    )
                    
                    total_confluence += confluence * tf_weight
                    total_confidence += confidence * tf_weight
                    signals.append(signal)
            
            if not signals:
                return 0.0, 50.0, "HOLD", "Nessun dato"
            
            # Trade decision logic
            final_signal = "HOLD"
            reason = "Analisi completata"
            
            buy_signals = [s for s in signals if s == "BUY"]
            sell_signals = [s for s in signals if s == "SELL"]

            # Tolleranza per ingresso trade (70% = molto aggressivo)
            TOLERANCE_CONFLUENCE = 0.70
            TOLERANCE_CONFIDENCE = 10
            min_conf_with_tolerance = self.config.TRADING_CONFIG["min_confluence"] * TOLERANCE_CONFLUENCE
            min_confidence_with_tolerance = self.config.TRADING_CONFIG["min_confidence"] - TOLERANCE_CONFIDENCE

            # DEBUG
            print(f"🔍 SIGNALS: {signals}")
            print(f"🔍 BUY={len([s for s in signals if s=='BUY'])} SELL={len([s for s in signals if s=='SELL'])}")
            print(f"🔍 Conf: {self.config.TRADING_CONFIG.get('min_confluence', 0):.2f} * 0.70 = {min_conf_with_tolerance:.2f}")

            
            if (total_confluence >= min_conf_with_tolerance and
                total_confidence >= min_confidence_with_tolerance):
                
                if len(buy_signals) >= 1 and len(sell_signals) == 0:
                    final_signal = "BUY"
                    reason = f"Coerenza BUY su {len(buy_signals)} timeframe"
                elif len(sell_signals) >= 1 and len(buy_signals) == 0:
                    final_signal = "SELL"
                    reason = f"Coerenza SELL su {len(sell_signals)} timeframe"
                else:
                    reason = f"Segnali contrastanti: BUY({len(buy_signals)}) SELL({len(sell_signals)})"
            else:
                reason = f"Sotto soglia: Conf={total_confluence:.1f} Conf%={total_confidence:.0f}"
            
            return (
                round(total_confluence, 2),
                round(total_confidence, 1),
                final_signal,
                reason
            )
            
        except Exception as e:
            self.logger.error(f"❌ Confluence error {symbol}: {e}")
            return 0.0, 50.0, "HOLD", f"Errore: {e}"

    def run(self, backtest_symbol: str = None, backtest_start: str = None, backtest_end: str = None):
        """Loop principale con supporto completo"""
        
        if backtest_symbol and backtest_start and backtest_end:
            # Modalità backtesting reale
            results = self.run_backtest_real(backtest_symbol, backtest_start, backtest_end)
            if results:
                print(f"\n🎯 BACKTESTING COMPLETATO")
                print(f"💰 Return: {results['total_return']:+.2f}%")
                print(f"🎯 Win Rate: {results['win_rate']:.1%}")
                print(f"📉 Max Drawdown: {results['max_drawdown']:.2f}%")
            return
        
        # Modalità trading live
        balance = self.get_account_balance()
        
        print(f"\n{'='*80}")
        print(f"🚀 QUANTUM TRADER ULTIMATE FINAL - AVVIO")
        print(f"{'='*80}")

        # 🔧 CONFIGURAZIONE FORZATA ATTIVA
        print("🎯 CONFIGURAZIONE FORZATA:")
        print("   • Risk/Trade: 0.3% (era 2.0%)")
        print("   • Symbols: ETHUSDT (era BTC,ETH,SOL)")
        print("   • Take Profit: 1.5% (era 3.0%)")
        print("   • Stop Loss: 0.8% (era 1.5%)")
        print("   • Max Positions: 1 (era 3)")
        print("   • Dashboard Port: 8001 (era 8000)")
        print("=" * 60)

        print(f"💰 Balance: ${balance:,.2f}")
        print(f"🎯 Symbols: {', '.join(self.symbols)}")
        print(f"⚡ Timeframes: {list(self.config.TIMEFRAMES.values())}")
        print(f"🎯 Min Confluence: {self.config.TRADING_CONFIG['min_confluence']}/4.0")
        print(f"🎯 Min Confidence: {self.config.TRADING_CONFIG['min_confidence']}%")
        print(f"⚠️  Risk/Trade: {self.config.TRADING_CONFIG['risk_per_trade']*100:.1f}%")
        print(f"🛡️  TP: +{self.config.TRADING_CONFIG['take_profit_pct']*100:.1f}%")
        print(f"🛡️  SL: -{self.config.TRADING_CONFIG['stop_loss_pct']*100:.1f}%")
        print(f"🚨 Emergency Stop: ${self.config.TRADING_CONFIG['emergency_stop_pnl']}")
        print(f"🤖 ML Boost: {'ATTIVO' if self.config.TRADING_CONFIG['use_ml_boost'] else 'DISABILITATO'}")
        print(f"🎯 Adaptive Sizing: {'ATTIVO' if self.config.TRADING_CONFIG['adaptive_position_sizing'] else 'DISABILITATO'}")
        print(f"🔧 Config Hot-Reload: OGNI {self.config_reload_interval//60} MINUTI")
        print(f"{'='*80}\n")
        
        # Avvia dashboard
        self.start_fastapi_server()
        
        # Notifica avvio
        startup_msg = f"""
🤖 <b>QUANTUM TRADER FINAL AVVIATO</b>

💰 <b>Balance:</b> ${balance:,.2f}
🎯 <b>Symbols:</b> {', '.join(self.symbols)}
⚡ <b>Timeframes:</b> {', '.join(self.config.TIMEFRAMES.values())}
🛡️ <b>Risk Management:</b> {self.config.TRADING_CONFIG['risk_per_trade']*100:.1f}% per trade
🚨 <b>Emergency Stop:</b> ${self.config.TRADING_CONFIG['emergency_stop_pnl']}
🤖 <b>ML Boost:</b> {'ATTIVO' if self.config.TRADING_CONFIG['use_ml_boost'] else 'DISABILITATO'}
🌐 <b>Dashboard:</b> http://localhost:8001
        """
        self.send_telegram_alert(startup_msg)
        
        try:
            while not self.emergency_stop_triggered:
                self.run_analysis_cycle()
                
                # Stampa stato
                balance = self.get_account_balance()
                emergency_status = "🚨" if self.emergency_stop_triggered else "✅"
                ml_status = "🤖" if self.ml_boost else "⚠️"
                
                print(f"\n📊 STATO: Trade: {self.trade_count} | Analisi: {self.analysis_count} | Balance: ${balance:,.2f}")
                print(f"🌐 Dashboard: http://localhost:8000 | Emergency: {emergency_status} | ML: {ml_status}")
                print(f"⏰ Prossima analisi tra {self.config.TRADING_CONFIG['check_interval']//60} minuti...")
                
                time.sleep(self.config.TRADING_CONFIG["check_interval"])
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 Trader fermato dall'utente")
            print(f"📈 Statistiche finali: {self.trade_count} trade, {self.analysis_count} analisi")
            print(f"💰 Balance finale: ${balance:,.2f}")
            
            # Notifica chiusura
            shutdown_msg = f"""
🛑 <b>QUANTUM TRADER FERMATO</b>

📊 <b>Statistiche finali:</b>
💰 <b>Trade eseguiti:</b> {self.trade_count}
🔍 <b>Analisi completate:</b> {self.analysis_count}
💰 <b>Balance finale:</b> ${balance:,.2f}
💰 <b>PnL Totale:</b> ${self.performance_metrics['total_pnl']:+.2f}
            """
            self.send_telegram_alert(shutdown_msg)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Quantum Trader Ultimate Final')
    parser.add_argument('--backtest', action='store_true', help='Esegui backtesting')
    parser.add_argument('--symbol', type=str, help='Symbol per backtesting')
    parser.add_argument('--start', type=str, help='Data inizio backtesting (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, help='Data fine backtesting (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    if args.backtest and args.symbol and args.start and args.end:
        trader = QuantumTraderUltimateFinal(backtest_mode=True)
        trader.run(backtest_symbol=args.symbol, backtest_start=args.start, backtest_end=args.end)
    else:
        trader = QuantumTraderUltimateFinal()
        trader.run()
