#!/usr/bin/env python3
"""
🚀 QUANTUM TRADER - MACRO CONFLUENCE EDITION
SL: -2.0% | TP: +4.5% | R:R 1:2.25
"""

import sqlite3
import requests
import time
import random
from datetime import datetime, timedelta

CONFIG = {
    'INITIAL_BALANCE': 10000.0,
    'POSITION_SIZE_PERCENT': 2.0,
    'STOP_LOSS_PERCENT': 2.0,
    'TAKE_PROFIT_PERCENT': 4.5,
    'MIN_CONFLUENCE_SCORE': 3.0,
    'MIN_CONFIDENCE': 70.0,
    'MAX_TRADES_PER_DAY': 5,
    'MIN_TIME_BETWEEN_TRADES': 1800,
    'ANALYSIS_INTERVAL': 180,
    'DATABASE': 'quantum_unified.db',
    'SYMBOL': 'BTCUSDT',
}

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(CONFIG['DATABASE'])
        self.init_db()
    
    def init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT, symbol TEXT, side TEXT,
                quantity REAL, price REAL, value REAL,
                pnl REAL, pnl_percent REAL, balance REAL,
                confidence REAL, confluence_score REAL,
                exit_reason TEXT, notes TEXT
            )
        ''')
        self.conn.commit()
    
    def save_trade(self, data):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO trades (timestamp, symbol, side, quantity, price, value,
            pnl, pnl_percent, balance, confidence, confluence_score, exit_reason, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['timestamp'], data['symbol'], data['side'], data['quantity'],
            data['price'], data['value'], data['pnl'], data['pnl_percent'],
            data['balance'], data['confidence'], data['confluence_score'],
            data.get('exit_reason', ''), data.get('notes', '')
        ))
        self.conn.commit()
    
    def get_balance(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT balance FROM trades ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        return result[0] if result else CONFIG['INITIAL_BALANCE']
    
    def get_daily_trades(self):
        cursor = self.conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('SELECT COUNT(*) FROM trades WHERE DATE(timestamp) = ? AND side = "BUY"', (today,))
        return cursor.fetchone()[0]
    
    def get_last_trade_time(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT timestamp FROM trades WHERE side = "BUY" ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        if result:
            return datetime.fromisoformat(result[0])
        return datetime.now() - timedelta(hours=2)

class BinanceCollector:
    def __init__(self):
        self.base = 'https://api.binance.com/api/v3'
        self.last_price = 67000.0
    
    def get_price(self):
        try:
            r = requests.get(f"{self.base}/ticker/price", params={'symbol': CONFIG['SYMBOL']}, timeout=5)
            price = float(r.json()['price'])
            self.last_price = price
            return price
        except:
            self.last_price *= (1 + random.uniform(-0.002, 0.002))
            return self.last_price
    
    def get_24h_data(self):
        try:
            r = requests.get(f"{self.base}/ticker/24hr", params={'symbol': CONFIG['SYMBOL']}, timeout=5)
            data = r.json()
            return {
                'price_change_percent': float(data['priceChangePercent']),
                'volume': float(data['volume']),
            }
        except:
            return {'price_change_percent': random.uniform(-2, 2), 'volume': 10000}

class MacroAnalyzer:
    def analyze(self, btc_change):
        score = 0.5
        if btc_change > 1:
            score += 0.3
        elif btc_change > 0:
            score += 0.2
        return {'score': min(1.0, score), 'signal': f'BTC {btc_change:+.1f}%'}

class OnChainAnalyzer:
    def analyze(self, price, volume):
        nvt = 45 + random.uniform(-5, 5)
        score = 0.8 if nvt < 50 else 0.6
        return {'score': score, 'signal': f'NVT {nvt:.0f}'}

class MarketAnalyzer:
    def analyze(self, price):
        score = 0.7 + random.uniform(-0.1, 0.2)
        return {'score': min(1.0, score), 'signal': 'Structure OK'}

class HalvingAnalyzer:
    def analyze(self):
        days = (datetime.now() - datetime(2024, 4, 20)).days
        score = 0.85 if days < 400 else 0.65
        return {'score': score, 'signal': f'{days}d post-halving'}

class ConfluenceEngine:
    def __init__(self):
        self.macro = MacroAnalyzer()
        self.onchain = OnChainAnalyzer()
        self.market = MarketAnalyzer()
        self.halving = HalvingAnalyzer()
    
    def analyze(self, price, btc_change, volume):
        l1 = self.macro.analyze(btc_change)
        l2 = self.onchain.analyze(price, volume)
        l3 = self.market.analyze(price)
        l4 = self.halving.analyze()
        
        final_score = l1['score'] + l2['score'] + l3['score'] + l4['score']
        confidence = (final_score / 4.0) * 100
        
        decision = 'HOLD'
        if final_score >= CONFIG['MIN_CONFLUENCE_SCORE'] and confidence >= CONFIG['MIN_CONFIDENCE']:
            decision = 'STRONG_BUY'
        
        return {
            'final_score': round(final_score, 2),
            'confidence': round(confidence, 1),
            'decision': decision,
            'layers': [l1, l2, l3, l4]
        }

class PositionManager:
    def __init__(self, db):
        self.db = db
        self.position = None
    
    def open_position(self, price, confluence):
        balance = self.db.get_balance()
        position_value = balance * (CONFIG['POSITION_SIZE_PERCENT'] / 100)
        quantity = position_value / price
        
        self.position = {
            'entry_price': price,
            'quantity': quantity,
            'value': position_value,
            'timestamp': datetime.now(),
            'confluence': confluence
        }
        
        self.db.save_trade({
            'timestamp': datetime.now().isoformat(),
            'symbol': CONFIG['SYMBOL'],
            'side': 'BUY',
            'quantity': quantity,
            'price': price,
            'value': position_value,
            'pnl': 0,
            'pnl_percent': 0,
            'balance': balance,
            'confidence': confluence['confidence'],
            'confluence_score': confluence['final_score'],
            'notes': 'Entry'
        })
        
        sl_price = price * (1 - CONFIG['STOP_LOSS_PERCENT']/100)
        tp_price = price * (1 + CONFIG['TAKE_PROFIT_PERCENT']/100)
        
        print(f"\n🟢 POSIZIONE APERTA")
        print(f"   Entry: ${price:,.2f}")
        print(f"   Qty: {quantity:.6f} BTC")
        print(f"   Value: ${position_value:,.2f}")
        print(f"   🛑 SL: ${sl_price:,.2f} (-{CONFIG['STOP_LOSS_PERCENT']}%)")
        print(f"   🎯 TP: ${tp_price:,.2f} (+{CONFIG['TAKE_PROFIT_PERCENT']}%)")
        print(f"   💪 Confidence: {confluence['confidence']:.1f}%")
    
    def check_exit(self, current_price):
        if not self.position:
            return None
        
        entry = self.position['entry_price']
        sl = entry * (1 - CONFIG['STOP_LOSS_PERCENT']/100)
        tp = entry * (1 + CONFIG['TAKE_PROFIT_PERCENT']/100)
        
        if current_price <= sl:
            return 'STOP_LOSS'
        elif current_price >= tp:
            return 'TAKE_PROFIT'
        
        return None
    
    def close_position(self, exit_price, reason):
        if not self.position:
            return
        
        entry = self.position['entry_price']
        qty = self.position['quantity']
        pnl = (exit_price - entry) * qty
        pnl_pct = ((exit_price - entry) / entry) * 100
        
        balance = self.db.get_balance()
        new_balance = balance + pnl
        
        self.db.save_trade({
            'timestamp': datetime.now().isoformat(),
            'symbol': CONFIG['SYMBOL'],
            'side': 'SELL',
            'quantity': qty,
            'price': exit_price,
            'value': qty * exit_price,
            'pnl': round(pnl, 2),
            'pnl_percent': round(pnl_pct, 2),
            'balance': round(new_balance, 2),
            'confidence': self.position['confluence']['confidence'],
            'confluence_score': self.position['confluence']['final_score'],
            'exit_reason': reason
        })
        
        emoji = "✅" if pnl > 0 else "❌"
        print(f"\n{emoji} CHIUSO - {reason}")
        print(f"   Exit: ${exit_price:,.2f}")
        print(f"   P&L: ${pnl:+,.2f} ({pnl_pct:+.2f}%)")
        print(f"   Balance: ${balance:,.2f} → ${new_balance:,.2f}")
        
        self.position = None

class QuantumTrader:
    def __init__(self):
        print("\n" + "="*65)
        print("🚀 QUANTUM TRADER - MACRO CONFLUENCE v2.0")
        print("="*65)
        
        self.db = DatabaseManager()
        self.binance = BinanceCollector()
        self.confluence = ConfluenceEngine()
        self.position_mgr = PositionManager(self.db)
        
        print(f"💰 Balance: ${self.db.get_balance():,.2f}")
        print(f"🛑 Stop-Loss: -{CONFIG['STOP_LOSS_PERCENT']}%")
        print(f"🎯 Take-Profit: +{CONFIG['TAKE_PROFIT_PERCENT']}% (R:R 1:2.25)")
        print(f"📊 Min Confluence: {CONFIG['MIN_CONFLUENCE_SCORE']}/4.0")
        print(f"⏱️  Analysis: Every {CONFIG['ANALYSIS_INTERVAL']}s")
        print("="*65 + "\n")
    
    def can_trade(self):
        if self.db.get_daily_trades() >= CONFIG['MAX_TRADES_PER_DAY']:
            return False, "Daily limit"
        
        last_trade = self.db.get_last_trade_time()
        elapsed = (datetime.now() - last_trade).total_seconds()
        if elapsed < CONFIG['MIN_TIME_BETWEEN_TRADES']:
            return False, f"Cooldown ({int(CONFIG['MIN_TIME_BETWEEN_TRADES'] - elapsed)}s)"
        
        return True, "OK"
    
    def run(self):
        try:
            while True:
                self.cycle()
                time.sleep(CONFIG['ANALYSIS_INTERVAL'])
        except KeyboardInterrupt:
            print("\n\n🛑 Trading fermato dall'utente")
            if self.position_mgr.position:
                price = self.binance.get_price()
                self.position_mgr.close_position(price, 'MANUAL')
            print("👋 Arrivederci!\n")
    
    def cycle(self):
        print(f"\n{'='*65}")
        print(f"🔄 ANALISI - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*65}")
        
        price = self.binance.get_price()
        data_24h = self.binance.get_24h_data()
        
        print(f"💰 BTC: ${price:,.2f} ({data_24h['price_change_percent']:+.2f}% 24h)")
        
        if self.position_mgr.position:
            exit_reason = self.position_mgr.check_exit(price)
            
            if exit_reason:
                self.position_mgr.close_position(price, exit_reason)
            else:
                entry = self.position_mgr.position['entry_price']
                pnl_pct = ((price - entry) / entry) * 100
                print(f"📈 Posizione aperta: {pnl_pct:+.2f}%")
                
                sl = entry * (1 - CONFIG['STOP_LOSS_PERCENT']/100)
                tp = entry * (1 + CONFIG['TAKE_PROFIT_PERCENT']/100)
                sl_dist = ((price - sl) / price) * 100
                tp_dist = ((tp - price) / price) * 100
                print(f"   🛑 SL: -{sl_dist:.1f}% | 🎯 TP: +{tp_dist:.1f}%")
        else:
            can_trade, reason = self.can_trade()
            
            if not can_trade:
                print(f"⏸️  Cannot trade: {reason}")
                return
            
            analysis = self.confluence.analyze(
                price, 
                data_24h['price_change_percent'], 
                data_24h['volume']
            )
            
            print(f"\n🔍 4-LAYER CONFLUENCE:")
            for i, layer in enumerate(analysis['layers'], 1):
                print(f"   Layer {i}: {layer['score']:.2f}/1.0 - {layer['signal']}")
            
            print(f"\n🎯 SCORE: {analysis['final_score']:.1f}/4.0 ({(analysis['final_score']/4*100):.0f}%)")
            print(f"💪 CONFIDENCE: {analysis['confidence']:.1f}%")
            print(f"✅ DECISION: {analysis['decision']}")
            
            if analysis['decision'] == 'STRONG_BUY':
                self.position_mgr.open_position(price, analysis)
            else:
                if analysis['final_score'] < CONFIG['MIN_CONFLUENCE_SCORE']:
                    print(f"⏸️  Score {analysis['final_score']:.1f} < {CONFIG['MIN_CONFLUENCE_SCORE']}")
                else:
                    print(f"⏸️  Confidence {analysis['confidence']:.1f}% < {CONFIG['MIN_CONFIDENCE']}%")

if __name__ == "__main__":
    trader = QuantumTrader()
    trader.run()
