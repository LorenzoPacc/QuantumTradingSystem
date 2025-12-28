import time
from datetime import datetime
from decimal import Decimal
from paper_trading_engine import PaperTradingEngine

class QuantumTraderPaperImproved:
    def __init__(self, initial_balance=150):
        self.engine = PaperTradingEngine(initial_balance)
        self.cycle_count = 0
        self.max_cycles = 50
        
    def analyze_market(self, symbol):
        """Strategia migliorata - meno aggressiva nelle vendite"""
        try:
            current_price = self.engine.get_real_price(symbol)
            if not current_price:
                return "HOLD", 0.5, "Prezzo non disponibile"
            
            # Simula analisi più sofisticata
            import random
            score = random.uniform(0.4, 0.8)  # Score più bilanciato
            
            if score > 0.7:
                return "BUY", score, f"Score alto: {score:.2f}"
            elif score < 0.4:
                return "SELL", score, f"Score basso: {score:.2f}"
            else:
                return "HOLD", score, f"Score neutro: {score:.2f}"
                
        except Exception as e:
            return "HOLD", 0.5, f"Errore analisi: {str(e)}"
    
    def run_cycle(self):
        """Ciclo trading migliorato"""
        self.cycle_count += 1
        print(f"\n{'='*60}")
        print(f"🔄 CICLO TRADING MIGLIORATO - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        symbols = ['ADAUSDT', 'MATICUSDT', 'AVAXUSDT', 'LINKUSDT']
        
        decisions_made = 0
        
        for symbol in symbols:
            action, score, reason = self.analyze_market(symbol)
            
            print(f"📊 {symbol:12} | {action:4} | Score: {score:.2f} | {reason}")
            
            # STRATEGIA MIGLIORATA:
            if action == "BUY" and float(self.engine.balance) > 10:
                # Acquista solo se non abbiamo già quell'asset
                if symbol not in self.engine.portfolio or float(self.engine.portfolio.get(symbol, 0)) == 0:
                    # CORREZIONE: Converti balance a float per il calcolo
                    amount = min(25, float(self.engine.balance) * 0.3)
                    success = self.engine.market_buy(symbol, amount)
                    if success:
                        decisions_made += 1
                        print(f"   ✅ ACQUISTATO: ${amount:.2f} di {symbol}")
            
            elif action == "SELL" and symbol in self.engine.portfolio:
                # Vendita più conservativa
                profit_data = self.engine.get_asset_profit(symbol)
                if profit_data:
                    profit_pct = profit_data['profit_pct']
                    # Vendi solo se profitto >5% o perdita >8%
                    if profit_pct > 5 or profit_pct < -8:
                        success = self.engine.market_sell(symbol)
                        if success:
                            decisions_made += 1
                            print(f"   ✅ VENDUTO: {symbol} (P&L: {profit_pct:.1f}%)")
        
        print(f"\n✅ Ciclo migliorato completato - {decisions_made} decisioni prese")
        print(f"💰 Balance: ${float(self.engine.balance):.2f}")
        print(f"📊 Portfolio: ${float(self.engine.get_portfolio_value()):.2f}")
        
        return decisions_made

    def print_status(self):
        """Stato sistema"""
        print(f"\n{'='*60}")
        print(f"📊 QUANTUM PAPER TRADING - STATO MIGLIORATO")
        print(f"{'='*60}")
        
        profit, profit_pct = self.engine.calculate_profit()
        portfolio_value = self.engine.get_portfolio_value()
        
        print(f"💵 Liquidità: ${float(self.engine.balance):.2f}")
        print(f"💼 Portfolio: ${float(portfolio_value):.2f}")
        print(f"💎 Totale: ${float(self.engine.balance + portfolio_value):.2f}")
        print(f"📈 P&L: ${float(profit):.2f} ({float(profit_pct):.2f}%)")
        print(f"📋 Ordini Totali: {len(self.engine.orders_history)}")
        print(f"💸 Fee Totali: ${float(self.engine.total_fees):.2f}")
        print(f"🔄 Cicli Completati: {self.cycle_count}")

if __name__ == "__main__":
    trader = QuantumTraderPaperImproved(150)
    
    try:
        while trader.cycle_count < trader.max_cycles:
            trader.run_cycle()
            trader.print_status()
            print(f"\n⏰ Attendo 60 secondi...")
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n🛑 Sistema fermato dall'utente")
        trader.print_status()

    def run_cycle(self):
        """Ciclo trading migliorato - CON SALVATAGGIO AUTOMATICO"""
        self.cycle_count += 1
        print(f"\n{'='*60}")
        print(f"🔄 CICLO TRADING MIGLIORATO - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        symbols = ['ADAUSDT', 'MATICUSDT', 'AVAXUSDT', 'LINKUSDT']
        
        decisions_made = 0
        
        for symbol in symbols:
            action, score, reason = self.analyze_market(symbol)
            
            print(f"📊 {symbol:12} | {action:4} | Score: {score:.2f} | {reason}")
            
            if action == "BUY" and float(self.engine.balance) > 10:
                if symbol not in self.engine.portfolio or float(self.engine.portfolio.get(symbol, 0)) == 0:
                    amount = min(25, float(self.engine.balance) * 0.3)
                    success = self.engine.market_buy(symbol, amount)
                    if success:
                        decisions_made += 1
                        print(f"   ✅ ACQUISTATO: ${amount:.2f} di {symbol}")
            
            elif action == "SELL" and symbol in self.engine.portfolio:
                profit_data = self.engine.get_asset_profit(symbol)
                if profit_data:
                    profit_pct = profit_data['profit_pct']
                    if profit_pct > 5 or profit_pct < -8:
                        success = self.engine.market_sell(symbol)
                        if success:
                            decisions_made += 1
                            print(f"   ✅ VENDUTO: {symbol} (P&L: {profit_pct:.1f}%)")
        
        # SALVATAGGIO AUTOMATICO PER LA DASHBOARD
        self.engine.save_to_json()
        print("💾 Stato salvato per la dashboard")
        
        print(f"\n✅ Ciclo migliorato completato - {decisions_made} decisioni prese")
        print(f"💰 Balance: ${float(self.engine.balance):.2f}")
        print(f"📊 Portfolio: ${float(self.engine.get_portfolio_value()):.2f}")
        
        return decisions_made
