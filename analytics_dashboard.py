#!/usr/bin/env python3
"""Real-time Analytics Dashboard"""

import json
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

class PerformanceAnalytics:
    def __init__(self, trades_file='paper_trading_30d/trades.json'):
        self.trades_file = trades_file
    
    def generate_report(self):
        try:
            with open(self.trades_file) as f:
                trades = json.load(f)
        except:
            return "❌ No trades file found"
        
        if not trades:
            return "📊 No trades yet - bot monitoring only"
        
        df = pd.DataFrame(trades)
        
        # Metrics
        total_trades = len(df)
        wins = len(df[df['pnl'] > 0])
        win_rate = wins / total_trades * 100
        
        avg_win = df[df['pnl'] > 0]['pnl_pct'].mean() if wins > 0 else 0
        avg_loss = df[df['pnl'] < 0]['pnl_pct'].mean() if (total_trades - wins) > 0 else 0
        
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        # Sharpe (simplified)
        returns = df['pnl_pct'].values
        sharpe = ((returns.mean() / returns.std()) * (252 ** 0.5) if returns.std() > 1e-6 else 0) if len(returns) > 1 else 0
        
        # Max DD
        cumulative = df['pnl'].cumsum()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / (running_max + 1e-6)  # Percentuale
        max_dd = drawdown.min() * 100  # In percentuale
        
        return f"""
╔════════════════════════════════════════════════════════════╗
║              📊 PERFORMANCE ANALYTICS V37                  ║
╚════════════════════════════════════════════════════════════╝

📈 OVERALL STATS:
   Total Trades: {total_trades}
   Win Rate: {win_rate:.1f}% ({wins}W / {total_trades-wins}L)
   Avg Win: {avg_win:.2f}%
   Avg Loss: {avg_loss:.2f}%
   Profit Factor: {profit_factor:.2f}
   
📊 RISK METRICS:
   Sharpe Ratio: {sharpe:.2f}
   Max Drawdown: {max_dd:.2f}%
   Total PnL: ${df['pnl'].sum():.2f}
   
🎯 BEST/WORST:
   Best Trade: {df['pnl_pct'].max():.2f}% (${df['pnl'].max():.2f})
   Worst Trade: {df['pnl_pct'].min():.2f}% (${df['pnl'].min():.2f})
   
⚠️ READINESS FOR ADVANCED FEATURES:
   Trades needed: 30
   Current: {total_trades}
   Status: {"✅ READY" if total_trades >= 30 else f"❌ Need {30-total_trades} more trades"}

════════════════════════════════════════════════════════════
        """
    
if __name__ == "__main__":
    analytics = PerformanceAnalytics()
    print(analytics.generate_report())
