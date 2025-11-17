#!/usr/bin/env python3
"""
FIX CRITICO per Quantum Trader V3.0 Backtester
Problema: Dry-run non aggiorna portfolio durante backtesting
"""

import sys
import os

# Leggi il file originale
with open('quantum_v3_mvp.py', 'r') as f:
    content = f.read()

# FIX 1: Aggiorna execute_buy per backtesting
old_execute_buy = '''    def execute_buy(self, symbol: str, market_data: Dict, reason: str):
        """Esegui acquisto con V3.0 position sizing - FIXED VERSION"""
        # V3.0: Calculate available slots based on current exposure
        total_value = self.cash_balance + sum(pos['total_cost'] for pos in self.portfolio.values())
        current_exposure = 1 - (self.cash_balance / total_value) if total_value > 0 else 0
        max_exposure = self.get_max_exposure(market_data['regime'])
        
        available_exposure = max(0, max_exposure - current_exposure)
        base_size = self.cash_balance * available_exposure
        
        # Get Fear & Greed for enhanced position sizing
        fear_greed = self.get_fear_greed_index()
        volatility = market_data['atr'] / market_data['price'] if market_data['atr'] else 0.02
        
        # 🚨 CRITICAL FIX: Enhanced position sizing with Fear & Greed
        position_size = AdvancedRiskManager.calculate_position_size(
            base_size, market_data['regime'], volatility, fear_greed
        )
        position_size = min(position_size, self.cash_balance)  # Don't exceed cash
        
        price = market_data['price']
        quantity = position_size / price
        
        if self.dry_run:
            logging.info(f"[V3.0 DRY-RUN] 🟢 BUY {symbol}: ${position_size:.2f} @ ${price:.2f} | {reason}")
            alert_system.send_alert("V3.0 DRY-RUN", f"🟢 BUY {symbol}: ${position_size:.2f} | {reason}")
            return
        
        self.portfolio[symbol] = {
            'quantity': quantity, 'entry_price': price, 'total_cost': position_size,
            'entry_time': datetime.now().isoformat(), 'take_profit': price * 1.08  # Base TP
        }
        self.cash_balance -= position_size
        self._log_trade(symbol, 'BUY', price, quantity, position_size, reason, market_data)
        alert_system.alert_trade_executed(symbol, 'BUY', quantity, price, position_size, reason)
        logging.info(f"🟢 V3.0 BUY {symbol}: ${position_size:.2f} @ ${price:.2f}")'''

new_execute_buy = '''    def execute_buy(self, symbol: str, market_data: Dict, reason: str):
        """Esegui acquisto con V3.0 position sizing - FIXED VERSION"""
        # V3.0: Calculate available slots based on current exposure
        total_value = self.cash_balance + sum(pos['total_cost'] for pos in self.portfolio.values())
        current_exposure = 1 - (self.cash_balance / total_value) if total_value > 0 else 0
        max_exposure = self.get_max_exposure(market_data['regime'])
        
        available_exposure = max(0, max_exposure - current_exposure)
        base_size = self.cash_balance * available_exposure
        
        # Get Fear & Greed for enhanced position sizing
        fear_greed = self.get_fear_greed_index()
        volatility = market_data['atr'] / market_data['price'] if market_data['atr'] else 0.02
        
        # 🚨 CRITICAL FIX: Enhanced position sizing with Fear & Greed
        position_size = AdvancedRiskManager.calculate_position_size(
            base_size, market_data['regime'], volatility, fear_greed
        )
        position_size = min(position_size, self.cash_balance)  # Don't exceed cash
        
        price = market_data['price']
        quantity = position_size / price
        
        # 🚨 FIX CRITICO: In backtesting mode, aggiorna portfolio anche in dry-run
        if self.dry_run and not hasattr(self, '_backtesting_mode'):
            logging.info(f"[V3.0 DRY-RUN] 🟢 BUY {symbol}: ${position_size:.2f} @ ${price:.2f} | {reason}")
            alert_system.send_alert("V3.0 DRY-RUN", f"🟢 BUY {symbol}: ${position_size:.2f} | {reason}")
            return
        
        # 🚨 FIX: Aggiorna portfolio anche in dry-run durante backtesting
        self.portfolio[symbol] = {
            'quantity': quantity, 'entry_price': price, 'total_cost': position_size,
            'entry_time': datetime.now().isoformat(), 'take_profit': price * 1.08  # Base TP
        }
        self.cash_balance -= position_size
        
        if self.dry_run and not hasattr(self, '_backtesting_mode'):
            logging.info(f"[V3.0 DRY-RUN] 🟢 BUY {symbol}: ${position_size:.2f} @ ${price:.2f} | {reason}")
            alert_system.send_alert("V3.0 DRY-RUN", f"🟢 BUY {symbol}: ${position_size:.2f} | {reason}")
        else:
            self._log_trade(symbol, 'BUY', price, quantity, position_size, reason, market_data)
            alert_system.alert_trade_executed(symbol, 'BUY', quantity, price, position_size, reason)
            logging.info(f"🟢 V3.0 BUY {symbol}: ${position_size:.2f} @ ${price:.2f}")'''

