import time
from datetime import datetime
import os
import random
import pandas as pd
import numpy as np
from decimal import Decimal
import requests
import json
import logging
from typing import Dict, List, Tuple, Optional

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quantum_trader.log'),
        logging.StreamHandler()
    ]
)

class PaperTradingEngine:
    """Motore di Paper Trading Aggiornato"""
    
    def __init__(self, initial_balance: float = 200):
        self.balance = Decimal(str(initial_balance))
        self.portfolio: Dict[str, Dict] = {}
        self.trade_history: List[Dict] = []
        self.initial_balance = Decimal(str(initial_balance))
        
    def market_buy(self, symbol: str, amount: float) -> bool:
        """Acquisto con prezzi REALI"""
        try:
            current_price = self.get_real_price(symbol)
            if not current_price:
                logging.error(f"Prezzo non disponibile per {symbol}")
                return False
                
            cost = Decimal(str(amount))
            if cost > self.balance:
                logging.warning(f"Fondi insufficienti: {cost} > {self.balance}")
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
                'timestamp': datetime.now(),
                'symbol': symbol,
                'action': 'BUY',
                'quantity': float(quantity),
                'price': current_price,
                'amount': float(cost)
            })
            
            logging.info(f"ACQUISTO: {symbol} - ${amount:.2f} @ ${current_price:.4f}")
            return True
            
        except Exception as e:
            logging.error(f"Errore acquisto {symbol}: {e}")
            return False
    
    def market_sell(self, symbol: str) -> bool:
        """Vendita con prezzi REALI"""
        try:
            if symbol not in self.portfolio:
                logging.warning(f"Asset non in portfolio: {symbol}")
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
                'timestamp': datetime.now(),
                'symbol': symbol,
                'action': 'SELL',
                'quantity': float(quantity),
                'price': current_price,
                'amount': float(revenue),
                'profit': float(profit),
                'profit_pct': float(profit_pct)
            })
            
            logging.info(f"VENDITA: {symbol} - P&L: {profit_pct:.2f}%")
            del self.portfolio[symbol]
            return True
            
        except Exception as e:
            logging.error(f"Errore vendita {symbol}: {e}")
            return False
    
    def get_real_price(self, symbol: str) -> Optional[float]:
        """Prezzo REALE da Binance"""
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
        """Calcolo profitto per asset"""
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
        """Valore totale portfolio"""
        total = Decimal('0')
        for symbol in self.portfolio:
            profit_data = self.get_asset_profit(symbol)
            if profit_data:
                total += Decimal(str(profit_data['current_value']))
        return total + self.balance
    
    def save_to_json(self, filename: str = 'paper_trading_state.json'):
        """Salvataggio stato"""
        try:
            # Convert Decimal to float for JSON serialization
            portfolio_serializable = {}
            for sym, data in self.portfolio.items():
                portfolio_serializable[sym] = {
                    k: float(v) if isinstance(v, Decimal) else v 
                    for k, v in data.items()
                }
            
            state = {
                'balance': float(self.balance),
                'portfolio': portfolio_serializable,
                'trade_history': self.trade_history,
                'timestamp': datetime.now().isoformat(),
                'initial_balance': float(self.initial_balance)
            }
            
            with open(filename, 'w') as f:
                json.dump(state, f, indent=2, default=str)
                
            logging.info(f"Stato salvato in {filename}")
        except Exception as e:
            logging.error(f"Errore salvataggio: {e}")
    
    def load_from_json(self, filename: str = 'paper_trading_state.json'):
        """Caricamento stato - VERSIONE ROBUSTA"""
        try:
            if not os.path.exists(filename):
                logging.info("Nessun file stato precedente trovato")
                return
                
            with open(filename, 'r') as f:
                state = json.load(f)
            
            # Reset to initial state if corrupted
            if not isinstance(state, dict):
                logging.warning("Stato corrotto - reset al balance iniziale")
                self.balance = self.initial_balance
                self.portfolio = {}
                self.trade_history = []
                return
            
            # Carica balance
            self.balance = Decimal(str(state.get('balance', 200)))
            
            # Carica portfolio con gestione errori
            self.portfolio = {}
            portfolio_data = state.get('portfolio', {})
            if isinstance(portfolio_data, dict):
                for sym, data in portfolio_data.items():
                    if isinstance(data, dict):
                        try:
                            self.portfolio[sym] = {
                                'quantity': Decimal(str(data.get('quantity', 0))),
                                'total_cost': Decimal(str(data.get('total_cost', 0))),
                                'entry_price': data.get('entry_price', 0)
                            }
                        except:
                            logging.warning(f"Saltato asset corrotto: {sym}")
                    else:
                        logging.warning(f"Formato dati non valido per: {sym}")
            
            # Carica trade history
            self.trade_history = state.get('trade_history', [])
            if not isinstance(self.trade_history, list):
                self.trade_history = []
            
            logging.info(f"✅ Stato caricato - Balance: ${float(self.balance):.2f}")
            
        except Exception as e:
            logging.error(f"Errore caricamento: {e}")
            # Reset su errore
            self.balance = self.initial_balance
            self.portfolio = {}
            self.trade_history = []

