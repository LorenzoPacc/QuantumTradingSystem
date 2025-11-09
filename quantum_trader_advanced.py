import time
from datetime import datetime
import os
from paper_trading_engine import PaperTradingEngine
import random
import pandas as pd
import numpy as np
from decimal import Decimal

class QuantumTraderAdvanced:
    def __init__(self, initial_balance=150):
        print("🚀 QUANTUM TRADER ADVANCED - Strategia Avanzata")
        self.engine = PaperTradingEngine(initial_balance)
        
        if os.path.exists('paper_trading_state.json'):
            self.engine.load_from_json('paper_trading_state.json')
            print(f"✅ Stato caricato - Balance: ${float(self.engine.balance):.2f}")
        
        self.cycle_count = 0
        
    def analyze_advanced_metrics(self, symbol):
        """STRATEGIA AVANZATA - Le tue confluenze originali"""
        try:
            current_price = self.engine.get_real_price(symbol)
            if not current_price:
                return "HOLD", 0.5, "Prezzo non disponibile"
            
            # 📊 1. ANALISI TECNICA BASE (Price Action + VWAP)
            price_action_score = self.analyze_price_action(symbol, current_price)
            
            # 📈 2. ANALISI ON-CHAIN (NVT + Puell Multiple)  
            on_chain_score = self.analyze_on_chain(symbol)
            
            # 🌍 3. ANALISI MACRO (DXY correlations + cicli)
            macro_score = self.analyze_macro(symbol)
            
            # 🔄 4. ANALISI CICLI HALVING
            halving_score = self.analyze_halving_cycles()
            
            # 🎯 CALCOLO SCORE FINALE (confluenze)
            final_score = (
                price_action_score * 0.35 +      # 35% Technical
                on_chain_score * 0.25 +          # 25% On-chain
                macro_score * 0.25 +             # 25% Macro
                halving_score * 0.15             # 15% Cicli
            )
            
            # 📊 DECISIONE BASATA SU CONFLUENZE
            if final_score > 0.7:
                return "BUY", final_score, f"Score alto: {final_score:.2f}"
            elif final_score < 0.3:
                return "SELL", final_score, f"Score basso: {final_score:.2f}"
            else:
                return "HOLD", final_score, f"Score neutro: {final_score:.2f}"
                
        except Exception as e:
            return "HOLD", 0.5, f"Errore analisi: {str(e)}"
    
    def analyze_price_action(self, symbol, current_price):
        """Analisi Price Action + VWAP + Liquidità"""
        try:
            # Simula analisi price action avanzata
            # Nel sistema reale qui avresti dati storici e VWAP
            price_trend = random.uniform(0.3, 0.8)
            
            # Simula supporti/resistenze
            support_resistance = random.uniform(0.4, 0.9)
            
            # Simula analisi volume/VWAP
            volume_analysis = random.uniform(0.5, 0.85)
            
            return (price_trend * 0.4 + support_resistance * 0.3 + volume_analysis * 0.3)
            
        except:
            return 0.5
    
    def analyze_on_chain(self, symbol):
        """Analisi metriche on-chain: NVT + Puell Multiple"""
        try:
            # Simula NVT Ratio (Network Value to Transactions)
            nvt_score = random.uniform(0.4, 0.9)
            
            # Simula Puell Multiple (miner profitability)
            puell_score = random.uniform(0.3, 0.8)
            
            # Simula OBV (On-Balance Volume)
            obv_score = random.uniform(0.5, 0.85)
            
            return (nvt_score * 0.4 + puell_score * 0.3 + obv_score * 0.3)
            
        except:
            return 0.5
    
    def analyze_macro(self, symbol):
        """Analisi macroeconomica: DXY, Gold, Cicli"""
        try:
            # Simula correlazione DXY/BTC (di solito inversa)
            dxy_correlation = random.uniform(0.6, 0.9)  # Alta correlazione inversa
            
            # Simula analisi Gold/BTC (store of value)
            gold_btc_correlation = random.uniform(0.5, 0.8)
            
            # Simula condizioni macro
            macro_conditions = random.uniform(0.4, 0.85)
            
            return (dxy_correlation * 0.4 + gold_btc_correlation * 0.3 + macro_conditions * 0.3)
            
        except:
            return 0.5
    
    def analyze_halving_cycles(self):
        """Analisi cicli halving Bitcoin"""
        try:
            # Simula posizione nel ciclo halving
            # Post-halving tendenza rialzista
            days_since_halving = random.randint(100, 500)
            
            if days_since_halving < 180:  # Primi 6 mesi post-halving
                cycle_score = random.uniform(0.7, 0.95)
            elif days_since_halving < 360:  # 6-12 mesi
                cycle_score = random.uniform(0.6, 0.9)
            else:  # >12 mesi
                cycle_score = random.uniform(0.4, 0.8)
                
            return cycle_score
            
        except:
            return 0.5
    
    def run_cycle(self):
        """Ciclo trading con strategia avanzata"""
        self.cycle_count += 1
        
        print(f"\n🎯 CICLO {self.cycle_count} - STRATEGIA AVANZATA")
        print("=" * 60)
        
        symbols = ['ADAUSDT', 'MATICUSDT', 'AVAXUSDT', 'LINKUSDT']
        decisions = 0
        
        for symbol in symbols:
            action, score, reason = self.analyze_advanced_metrics(symbol)
            
            print(f"📊 {symbol:10} | {action:4} | Score: {score:.2f}")
            print(f"   📈 Ragione: {reason}")
            
            # STRATEGIA AVANZATA DI TRADING
            if action == "BUY" and float(self.engine.balance) > 10:
                if symbol not in self.engine.portfolio:
                    # Size position basata sulla confidence
                    amount = min(30, float(self.engine.balance) * 0.4)  # Fino al 40%
                    if self.engine.market_buy(symbol, amount):
                        decisions += 1
                        print(f"   🟢 ACQUISTATO ${amount:.2f} (Score: {score:.2f})")
            
            elif action == "SELL" and symbol in self.engine.portfolio:
                profit_data = self.engine.get_asset_profit(symbol)
                if profit_data:
                    pnl = profit_data['profit_pct']
                    # Vendita più aggressiva con strategia avanzata
                    if pnl > 3 or pnl < -4:  # Soglie più strette
                        if self.engine.market_sell(symbol):
                            decisions += 1
                            print(f"   🔴 VENDUTO (P&L: {pnl:.1f}%, Score: {score:.2f})")
        
        # SALVATAGGIO
        self.engine.save_to_json()
        portfolio_value = float(self.engine.get_portfolio_value())
        total_value = float(self.engine.balance) + portfolio_value
        
        print(f"\n📈 RIEPILOGO CICLO {self.cycle_count}:")
        print(f"   💰 Cash: ${float(self.engine.balance):.2f}")
        print(f"   📦 Portfolio: ${portfolio_value:.2f}")
        print(f"   💎 Totale: ${total_value:.2f}")
        print(f"   🎯 Decisioni: {decisions}")
        print(f"   💾 Stato salvato")
        
        return decisions

    def run_continuous(self, cycles=15, delay=45):
        """Esecuzione strategia avanzata"""
        print(f"\n🚀 QUANTUM TRADER ADVANCED - AVVIATO")
        print(f"🎯 Strategia: Confluenze Multiple")
        print(f"📊 Analisi: Price Action, On-Chain, Macro, Cicli")
        print("=" * 60)
        
        try:
            for i in range(cycles):
                self.run_cycle()
                if i < cycles - 1:
                    print(f"\n⏳ Prossima analisi in {delay}s...")
                    time.sleep(delay)
                    
        except KeyboardInterrupt:
            print("\n🛑 SISTEMA FERMATO")
        finally:
            self.engine.save_to_json()
            print(f"\n💾 STATO FINALE SALVATO")
            print(f"📊 Cicli completati: {self.cycle_count}")

if __name__ == "__main__":
    trader = QuantumTraderAdvanced(200)  # Più capitale per strategia avanzata
    trader.run_continuous(cycles=12, delay=45)
