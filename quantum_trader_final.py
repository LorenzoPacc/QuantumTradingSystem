import time
from datetime import datetime
import os
from paper_trading_engine import PaperTradingEngine

class QuantumTraderFinal:
    def __init__(self, initial_balance=150):
        self.engine = PaperTradingEngine(initial_balance)
        # CARICA SEMPRE STATO ESISTENTE SE PRESENTE
        if os.path.exists('paper_trading_state.json'):
            print("📂 Caricamento stato esistente...")
            self.engine.load_from_json('paper_trading_state.json')
        self.cycle_count = 0
        
    def analyze_market(self, symbol):
        """Strategia finale"""
        try:
            current_price = self.engine.get_real_price(symbol)
            if not current_price:
                return "HOLD", 0.5
            import random
            score = random.uniform(0.4, 0.8)
            if score > 0.7: return "BUY", score
            elif score < 0.4: return "SELL", score
            else: return "HOLD", score
        except:
            return "HOLD", 0.5
    
    def run_cycle(self):
        """Ciclo con backup automatico"""
        self.cycle_count += 1
        
        print(f"\n🔄 CICLO {self.cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 40)
        
        symbols = ['ADAUSDT', 'MATICUSDT', 'AVAXUSDT', 'LINKUSDT']
        
        for symbol in symbols:
            action, score = self.analyze_market(symbol)
            print(f"📊 {symbol}: {action} (Score: {score:.2f})")
            
            if action == "BUY" and float(self.engine.balance) > 10:
                if symbol not in self.engine.portfolio:
                    amount = min(25, float(self.engine.balance) * 0.3)
                    if self.engine.market_buy(symbol, amount):
                        print(f"   ✅ ACQUISTATO ${amount:.2f} {symbol}")
            
            elif action == "SELL" and symbol in self.engine.portfolio:
                profit_data = self.engine.get_asset_profit(symbol)
                if profit_data and (profit_data['profit_pct'] > 5 or profit_data['profit_pct'] < -8):
                    if self.engine.market_sell(symbol):
                        print(f"   ✅ VENDUTO {symbol}")
        
        # SALVATAGGIO OBBLIGATORIO
        self.engine.save_to_json()
        print(f"💾 STATO SALVATO - Balance: ${float(self.engine.balance):.2f}")
        
        return True

    def run_continuous(self, cycles=50, delay=60):
        """Esecuzione continua con salvataggio"""
        print("🚀 QUANTUM TRADER FINAL - AVVIATO")
        print(f"💰 Balance iniziale: ${float(self.engine.balance):.2f}")
        
        try:
            for i in range(cycles):
                self.run_cycle()
                if i < cycles - 1:
                    print(f"⏰ Attesa {delay}s...")
                    time.sleep(delay)
        except KeyboardInterrupt:
            print("\n🛑 Fermato dall'utente")
        finally:
            # SALVATAGGIO FINALE
            self.engine.save_to_json()
            print("\n💾 STATO FINALE SALVATO")
            print(f"📊 Cicli completati: {self.cycle_count}")
            print(f"💰 Balance finale: ${float(self.engine.balance):.2f}")

if __name__ == "__main__":
    trader = QuantumTraderFinal(150)
    trader.run_continuous(cycles=20, delay=30)  # Cicli più brevi per test