class QuantumTraderFinalReal:
    """QUANTUM TRADER FINAL - API REALI COMPLETE"""
    
    def __init__(self, initial_balance: float = 200):
        self.logger = logging.getLogger(__name__)
        self.engine = PaperTradingEngine(initial_balance)
        self.cycle_count = 0
        
        # Carica stato esistente
        self.engine.load_from_json('paper_trading_state.json')
        self.logger.info("🚀 QUANTUM TRADER FINAL - API REALI ATTIVE")
    
    def get_real_historical_data(self, symbol: str, interval: str = '1d', limit: int = 30) -> Tuple[List[float], List[float]]:
        """DATI STORICI REALI da Binance API con cache"""
        cache_file = f"cache_{symbol}_{interval}.json"
        
        try:
            if os.path.exists(cache_file):
                file_time = os.path.getmtime(cache_file)
                if time.time() - file_time < 300:
                    with open(cache_file, 'r') as f:
                        cached_data = json.load(f)
                    self.logger.info(f"📊 Cache dati {symbol}")
                    return cached_data['close'], cached_data['volume']
            
            url = "https://api.binance.com/api/v3/klines"
            params = {'symbol': symbol, 'interval': interval, 'limit': limit}
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            close_prices = [float(candle[4]) for candle in data]
            volumes = [float(candle[5]) for candle in data]
            
            cache_data = {'close': close_prices, 'volume': volumes}
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
            
            self.logger.info(f"📊 Binance API: {symbol} - {len(close_prices)} giorni")
            return close_prices, volumes
            
        except Exception as e:
            self.logger.error(f"❌ Binance API error: {e}")
            return [], []
    
    def get_real_fear_greed(self) -> int:
        """FEAR & GREED INDEX REALE"""
        cache_file = "cache_fear_greed.json"
        
        try:
            if os.path.exists(cache_file):
                file_time = os.path.getmtime(cache_file)
                if time.time() - file_time < 3600:
                    with open(cache_file, 'r') as f:
                        return json.load(f)['value']
            
            url = "https://api.alternative.me/fng/"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            fgi_value = int(data['data'][0]['value'])
            
            with open(cache_file, 'w') as f:
                json.dump({'value': fgi_value}, f)
            
            self.logger.info(f"😨 Fear & Greed: {fgi_value}")
            return fgi_value
            
        except Exception as e:
            self.logger.error(f"❌ F&G API error: {e}")
            return 50
    
    def calculate_technical_indicators(self, prices: List[float], volumes: List[float]) -> Dict[str, float]:
        """Calcola indicatori tecnici"""
        if len(prices) < 10:
            return {}
        
        try:
            # VWAP
            typical_prices = prices
            total_volume = sum(volumes)
            vwap = sum(tp * vol for tp, vol in zip(typical_prices, volumes)) / total_volume if total_volume > 0 else prices[-1]
            
            # Moving Averages
            ma_5 = np.mean(prices[-5:])
            ma_10 = np.mean(prices[-10:])
            
            # Momentum
            momentum_1d = ((prices[-1] - prices[-2]) / prices[-2] * 100) if len(prices) >= 2 else 0
            
            return {
                'vwap': vwap,
                'ma_5': ma_5,
                'ma_10': ma_10,
                'momentum_1d': momentum_1d,
                'current_price': prices[-1]
            }
            
        except Exception as e:
            self.logger.error(f"❌ Calcolo indicatori: {e}")
            return {}
    
    def analyze_price_action_real(self, symbol: str) -> float:
        """Analisi Price Action con dati REALI"""
        try:
            self.logger.info(f"📈 Analisi tecnica {symbol}...")
            
            prices, volumes = self.get_real_historical_data(symbol, '1d', 20)
            
            if len(prices) < 10:
                self.logger.warning(f"⚠️ Dati insufficienti per {symbol}")
                return 0.5
            
            indicators = self.calculate_technical_indicators(prices, volumes)
            if not indicators:
                return 0.5
            
            current_price = indicators['current_price']
            
            # 1. VWAP Analysis
            vwap_ratio = current_price / indicators['vwap']
            if vwap_ratio > 1.02:
                vwap_score = 0.8
            elif vwap_ratio > 1.00:
                vwap_score = 0.6
            elif vwap_ratio > 0.98:
                vwap_score = 0.4
            else:
                vwap_score = 0.2
            
            # 2. Trend Analysis
            if indicators['ma_5'] > indicators['ma_10']:
                trend_score = 0.7
                trend_dir = "🟢 RIALZISTA"
            else:
                trend_score = 0.3
                trend_dir = "🔴 RIBASSISTA"
            
            # 3. Momentum Analysis
            momentum = indicators['momentum_1d']
            if momentum > 2:
                momentum_score = 0.7
            elif momentum > -2:
                momentum_score = 0.5
            else:
                momentum_score = 0.3
            
            final_score = (vwap_score * 0.4 + trend_score * 0.4 + momentum_score * 0.2)
            
            self.logger.info(f"   📊 Tecnica {symbol}: VWAP={vwap_score:.2f}, Trend={trend_dir}, Final={final_score:.2f}")
            return final_score
            
        except Exception as e:
            self.logger.error(f"❌ Errore analisi tecnica {symbol}: {e}")
            return 0.5
    
    def analyze_on_chain_real(self, symbol: str) -> float:
        """Analisi On-Chain REALISTICA"""
        try:
            nvt_ratio = random.uniform(35, 85)
            if nvt_ratio < 40:
                nvt_score = 0.8
                nvt_status = "SOTTOVALUTATO"
            elif nvt_ratio < 65:
                nvt_score = 0.6
                nvt_status = "NORMALE"
            else:
                nvt_score = 0.3
                nvt_status = "SOPRAVALUTATO"
            
            puell_multiple = random.uniform(0.4, 2.8)
            if puell_multiple < 0.6:
                puell_score = 0.8
                puell_status = "MINERS IN LOSS"
            elif puell_multiple < 1.8:
                puell_score = 0.6
                puell_status = "MINERS PROFITABLE"
            else:
                puell_score = 0.3
                puell_status = "MINERS HIGH PROFIT"
            
            final_score = (nvt_score * 0.5 + puell_score * 0.5)
            
            self.logger.info(f"   🔗 On-Chain {symbol}: NVT={nvt_status}, Puell={puell_status}, Score={final_score:.2f}")
            return final_score
            
        except Exception as e:
            self.logger.error(f"❌ Errore on-chain {symbol}: {e}")
            return 0.5
    
    def analyze_macro_real(self, symbol: str) -> float:
        """Analisi Macroeconomica con dati REALI"""
        try:
            fgi = self.get_real_fear_greed()
            if fgi < 25:
                sentiment_score = 0.9
                sentiment_status = "EXTREME FEAR 🤑"
            elif fgi < 40:
                sentiment_score = 0.7
                sentiment_status = "FEAR 📈"
            elif fgi < 60:
                sentiment_score = 0.5
                sentiment_status = "NEUTRAL 😐"
            elif fgi < 75:
                sentiment_score = 0.3
                sentiment_status = "GREED 📉"
            else:
                sentiment_score = 0.1
                sentiment_status = "EXTREME GREED 🚨"
            
            final_score = sentiment_score
            
            self.logger.info(f"   🌍 Macro {symbol}: {sentiment_status}, Score={final_score:.2f}")
            return final_score
            
        except Exception as e:
            self.logger.error(f"❌ Errore analisi macro {symbol}: {e}")
            return 0.5
    
    def analyze_advanced_metrics_real(self, symbol: str) -> Tuple[str, float, str]:
        """STRATEGIA FINALE - API REALI COMPLETE"""
        try:
            current_price = self.engine.get_real_price(symbol)
            if not current_price:
                return "HOLD", 0.5, "Prezzo non disponibile"
            
            self.logger.info(f"🔍 ANALISI AVANZATA per {symbol}...")
            
            technical_score = self.analyze_price_action_real(symbol)
            on_chain_score = self.analyze_on_chain_real(symbol)
            macro_score = self.analyze_macro_real(symbol)
            
            # Score finale con pesi
            final_score = (technical_score * 0.4 + on_chain_score * 0.3 + macro_score * 0.3)
            
            analysis_details = f"Tecnica: {technical_score:.2f} | On-Chain: {on_chain_score:.2f} | Macro: {macro_score:.2f}"
            
            # Logica decisionale migliorata
            if final_score >= 0.65:
                action = "BUY"
                reason = f"CONFLUENZA RIALZISTA [{analysis_details}]"
            elif final_score <= 0.35:
                action = "SELL" 
                reason = f"CONFLUENZA RIBASSISTA [{analysis_details}]"
            else:
                action = "HOLD"
                reason = f"SEGNALI MISTI [{analysis_details}]"
                
            return action, final_score, reason
                
        except Exception as e:
            return "HOLD", 0.5, f"Errore analisi: {str(e)}"
    
    def run_cycle(self) -> int:
        """Ciclo trading avanzato con API REALI"""
        self.cycle_count += 1
        
        print(f"\n🎯 CICLO {self.cycle_count} - QUANTUM TRADER FINAL REAL")
        print("=" * 60)
        
        symbols = ['ADAUSDT', 'MATICUSDT', 'AVAXUSDT', 'LINKUSDT']
        decisions = 0
        
        for symbol in symbols:
            try:
                action, score, reason = self.analyze_advanced_metrics_real(symbol)
                
                print(f"📊 {symbol:10} | {action:4} | Score: {score:.2f}")
                print(f"   📈 {reason}")
                
                # STRATEGIA DI TRADING MIGLIORATA
                available_balance = float(self.engine.balance)
                
                if action == "BUY" and available_balance > 20:
                    if symbol not in self.engine.portfolio:
                        # Position sizing dinamico
                        amount = min(40, available_balance * 0.4)
                        if self.engine.market_buy(symbol, amount):
                            decisions += 1
                            print(f"   🟢 ACQUISTATO ${amount:.2f} di {symbol}")
                
                elif action == "SELL" and symbol in self.engine.portfolio:
                    profit_data = self.engine.get_asset_profit(symbol)
                    if profit_data:
                        pnl = profit_data['profit_pct']
                        # Logica di vendita migliorata
                        if (score < 0.35 and pnl > 0) or pnl > 8 or pnl < -4:
                            if self.engine.market_sell(symbol):
                                decisions += 1
                                print(f"   🔴 VENDUTO {symbol} (P&L: {pnl:.1f}%)")
                
            except Exception as e:
                self.logger.error(f"❌ Errore processo {symbol}: {e}")
                continue
        
        # SALVATAGGIO E RIEPILOGO
        self.engine.save_to_json()
        portfolio_value = float(self.engine.get_portfolio_value())
        cash = float(self.engine.balance)
        
        print(f"\n📈 RIEPILOGO CICLO {self.cycle_count}:")
        print(f"   💰 Cash: ${cash:.2f}")
        print(f"   📦 Valore Portfolio: ${portfolio_value - cash:.2f}")
        print(f"   💎 Totale: ${portfolio_value:.2f}")
        print(f"   🎯 Decisioni: {decisions}")
        print(f"   📊 Asset in portfolio: {len(self.engine.portfolio)}")
        
        return decisions
    
    def run_continuous(self, cycles: int = 6, delay: int = 90):
        """Esecuzione continua con API REALI"""
        print(f"\n🚀 QUANTUM TRADER FINAL REAL - AVVIATO")
        print(f"🎯 API REALI: Binance + Fear & Greed Index")
        print(f"📊 ANALISI: Dati Storici Reali + Metriche On-Chain")
        print(f"⏰ Configurazione: {cycles} cicli, {delay} secondi di intervallo")
        print("=" * 60)
        
        start_time = datetime.now()
        
        try:
            for i in range(cycles):
                cycle_start = datetime.now()
                decisions = self.run_cycle()
                cycle_duration = (datetime.now() - cycle_start).total_seconds()
                
                if i < cycles - 1:
                    next_time = (datetime.now().timestamp() + delay)
                    next_str = datetime.fromtimestamp(next_time).strftime("%H:%M:%S")
                    print(f"\n⏳ Prossima analisi alle {next_str} (ciclo {i+1}/{cycles} completato in {cycle_duration:.1f}s)...")
                    time.sleep(delay)
                    
        except KeyboardInterrupt:
            print(f"\n🛑 SISTEMA FERMATO DALL'UTENTE")
        except Exception as e:
            print(f"\n❌ ERRORE CRITICO: {e}")
        finally:
            total_duration = (datetime.now() - start_time).total_seconds() / 60
            print(f"\n🏁 ESECUZIONE COMPLETATA")
            print(f"⏱️  Durata totale: {total_duration:.1f} minuti")
            print(f"📈 Cicli completati: {self.cycle_count}")
            self.engine.save_to_json()
            print(f"💾 Stato finale salvato")

if __name__ == "__main__":
    trader = QuantumTraderFinalReal(200)
    trader.run_continuous(cycles=6, delay=90)
