import time
from datetime import datetime
import os
from paper_trading_engine import PaperTradingEngine

class QuantumTraderPro:
    def __init__(self, initial_balance=150):
        print("🎮 Quantum Trader PRO - Inizializzazione")
        self.engine = PaperTradingEngine(initial_balance)
        
        # Tentativo di caricamento stato esistente
        if os.path.exists('paper_trading_state.json'):
            print("📂 Tentativo di caricamento stato esistente...")
            try:
                success = self.engine.load_from_json('paper_trading_state.json')
                if success:
                    print("✅ Stato esistente caricato correttamente")
                    print(f"   💰 Balance: ${float(self.engine.balance):.2f}")
                    print(f"   📦 Asset: {len(self.engine.portfolio)}")
                    print(f"   📋 Ordini: {len(self.engine.orders_history)}")
                else:
                    print("⚠️  Stato esistente non valido, uso balance iniziale")
            except Exception as e:
                print(f"❌ Errore caricamento stato: {e}")
        else:
            print("📄 Nessuno stato esistente, starting fresh")
        
        self.cycle_count = 0
        
    def analyze_market(self, symbol):
        """Analisi semplificata ma efficace"""
        try:
            current_price = self.engine.get_real_price(symbol)
            if not current_price:
                return "HOLD", 0.5
                
            import random
            score = random.uniform(0.4, 0.8)
            
            if score > 0.7: 
                return "BUY", score
            elif score < 0.4: 
                return "SELL", score
            else: 
                return "HOLD", score
                
        except Exception as e:
            return "HOLD", 0.5
    
    def run_cycle(self):
        """Ciclo di trading con logging chiaro"""
        self.cycle_count += 1
        
        print(f"\n🎯 CICLO {self.cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 50)
        
        symbols = ['ADAUSDT', 'MATICUSDT', 'AVAXUSDT', 'LINKUSDT']
        decisions = 0
        
        for symbol in symbols:
            action, score = self.analyze_market(symbol)
            status = f"📊 {symbol:10} | {action:4} | Score: {score:.2f}"
            
            if action == "BUY" and float(self.engine.balance) > 10:
                if symbol not in self.engine.portfolio:
                    amount = min(25, float(self.engine.balance) * 0.3)
                    if self.engine.market_buy(symbol, amount):
                        decisions += 1
                        print(f"{status} -> 🟢 ACQUISTATO ${amount:.2f}")
                    else:
                        print(f"{status} -> ❌ Acquisto fallito")
                else:
                    print(f"{status} -> ⏭️  Già in portfolio")
                    
            elif action == "SELL" and symbol in self.engine.portfolio:
                profit_data = self.engine.get_asset_profit(symbol)
                if profit_data:
                    pnl = profit_data['profit_pct']
                    if pnl > 5 or pnl < -8:
                        if self.engine.market_sell(symbol):
                            decisions += 1
                            print(f"{status} -> 🔴 VENDUTO (P&L: {pnl:.1f}%)")
                        else:
                            print(f"{status} -> ❌ Vendita fallita")
                    else:
                        print(f"{status} -> ⏭️  P&L {pnl:.1f}% (no trigger)")
                else:
                    print(f"{status} -> ⏭️  Dati P&L non disponibili")
            else:
                print(status)
        
        # SALVATAGGIO OBBLIGATORIO
        self.engine.save_to_json()
        portfolio_value = float(self.engine.get_portfolio_value())
        total_value = float(self.engine.balance) + portfolio_value
        
        print(f"\n📈 RIEPILOGO CICLO {self.cycle_count}:")
        print(f"   💰 Cash: ${float(self.engine.balance):.2f}")
        print(f"   📦 Portfolio: ${portfolio_value:.2f}")
        print(f"   💎 Totale: ${total_value:.2f}")
        print(f"   📋 Decisioni: {decisions}")
        print(f"   💾 Stato salvato")
        
        return decisions

    def run_continuous(self, cycles=20, delay=30):
        """Esecuzione principale"""
        print(f"\n🚀 QUANTUM TRADER PRO - AVVIATO")
        print(f"⏰ Config: {cycles} cicli, {delay}s intervallo")
        print("=" * 50)
        
        try:
            for i in range(cycles):
                self.run_cycle()
                if i < cycles - 1:
                    print(f"\n⏳ Prossimo ciclo in {delay}s...")
                    time.sleep(delay)
                    
        except KeyboardInterrupt:
            print("\n🛑 SISTEMA FERMATO DALL'UTENTE")
        except Exception as e:
            print(f"\n❌ ERRORE: {e}")
        finally:
            # SALVATAGGIO FINALE
            self.engine.save_to_json()
            print(f"\n💾 STATO FINALE SALVATO")
            print(f"📊 Cicli completati: {self.cycle_count}")
            print(f"💰 Cash finale: ${float(self.engine.balance):.2f}")
            print("🎯 Quantum Trader PRO - Terminato")

if __name__ == "__main__":
    trader = QuantumTraderPro(150)
    trader.run_continuous(cycles=10, delay=30)  # 10 cicli per test