# FIX 2: Aggiorna execute_sell per backtesting
old_execute_sell = '''    def execute_sell(self, symbol: str, market_data: Dict, reason: str):
        """Esegui vendita"""
        position = self.portfolio[symbol]
        price, quantity = market_data['price'], position['quantity']
        total_value = quantity * price
        profit_pct = ((price - position['entry_price']) / position['entry_price']) * 100
        
        if self.dry_run:
            status = "✅" if profit_pct > 0 else "🔴"
            logging.info(f"[V3.0 DRY-RUN] {status} SELL {symbol}: ${total_value:.2f} | {profit_pct:+.2f}%")
            alert_system.send_alert("V3.0 DRY-RUN", f"{status} SELL {symbol}: ${total_value:.2f} | {profit_pct:+.2f}%")
            return
        
        self.cash_balance += total_value
        del self.portfolio[symbol]
        self._log_trade(symbol, 'SELL', price, quantity, total_value, f"{reason} | P&L: {profit_pct:+.2f}%", market_data)
        alert_system.alert_trade_executed(symbol, 'SELL', quantity, price, total_value, f"{reason}")
        status = "✅" if profit_pct > 0 else "🔴"
        logging.info(f"{status} V3.0 SELL {symbol}: ${total_value:.2f} | {profit_pct:+.2f}%")'''

new_execute_sell = '''    def execute_sell(self, symbol: str, market_data: Dict, reason: str):
        """Esegui vendita"""
        position = self.portfolio[symbol]
        price, quantity = market_data['price'], position['quantity']
        total_value = quantity * price
        profit_pct = ((price - position['entry_price']) / position['entry_price']) * 100
        
        # 🚨 FIX CRITICO: In backtesting mode, aggiorna portfolio anche in dry-run
        if self.dry_run and not hasattr(self, '_backtesting_mode'):
            status = "✅" if profit_pct > 0 else "🔴"
            logging.info(f"[V3.0 DRY-RUN] {status} SELL {symbol}: ${total_value:.2f} | {profit_pct:+.2f}%")
            alert_system.send_alert("V3.0 DRY-RUN", f"{status} SELL {symbol}: ${total_value:.2f} | {profit_pct:+.2f}%")
            return
        
        # 🚨 FIX: Aggiorna portfolio anche in dry-run durante backtesting
        self.cash_balance += total_value
        del self.portfolio[symbol]
        
        if self.dry_run and not hasattr(self, '_backtesting_mode'):
            status = "✅" if profit_pct > 0 else "🔴"
            logging.info(f"[V3.0 DRY-RUN] {status} SELL {symbol}: ${total_value:.2f} | {profit_pct:+.2f}%")
            alert_system.send_alert("V3.0 DRY-RUN", f"{status} SELL {symbol}: ${total_value:.2f} | {profit_pct:+.2f}%")
        else:
            self._log_trade(symbol, 'SELL', price, quantity, total_value, f"{reason} | P&L: {profit_pct:+.2f}%", market_data)
            alert_system.alert_trade_executed(symbol, 'SELL', quantity, price, total_value, f"{reason}")
            status = "✅" if profit_pct > 0 else "🔴"
            logging.info(f"{status} V3.0 SELL {symbol}: ${total_value:.2f} | {profit_pct:+.2f}%")'''

# FIX 3: Aggiorna SimpleBacktester per gestire backtesting mode
old_backtester = '''class SimpleBacktester:
    """Backtester minimale per V3.0 - NEW ADDITION"""
    
    def __init__(self, trader: QuantumTraderV3):
        self.trader = trader
    
    def run_simple_test(self, days: int = 30):
        """Test semplice su N giorni recenti"""
        print(f"\n🧪 BACKTESTING V3.0 - Last {days} days simulation")
        print("="*50)
        
        # Simula cicli passati
        initial = self.trader.cash_balance
        cycles = days * 4  # 4 cicli al giorno (ogni 6h)
        
        for i in range(cycles):
            try:
                self.trader.run_cycle()
                time.sleep(1)  # Fast simulation
            except Exception as e:
                print(f"Cycle {i} error: {e}")
        
        final = self.trader.cash_balance
        for pos in self.trader.portfolio.values():
            final += pos['total_cost']
        
        roi = ((final - initial) / initial) * 100
        print(f"\n📊 BACKTEST RESULTS:")
        print(f"   Initial: ${initial:.2f}")
        print(f"   Final: ${final:.2f}")
        print(f"   ROI: {roi:+.2f}%")
        print(f"   Trades: {cycles} cycles simulated")
        return roi'''

new_backtester = '''class SimpleBacktester:
    """Backtester minimale per V3.0 - NEW ADDITION"""
    
    def __init__(self, trader: QuantumTraderV3):
        self.trader = trader
    
    def run_simple_test(self, days: int = 30):
        """Test semplice su N giorni recenti"""
        print(f"\n🧪 BACKTESTING V3.0 - Last {days} days simulation")
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
        
        print(f"\n📊 BACKTEST RESULTS:")
        print(f"   Initial: ${initial:.2f}")
        print(f"   Final: ${final:.2f}")
        print(f"   ROI: {roi:+.2f}%")
        print(f"   Positions: {len(self.trader.portfolio)}")
        print(f"   Cash: ${self.trader.cash_balance:.2f}")
        print(f"   Cycles: {cycles}")
        
        # Mostra dettagli posizioni
        if self.trader.portfolio:
            print(f"\n📈 FINAL POSITIONS:")
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

# Applica i fix
content = content.replace(old_execute_buy, new_execute_buy)
content = content.replace(old_execute_sell, new_execute_sell) 
content = content.replace(old_backtester, new_backtester)

# Scrivi il file fixato
with open('quantum_v3_mvp_fixed.py', 'w') as f:
    f.write(content)

print("✅ Fix applicato con successo!")
print("📁 Nuovo file: quantum_v3_mvp_fixed.py")
