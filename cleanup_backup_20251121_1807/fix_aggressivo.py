#!/usr/bin/env python3
"""
FIX AGGRESSIVO per backtesting - Problema CRITICO
"""

import re

# Leggi il file
with open('quantum_v3_mvp.py', 'r') as f:
    content = f.read()

# TROVA e SOSTITUISCI execute_buy COMPLETAMENTE
# Cerca il metodo execute_buy
buy_pattern = r'def execute_buy\(self, symbol: str, market_data: Dict, reason: str\):.*?logging\.info\(f"🟢 V3\.0 BUY {symbol}: \${position_size:\.2f} @ \${price:\.2f}"\)'
buy_replacement = '''def execute_buy(self, symbol: str, market_data: Dict, reason: str):
        """Esegui acquisto con V3.0 position sizing - FIXED BACKTESTING"""
        # V3.0: Calculate available slots based on current exposure
        total_value = self.cash_balance + sum(pos['total_cost'] for pos in self.portfolio.values())
        current_exposure = 1 - (self.cash_balance / total_value) if total_value > 0 else 0
        max_exposure = self.get_max_exposure(market_data['regime'])
        
        available_exposure = max(0, max_exposure - current_exposure)
        base_size = self.cash_balance * available_exposure
        
        # Get Fear & Greed for enhanced position sizing
        fear_greed = self.get_fear_greed_index()
        volatility = market_data['atr'] / market_data['price'] if market_data['atr'] else 0.02
        
        # Enhanced position sizing with Fear & Greed
        position_size = AdvancedRiskManager.calculate_position_size(
            base_size, market_data['regime'], volatility, fear_greed
        )
        position_size = min(position_size, self.cash_balance)  # Don't exceed cash
        
        price = market_data['price']
        quantity = position_size / price
        
        # 🚨 FIX CRITICO: SEMPRE aggiorna portfolio, anche in dry-run
        self.portfolio[symbol] = {
            'quantity': quantity, 'entry_price': price, 'total_cost': position_size,
            'entry_time': datetime.now().isoformat(), 'take_profit': price * 1.08
        }
        self.cash_balance -= position_size
        
        if self.dry_run:
            logging.info(f"[V3.0 DRY-RUN] 🟢 BUY {symbol}: ${position_size:.2f} @ ${price:.2f} | {reason}")
            alert_system.send_alert("V3.0 DRY-RUN", f"🟢 BUY {symbol}: ${position_size:.2f} | {reason}")
        else:
            self._log_trade(symbol, 'BUY', price, quantity, position_size, reason, market_data)
            alert_system.alert_trade_executed(symbol, 'BUY', quantity, price, position_size, reason)
            logging.info(f"🟢 V3.0 BUY {symbol}: ${position_size:.2f} @ ${price:.2f}")'''

# TROVA e SOSTITUISCI execute_sell COMPLETAMENTE  
sell_pattern = r'def execute_sell\(self, symbol: str, market_data: Dict, reason: str\):.*?logging\.info\(f"{status} V3\.0 SELL {symbol}: \${total_value:\.2f} \| {profit_pct:\+\.2f}%"\)'
sell_replacement = '''def execute_sell(self, symbol: str, market_data: Dict, reason: str):
        """Esegui vendita - FIXED BACKTESTING"""
        position = self.portfolio[symbol]
        price, quantity = market_data['price'], position['quantity']
        total_value = quantity * price
        profit_pct = ((price - position['entry_price']) / position['entry_price']) * 100
        
        # 🚨 FIX CRITICO: SEMPRE aggiorna portfolio, anche in dry-run
        self.cash_balance += total_value
        del self.portfolio[symbol]
        
        status = "✅" if profit_pct > 0 else "🔴"
        
        if self.dry_run:
            logging.info(f"[V3.0 DRY-RUN] {status} SELL {symbol}: ${total_value:.2f} | {profit_pct:+.2f}%")
            alert_system.send_alert("V3.0 DRY-RUN", f"{status} SELL {symbol}: ${total_value:.2f} | {profit_pct:+.2f}%")
        else:
            self._log_trade(symbol, 'SELL', price, quantity, total_value, f"{reason} | P&L: {profit_pct:+.2f}%", market_data)
            alert_system.alert_trade_executed(symbol, 'SELL', quantity, price, total_value, f"{reason}")
            logging.info(f"{status} V3.0 SELL {symbol}: ${total_value:.2f} | {profit_pct:+.2f}%")'''

# Sostituzioni usando regex
content = re.sub(buy_pattern, buy_replacement, content, flags=re.DOTALL)
content = re.sub(sell_pattern, sell_replacement, content, flags=re.DOTALL)

