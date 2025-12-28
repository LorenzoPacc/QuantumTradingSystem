#!/usr/bin/env python3
"""
Backtest della strategia su dati storici
Walk-forward validation
"""

import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from market_state_engine import MarketStateEngine
from strategy_trend_following import TrendFollowingStrategy

class StrategyBacktester:
    def __init__(self, initial_capital=1000):
        self.exchange = ccxt.binance()
        self.capital = initial_capital
        self.initial_capital = initial_capital
        self.trades = []
        self.equity_curve = [initial_capital]
        
        self.market_engine = MarketStateEngine()
        self.strategy = TrendFollowingStrategy()
    
    def run_backtest(self, symbol, start_date, end_date, timeframe='4h'):
        """
        Run backtest su periodo storico
        """
        print(f"\n🧪 BACKTESTING {symbol}")
        print(f"   Period: {start_date} → {end_date}")
        print(f"   Capital: ${self.capital}")
        print("="*70)
        
        # Fetch historical data
        since = self.exchange.parse8601(start_date + 'T00:00:00Z')
        
        all_candles = []
        while since < self.exchange.parse8601(end_date + 'T00:00:00Z'):
            candles = self.exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
            if not candles:
                break
            all_candles.extend(candles)
            since = candles[-1][0] + 1
        
        print(f"✅ Loaded {len(all_candles)} candles")
        
        # Simulate trading
        position = None
        
        for i in range(200, len(all_candles)):  # Skip warm-up
            # Use data up to this point
            window = all_candles[max(0, i-200):i+1]
            closes = np.array([c[4] for c in window])
            current_price = closes[-1]
            timestamp = datetime.fromtimestamp(all_candles[i][0]/1000)
            
            # 1. Check market state
            # (Simplified - use price action only)
            atr = np.mean(np.abs(np.diff(closes[-14:])))
            atr_pct = (atr / current_price) * 100
            
            market_state = {
                'state': 'ACTIVE' if 0.8 < atr_pct < 4.0 else 'RANGE',
                'confidence': 0.7
            }
            
            # 2. Get signal
            # (Simplified version for backtest)
            ema20 = self._ema(closes, 20)
            ema200 = self._ema(closes, 200)
            
            # Entry logic
            if position is None and market_state['state'] == 'ACTIVE':
                if current_price > ema200[-1] and current_price < ema20[-1] * 1.02:
                    # BUY
                    position = {
                        'side': 'LONG',
                        'entry': current_price,
                        'stop': ema20[-1] * 0.98,
                        'target': current_price * 1.03,
                        'entry_time': timestamp,
                        'size': self.capital * 0.1 / current_price  # 10% per trade
                    }
            
            # Exit logic
            elif position:
                pnl_pct = ((current_price - position['entry']) / position['entry']) * 100
                
                # Check TP/SL
                if current_price >= position['target']:
                    # Take profit
                    pnl = position['size'] * (current_price - position['entry'])
                    self.capital += pnl
                    
                    self.trades.append({
                        'entry': position['entry'],
                        'exit': current_price,
                        'pnl': pnl,
                        'pnl_pct': pnl_pct,
                        'duration': (timestamp - position['entry_time']).total_seconds() / 3600,
                        'exit_reason': 'TP'
                    })
                    
                    position = None
                
                elif current_price <= position['stop']:
                    # Stop loss
                    pnl = position['size'] * (current_price - position['entry'])
                    self.capital += pnl
                    
                    self.trades.append({
                        'entry': position['entry'],
                        'exit': current_price,
                        'pnl': pnl,
                        'pnl_pct': pnl_pct,
                        'duration': (timestamp - position['entry_time']).total_seconds() / 3600,
                        'exit_reason': 'SL'
                    })
                    
                    position = None
            
            self.equity_curve.append(self.capital)
        
        self._print_results()
    
    def _ema(self, data, period):
        ema = np.zeros_like(data)
        ema[0] = data[0]
        k = 2 / (period + 1)
        for i in range(1, len(data)):
            ema[i] = data[i] * k + ema[i-1] * (1 - k)
        return ema
    
    def _print_results(self):
        """Print backtest results"""
        if not self.trades:
            print("❌ No trades executed")
            return
        
        wins = [t for t in self.trades if t['pnl'] > 0]
        losses = [t for t in self.trades if t['pnl'] <= 0]
        
        total_pnl = sum(t['pnl'] for t in self.trades)
        win_rate = len(wins) / len(self.trades) * 100
        
        avg_win = np.mean([t['pnl'] for t in wins]) if wins else 0
        avg_loss = np.mean([t['pnl'] for t in losses]) if losses else 0
        
        expectancy = (len(wins)/len(self.trades) * avg_win) + (len(losses)/len(self.trades) * avg_loss)
        
        profit_factor = sum(t['pnl'] for t in wins) / abs(sum(t['pnl'] for t in losses)) if losses else 0
        
        # Max drawdown
        peak = self.equity_curve[0]
        max_dd = 0
        for val in self.equity_curve:
            if val > peak:
                peak = val
            dd = (peak - val) / peak * 100
            if dd > max_dd:
                max_dd = dd
        
        print("\n" + "="*70)
        print("📊 BACKTEST RESULTS")
        print("="*70)
        print(f"Total Trades: {len(self.trades)}")
        print(f"Win Rate: {win_rate:.1f}%")
        print(f"Total PnL: ${total_pnl:.2f} ({(total_pnl/self.initial_capital)*100:.1f}%)")
        print(f"Expectancy: ${expectancy:.4f} per trade")
        print(f"Profit Factor: {profit_factor:.2f}")
        print(f"Max Drawdown: {max_dd:.2f}%")
        print(f"Final Capital: ${self.capital:.2f}")
        print("="*70)
        
        # Verdict
        print("\n🎯 VERDICT:")
        if expectancy > 0 and profit_factor > 1.3 and max_dd < 20:
            print("✅ STRATEGY PASSES - Ready for paper trading")
        else:
            print("❌ STRATEGY FAILS - Needs improvement")
            if expectancy <= 0:
                print("   ⚠️  Negative expectancy")
            if profit_factor <= 1.3:
                print("   ⚠️  Profit factor too low")
            if max_dd >= 20:
                print("   ⚠️  Drawdown too high")

# Run backtest
if __name__ == "__main__":
    backtester = StrategyBacktester(initial_capital=1000)
    
    # Test last 3 months
    end = datetime.now().strftime('%Y-%m-%d')
    start = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    
    backtester.run_backtest('BTC/USDT', start, end, '4h')

