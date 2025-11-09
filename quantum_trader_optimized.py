import time
from datetime import datetime
import os
import random
import numpy as np
from decimal import Decimal
import requests
import json
import logging
from typing import Dict, List, Tuple, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quantum_trader.log'),
        logging.StreamHandler()
    ]
)

class PaperTradingEngine:
    def __init__(self, initial_balance: float = 200):  # ✅ $200 EURO
        self.balance = Decimal(str(initial_balance))
        self.portfolio: Dict[str, Dict] = {}
        self.trade_history: List[Dict] = []
        self.initial_balance = Decimal(str(initial_balance))
        
    def market_buy(self, symbol: str, amount: float) -> bool:
        try:
            current_price = self.get_real_price(symbol)
            if not current_price:
                return False
                
            cost = Decimal(str(amount))
            if cost > self.balance:
                return False
                
            quantity = cost / Decimal(str(current_price))
            
            if symbol in self.portfolio:
                self.portfolio[symbol]['quantity'] += quantity
                self.portfolio[symbol]['total_cost'] += cost
            else:
                self.portfolio[symbol] = {
                    'quantity': quantity,
                    'total_cost': cost,
                    'entry_price': current_price
                }
                
            self.balance -= cost
            self.trade_history.append({
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'action': 'BUY',
                'quantity': float(quantity),
                'price': current_price,
                'amount': float(cost)
            })
            
            logging.info(f"✅ ACQUISTO: {symbol} - ${amount:.2f} @ ${current_price:.4f}")
            return True
            
        except Exception as e:
            logging.error(f"Errore acquisto {symbol}: {e}")
            return False
    
    def market_sell(self, symbol: str) -> bool:
        try:
            if symbol not in self.portfolio:
                return False
                
            current_price = self.get_real_price(symbol)
            if not current_price:
                return False
                
            asset = self.portfolio[symbol]
            quantity = asset['quantity']
            revenue = quantity * Decimal(str(current_price))
            
            self.balance += revenue
            profit = revenue - asset['total_cost']
            profit_pct = (profit / asset['total_cost']) * 100
            
            self.trade_history.append({
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'action': 'SELL',
                'quantity': float(quantity),
                'price': current_price,
                'amount': float(revenue),
                'profit': float(profit),
                'profit_pct': float(profit_pct)
            })
            
            logging.info(f"✅ VENDITA: {symbol} - P&L: {profit_pct:.2f}%")
            del self.portfolio[symbol]
            return True
            
        except Exception as e:
            logging.error(f"Errore vendita {symbol}: {e}")
            return False
    
    def get_real_price(self, symbol: str) -> Optional[float]:
        try:
            url = "https://api.binance.com/api/v3/ticker/price"
            params = {'symbol': symbol}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            return float(data['price'])
        except Exception as e:
            logging.error(f"Errore prezzo {symbol}: {e}")
            return None
    
    def get_asset_profit(self, symbol: str) -> Optional[Dict]:
        if symbol not in self.portfolio:
            return None
            
        current_price = self.get_real_price(symbol)
        if not current_price:
            return None
            
        asset = self.portfolio[symbol]
        current_value = asset['quantity'] * Decimal(str(current_price))
        profit = current_value - asset['total_cost']
        profit_pct = (profit / asset['total_cost']) * 100
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'quantity': float(asset['quantity']),
            'current_value': float(current_value),
            'total_cost': float(asset['total_cost']),
            'profit': float(profit),
            'profit_pct': float(profit_pct)
        }
    
    def get_portfolio_value(self) -> Decimal:
        total = Decimal('0')
        for symbol in self.portfolio:
            profit_data = self.get_asset_profit(symbol)
            if profit_data:
                total += Decimal(str(profit_data['current_value']))
        return total + self.balance
    
    def save_to_json(self, filename: str = 'paper_trading_state.json'):
        try:
            state = {
                'balance': float(self.balance),
                'portfolio': {
                    sym: {k: float(v) if isinstance(v, Decimal) else v 
                         for k, v in data.items()}
                    for sym, data in self.portfolio.items()
                },
                'trade_history': self.trade_history,
                'timestamp': datetime.now().isoformat(),
                'initial_balance': float(self.initial_balance)
            }
            
            with open(filename, 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            logging.error(f"Errore salvataggio: {e}")
    
    def load_from_json(self, filename: str = 'paper_trading_state.json'):
        try:
            if not os.path.exists(filename):
                logging.info("📝 Nuovo sistema - Balance iniziale: $200")
                return
                
            with open(filename, 'r') as f:
                state = json.load(f)
            
            self.balance = Decimal(str(state.get('balance', 200)))
            
            self.portfolio = {}
            for sym, data in state.get('portfolio', {}).items():
                self.portfolio[sym] = {
                    'quantity': Decimal(str(data.get('quantity', 0))),
                    'total_cost': Decimal(str(data.get('total_cost', 0))),
                    'entry_price': data.get('entry_price', 0)
                }
            
            self.trade_history = state.get('trade_history', [])
            
            logging.info(f"✅ Stato caricato - Balance: ${float(self.balance):.2f}")
            
        except Exception as e:
            logging.error(f"Errore caricamento: {e}")

class QuantumTraderOptimized:
    """STRATEGIA OTTIMIZZATA per $200 EURO"""
    
    def __init__(self, initial_balance: float = 200):  # ✅ $200 EURO
        self.logger = logging.getLogger(__name__)
        self.engine = PaperTradingEngine(initial_balance)
        self.cycle_count = 0
        self.engine.load_from_json()
        self.logger.info("🚀 QUANTUM TRADER OTTIMIZZATO - $200 EURO")
    
    def get_real_fear_greed(self) -> int:
        try:
            url = "https://api.alternative.me/fng/"
            response = requests.get(url, timeout=10)
            data = response.json()
            fgi_value = int(data['data'][0]['value'])
            return fgi_value
        except Exception as e:
            self.logger.error(f"F&G API error: {e}")
            return 50
    
    def get_historical_prices(self, symbol: str) -> List[float]:
        try:
            url = "https://api.binance.com/api/v3/klines"
            params = {'symbol': symbol, 'interval': '1d', 'limit': 10}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            return [float(candle[4]) for candle in data]
        except:
            return []
    
    def analyze_optimized(self, symbol: str, asset_tier: str) -> Tuple[str, float, str]:
        """ANALISI OTTIMIZZATA per $200"""
        try:
            current_price = self.engine.get_real_price(symbol)
            if not current_price:
                return "HOLD", 0.5, "Prezzo non disponibile"
            
            # 1. Fear & Greed Index (peso 70%)
            fgi = self.get_real_fear_greed()
            
            if fgi < 25:
                fear_score = 0.95
                fear_status = "EXTREME FEAR 🤑"
            elif fgi < 40:
                fear_score = 0.80
                fear_status = "FEAR 📈"
            elif fgi < 60:
                fear_score = 0.50
                fear_status = "NEUTRAL 😐"
            else:
                fear_score = 0.30
                fear_status = "GREED/DANGER ⚠️"
            
            # 2. Trend Tecnico (peso 30%)
            prices = self.get_historical_prices(symbol)
            if len(prices) >= 5:
                recent_avg = np.mean(prices[-3:])
                older_avg = np.mean(prices[:5])
                
                if recent_avg > older_avg * 1.02:
                    trend_score = 0.70
                    trend_status = "UPTREND"
                elif recent_avg > older_avg * 0.98:
                    trend_score = 0.50
                    trend_status = "LATERAL"
                else:
                    trend_score = 0.40
                    trend_status = "DOWNTREND"
            else:
                trend_score = 0.50
                trend_status = "UNKNOWN"
            
            # BOOST per BTC/ETH in Extreme Fear
            if asset_tier == "MAJOR" and fgi < 30:
                boost = 0.05
                tier_label = "🔥 MAJOR"
            else:
                boost = 0.0
                tier_label = "⭐ ALTCOIN"
            
            # SCORE FINALE: 70% Fear + 30% Trend + Boost
            final_score = (fear_score * 0.70 + trend_score * 0.30) + boost
            
            reason = f"{tier_label} | {fear_status} | {trend_status} | Score={final_score:.2f}"
            
            # 🎯 DECISIONE OTTIMIZZATA - GESTIONE VENDITE PIÙ AGGRESSIVA
            if symbol in self.engine.portfolio:
                profit_data = self.engine.get_asset_profit(symbol)
                if profit_data:
                    pnl = profit_data['profit_pct']
                    # ✅ VENDITA PIÙ AGGRESSIVA per liberare cash
                    if pnl > 4 or pnl < -2:  # Soglie più basse
                        return "SELL", final_score, f"VENDITA: {pnl:.1f}%"
            
            if final_score >= 0.65:
                return "BUY", final_score, reason
            elif final_score <= 0.35:
                return "SELL", final_score, reason
            else:
                return "HOLD", final_score, reason
                
        except Exception as e:
            return "HOLD", 0.5, f"Errore: {e}"
    
    def run_cycle(self) -> int:
        self.cycle_count += 1
        
        print(f"\n{'='*70}")
        print(f"🎯 CICLO {self.cycle_count} - STRATEGIA OTTIMIZZATA ($200)")
        print(f"{'='*70}")
        
        # Fear & Greed globale
        fgi = self.get_real_fear_greed()
        if fgi < 25:
            print(f"😨 FEAR & GREED: {fgi} - ⚡ EXTREME FEAR - COMPRA AGGRESSIVO! ⚡")
        elif fgi < 40:
            print(f"😨 FEAR & GREED: {fgi} - 📈 FEAR - Opportunità")
        else:
            print(f"😨 FEAR & GREED: {fgi} - 😐 Normal/Greed")
        
        print()
        
        # 🔥 TOP 7 CRYPTO con priorità intelligente
        assets = [
            {'symbol': 'BTCUSDT', 'tier': 'MAJOR', 'name': 'Bitcoin', 'priority': 1},
            {'symbol': 'ETHUSDT', 'tier': 'MAJOR', 'name': 'Ethereum', 'priority': 2},
            {'symbol': 'SOLUSDT', 'tier': 'ALTCOIN', 'name': 'Solana', 'priority': 3},
            {'symbol': 'AVAXUSDT', 'tier': 'ALTCOIN', 'name': 'Avalanche', 'priority': 4},
            {'symbol': 'LINKUSDT', 'tier': 'ALTCOIN', 'name': 'Chainlink', 'priority': 5},
            {'symbol': 'DOTUSDT', 'tier': 'ALTCOIN', 'name': 'Polkadot', 'priority': 6},
            {'symbol': 'MATICUSDT', 'tier': 'ALTCOIN', 'name': 'Polygon', 'priority': 7}
        ]
        
        decisions = 0
        max_assets = 5  # ✅ Massimo 5 asset con $200
        
        # Ordina per priorità (BTC/ETH prima)
        assets_sorted = sorted(assets, key=lambda x: x['priority'])
        
        for asset in assets_sorted:
            symbol = asset['symbol']
            tier = asset['tier']
            name = asset['name']
            
            action, score, reason = self.analyze_optimized(symbol, tier)
            
            print(f"📊 {name:12} ({symbol:10}) | {action:4} | Score: {score:.2f}")
            print(f"   └─ {reason}")
            
            available_balance = float(self.engine.balance)
            current_assets = len(self.engine.portfolio)
            
            # 🎯 TRADING LOGIC OTTIMIZZATA per $200
            if action == "BUY" and available_balance > 20 and current_assets < max_assets:
                if symbol not in self.engine.portfolio:
                    # Position sizing OTTIMIZZATO per $200
                    if tier == "MAJOR":
                        if fgi < 25:
                            amount = min(45, available_balance * 0.40)  # BTC/ETH: 40%
                        else:
                            amount = min(40, available_balance * 0.35)
                    else:
                        if fgi < 25:
                            amount = min(35, available_balance * 0.30)  # Altcoin: 30%
                        else:
                            amount = min(30, available_balance * 0.25)
                    
                    if self.engine.market_buy(symbol, amount):
                        decisions += 1
                        print(f"   🟢 ACQUISTATO ${amount:.2f} ({current_assets + 1}/{max_assets} asset)")
            
            elif action == "SELL" and symbol in self.engine.portfolio:
                profit_data = self.engine.get_asset_profit(symbol)
                if profit_data:
                    pnl = profit_data['profit_pct']
                    
                    if self.engine.market_sell(symbol):
                        decisions += 1
                        print(f"   🔴 VENDUTO {symbol} (P&L: {pnl:.1f}%)")
        
        self.engine.save_to_json()
        
        # RIEPILOGO
        cash = float(self.engine.balance)
        portfolio_value = float(self.engine.get_portfolio_value())
        total = cash + portfolio_value
        profit = total - float(self.engine.initial_balance)
        profit_pct = (profit / float(self.engine.initial_balance)) * 100
        
        print(f"\n📈 RIEPILOGO:")
        print(f"   💰 Cash: ${cash:.2f}")
        print(f"   📦 Portfolio: ${portfolio_value:.2f}")
        print(f"   💎 TOTALE: ${total:.2f} ({profit:+.2f} / {profit_pct:+.1f}%)")
        print(f"   🎯 Trade: {decisions} | Asset: {len(self.engine.portfolio)}/{max_assets}")
        
        # Dettaglio portfolio
        if self.engine.portfolio:
            print(f"\n   📊 PORTFOLIO ATTIVO:")
            total_invested = 0
            total_current = 0
            
            for sym in self.engine.portfolio:
                profit_data = self.engine.get_asset_profit(sym)
                if profit_data:
                    pnl = profit_data['profit_pct']
                    value = profit_data['current_value']
                    cost = profit_data['total_cost']
                    emoji = "🟢" if pnl >= 0 else "🔴"
                    
                    asset_name = next((a['name'] for a in assets if a['symbol'] == sym), sym)
                    total_invested += cost
                    total_current += value
                    
                    print(f"      {emoji} {asset_name:12}: ${value:.2f} ({pnl:+.1f}%)")
            
            portfolio_pnl = ((total_current - total_invested) / total_invested * 100) if total_invested > 0 else 0
            print(f"   📊 TOTALE PORTFOLIO: ${total_current:.2f} ({portfolio_pnl:+.2f}%)")
        
        return decisions
    
    def run_continuous(self, cycles: int = 10, delay: int = 60):
        print(f"\n{'='*70}")
        print("🚀 QUANTUM TRADER OTTIMIZZATO - $200 EURO")
        print("📊 Portfolio: BTC + ETH + SOL + AVAX + LINK + DOT + MATIC")
        print("🎯 Max Assets: 5 contemporaneamente")
        print("💰 Balance: $200 Euro")
        print("🎯 Vendite: P&L > 4% o < -2% (ottimizzate)")
        print("⚡ Strategia: Extreme Fear Contrarian")
        print(f"{'='*70}\n")
        
        try:
            for i in range(cycles):
                self.run_cycle()
                if i < cycles - 1:
                    print(f"\n⏳ Prossimo ciclo in {delay}s...\n")
                    time.sleep(delay)
                    
        except KeyboardInterrupt:
            print("\n🛑 FERMATO")
        finally:
            self.engine.save_to_json()
            print("\n💾 Stato salvato")

if __name__ == "__main__":
    trader = QuantumTraderOptimized(200)
    trader.run_continuous(cycles=10, delay=60)