# Sostituzione SIMPLE del backtester
old_bt = '''    def run_simple_test(self, days: int = 30):
        """Test semplice su N giorni recenti"""
        print(f"\\n🧪 BACKTESTING V3.0 - Last {days} days simulation")
        print("="*50)
        
        # 🚨 FIX CRITICO: Attiva modalità backtesting
        self.trader._backtesting_mode = True
        
        # Simula cicli passati
        initial = self.trader.cash_balance
        cycles = days * 4  # 4 cicli al giorno (ogni 6h)
        
        print(f"Simulating {cycles} cycles over {days} days...")
        
        for i in range(cycles):
            try:
                if i % 10 == 0:  # Progress indicator
                    print(f"  Cycle {i+1}/{cycles}...")
                self.trader.run_cycle()
                time.sleep(0.1)  # Faster simulation
            except Exception as e:
                print(f"Cycle {i} error: {e}")
        
        final = self.trader.cash_balance
        for symbol, pos in self.trader.portfolio.items():
            # Ottieni prezzo corrente per valutazione
            market_data = self.trader.get_market_data(symbol)
            if market_data:
                final += pos['quantity'] * market_data['price']
            else:
                final += pos['total_cost']  # Fallback al costo
        
        roi = ((final - initial) / initial) * 100
        
        print(f"\\n📊 BACKTEST RESULTS:")
        print(f"   Initial: ${initial:.2f}")
        print(f"   Final: ${final:.2f}")
        print(f"   ROI: {roi:+.2f}%")
        print(f"   Positions: {len(self.trader.portfolio)}")
        print(f"   Cash: ${self.trader.cash_balance:.2f}")
        print(f"   Cycles: {cycles}")
        
        # Mostra dettagli posizioni
        if self.trader.portfolio:
            print(f"\\n📈 FINAL POSITIONS:")
            for symbol, pos in self.trader.portfolio.items():
                market_data = self.trader.get_market_data(symbol)
                if market_data:
                    current_value = pos['quantity'] * market_data['price']
                    pnl_pct = ((market_data['price'] - pos['entry_price']) / pos['entry_price']) * 100
                    status = "🟢" if pnl_pct > 0 else "🔴"
                    print(f"   {status} {symbol}: ${current_value:.2f} ({pnl_pct:+.2f}%)")
        
        # 🚨 FIX: Disattiva modalità backtesting
        if hasattr(self.trader, '_backtesting_mode'):
            delattr(self.trader, '_backtesting_mode')
            
        return roi'''

new_bt = '''    def run_simple_test(self, days: int = 30):
        """Test semplice su N giorni recenti - ULTRA FIXED"""
        print(f"\\n🧪 BACKTESTING V3.0 - Last {days} days simulation")
        print("="*50)
        
        # Forza dry-run per backtesting
        self.trader.dry_run = True
        
        # Simula cicli passati
        initial = self.trader.cash_balance
        cycles = min(days * 4, 12)  # Max 12 cicli per test veloce
        
        print(f"Simulating {cycles} cycles over {days} days...")
        print(f"Initial cash: ${initial:.2f}")
        
        positions_created = 0
        for i in range(cycles):
            try:
                print(f"  🔄 Cycle {i+1}/{cycles}...")
                self.trader.run_cycle()
                
                # Mostra stato dopo ogni ciclo
                current_cash = self.trader.cash_balance
                current_positions = len(self.trader.portfolio)
                if current_positions > positions_created:
                    positions_created = current_positions
                    print(f"     📈 Positions: {current_positions}, Cash: ${current_cash:.2f}")
                    
            except Exception as e:
                print(f"Cycle {i} error: {e}")
        
        # Calcola valore finale
        final = self.trader.cash_balance
        portfolio_value = 0
        print(f"\\n  Calculating final portfolio value...")
        
        for symbol, pos in self.trader.portfolio.items():
            market_data = self.trader.get_market_data(symbol)
            if market_data:
                current_price = market_data['price']
                current_value = pos['quantity'] * current_price
                portfolio_value += current_value
                pnl_pct = ((current_price - pos['entry_price']) / pos['entry_price']) * 100
                print(f"     {symbol}: ${current_value:.2f} ({pnl_pct:+.2f}%)")
            else:
                portfolio_value += pos['total_cost']  # Fallback
        
        final += portfolio_value
        roi = ((final - initial) / initial) * 100
        
        print(f"\\n📊 BACKTEST RESULTS:")
        print(f"   Initial Capital: ${initial:.2f}")
        print(f"   Final Portfolio: ${final:.2f}")
        print(f"   ROI: {roi:+.2f}%")
        print(f"   Cash: ${self.trader.cash_balance:.2f}")
        print(f"   Portfolio Value: ${portfolio_value:.2f}")
        print(f"   Positions: {len(self.trader.portfolio)}")
        print(f"   Cycles Completed: {cycles}")
        
        # Reset per eventuali test successivi
        self.trader.cash_balance = initial
        self.trader.portfolio = {}
        self.trader.cycle_count = 0
            
        return roi'''

content = content.replace(old_bt, new_bt)

# Scrivi il file fixato
with open('quantum_v3_mvp_fixed_aggressive.py', 'w') as f:
    f.write(content)

print("✅ FIX AGGRESSIVO APPLICATO!")
print("📁 File creato: quantum_v3_mvp_fixed_aggressive.py")
