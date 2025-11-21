import os
import sys
from paper_trading_engine import PaperTradingEngine
from datetime import datetime
import time
from decimal import Decimal

class QuantumTraderPaper:
    def __init__(self, starting_balance=150.0):
        print("🚀 QUANTUM TRADING - VERSIONE DEFINITIVA €150")
        print("="*70)
        print("💰 CAPITALE INIZIALE: €150.00")
        print("✅ Prezzi REALI da Binance")
        print("✅ Fee simulate (0.1%)")
        print("✅ Stop Loss (10%) e Take Profit (15%)")
        print("✅ Risk Management avanzato")
        print("="*70 + "\n")
        
        self.engine = PaperTradingEngine(starting_balance)
        
        # Crypto ottimizzate per €150
        self.symbols = [
            'BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'XRPUSDT',
            'SOLUSDT', 'MATICUSDT', 'AVAXUSDT', 'LINKUSDT'
        ]
        
        # Configurazione risk management
        self.stop_loss_pct = 10
        self.take_profit_pct = 15
        
        print(f"📊 Monitoraggio {len(self.symbols)} crypto")
        print(f"🛡️  Stop Loss: {self.stop_loss_pct}%")
        print(f"💎 Take Profit: {self.take_profit_pct}%")
        print(f"💰 Trade Size: €5-€30\n")

    def analyze_market_simple(self, symbol):
        data_24h = self.engine.get_real_24h_data(symbol)
        
        if not data_24h:
            return {'signal': 'HOLD', 'score': 0.5, 'reason': 'Dati non disponibili'}
        
        price = data_24h['price']
        change_pct = data_24h['priceChangePercent']
        
        # Logica migliorata per €150
        if change_pct > 3:
            signal = 'BUY'
            score = min(0.95, 0.6 + (change_pct - 3) / 100)
            reason = f"Rialzo +{float(change_pct):.2f}%"
        elif change_pct < -3:
            signal = 'SELL'
            score = max(0.3, 0.4 - abs(float(change_pct)) / 100)
            reason = f"Ribasso {float(change_pct):.2f}%"
        else:
            signal = 'HOLD'
            score = 0.5
            reason = f"Stabile {float(change_pct):+.2f}%"
        
        return {
            'signal': signal,
            'score': score,
            'price': float(price),
            'change_24h': float(change_pct),
            'reason': reason,
            'timestamp': datetime.now()
        }

    def check_risk_management(self, symbol):
        """Applica stop loss e take profit"""
        # Check Stop Loss
        stop_loss_result = self.engine.check_stop_loss(symbol, self.stop_loss_pct)
        if stop_loss_result:
            return stop_loss_result
            
        # Check Take Profit
        take_profit_result = self.engine.check_take_profit(symbol, self.take_profit_pct)
        if take_profit_result:
            return take_profit_result
            
        return None

    def auto_trade(self, symbol, analysis):
        signal = analysis.get('signal')
        score = analysis.get('score', 0)
        
        # Prima controlla risk management
        risk_result = self.check_risk_management(symbol)
        if risk_result:
            return risk_result
        
        # BUY logic per €150
        if signal == "BUY" and score >= 0.6:
            # Investi 15% del balance, max €30
            buy_amount = min(float(self.engine.balance) * 0.15, 30)
            
            if buy_amount >= 5 and float(self.engine.balance) >= buy_amount:
                print(f"\n🤖 AUTO TRADE DECISION:")
                print(f"   Signal: {signal}")
                print(f"   Score: {score:.2f}")
                print(f"   Reason: {analysis.get('reason')}")
                print(f"   Amount: €{buy_amount:.2f}")
                return self.engine.market_buy(symbol, buy_amount)
        
        # SELL logic
        if signal == "SELL" and symbol in self.engine.portfolio:
            qty = self.engine.portfolio[symbol]
            if qty > Decimal('0'):
                print(f"\n🤖 AUTO TRADE DECISION:")
                print(f"   Signal: {signal}")
                print(f"   Score: {score:.2f}")
                print(f"   Reason: {analysis.get('reason')}")
                return self.engine.market_sell(symbol, qty)
        
        return None

    def run_cycle(self):
        print(f"\n{'='*70}")
        print(f"🔄 CICLO TRADING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        trades_executed = 0
        
        for symbol in self.symbols:
            # Analizza mercato
            analysis = self.analyze_market_simple(symbol)
            
            print(f"📊 {symbol:12} | {analysis['signal']:4} | Score: {analysis['score']:.2f} | ${analysis['price']:8.2f} | {analysis['reason']}")
            
            # Trading automatico con risk management
            result = self.auto_trade(symbol, analysis)
            
            if result:
                trades_executed += 1
                time.sleep(1)  # Pausa tra ordini
        
        print(f"\n✅ Ciclo completato - {trades_executed} ordini eseguiti")
        self.engine.print_status()

    def run_test(self, cycles=5, delay=15):
        print(f"\n🎯 TEST €150 AVANZATO - {cycles} CICLI")
        print(f"   Delay: {delay}s")
        print(f"   Durata stimata: ~{cycles * delay / 60:.1f} minuti")
        print(f"   Risk Management: Stop Loss {self.stop_loss_pct}%, Take Profit {self.take_profit_pct}%\n")
        
        for i in range(cycles):
            print(f"\n{'#'*70}")
            print(f"# CICLO {i+1}/{cycles}")
            print(f"{'#'*70}")
            
            self.run_cycle()
            self.engine.save_to_json()
            
            if i < cycles - 1:
                print(f"\n⏳ Attendo {delay}s per il prossimo ciclo...\n")
                time.sleep(delay)
        
        print(f"\n{'='*70}")
        print(f"🎉 TEST COMPLETATO!")
        print(f"{'='*70}")
        
        self.engine.print_status()
        
        profit, profit_pct = self.engine.calculate_profit()
        print(f"\n📈 REPORT FINALE €150:")
        print(f"   Iniziale: ${float(self.engine.initial_balance):.2f}")
        print(f"   Finale: ${float(self.engine.get_portfolio_value()):.2f}")
        
        if profit >= Decimal('0'):
            print(f"   Risultato: +${float(profit):.2f} (+{float(profit_pct):.2f}%) 🎉")
        else:
            print(f"   Risultato: ${float(profit):.2f} ({float(profit_pct):.2f}%)")
        
        print(f"   Fee Totali: ${float(self.engine.total_fees):.4f}")
        print(f"   Ordini Totali: {len(self.engine.orders_history)}")

if __name__ == "__main__":
    print("💡 QUANTUM PAPER TRADING - VERSIONE DEFINITIVA €150\n")
    
    trader = QuantumTraderPaper(starting_balance=150.0)
    
    print("\n📚 COMANDI DISPONIBILI:")
    print("   trader.run_cycle()                    # 1 ciclo")
    print("   trader.run_test(cycles=10, delay=20)  # 10 cicli")
    print("   trader.engine.market_buy('BTCUSDT', 25)   # Compra €25 BTC")
    print("   trader.engine.market_sell('ETHUSDT')      # Vendi ETH")
    print("   trader.engine.print_status()          # Stato")
    print("   trader.engine.save_to_json()          # Salva")
    print("\n🚀 Avvio test automatico...\n")
    
    # Test con 5 cicli
    trader.run_test(cycles=5, delay=15)
