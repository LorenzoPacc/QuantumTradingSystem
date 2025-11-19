#!/bin/bash

echo "📊 QUANTUM V3.1 - PERFORMANCE ANALYTICS ENGINE"
echo "=============================================="
echo ""

# STEP 1: Crea Performance Analytics Engine
echo "🔧 Step 1: Creazione Performance Analytics Engine..."

cat > quantum_performance_analytics.py << 'PYEOF'
#!/usr/bin/env python3
"""
📊 PERFORMANCE ANALYTICS ENGINE - QUANTUM V3.1
Sistema completo di analisi performance trading
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import logging

class PerformanceAnalyticsEngine:
    """
    📊 Engine completo per analisi performance
    """
    
    def __init__(self, db_path="quantum_v2_performance.db"):
        self.db_path = db_path
        self.logger = logging.getLogger("PerformanceAnalytics")
        
    def calculate_all_metrics(self, lookback_days=30) -> Dict:
        """
        Calcola tutte le metriche di performance
        """
        trades = self._load_trades(lookback_days)
        
        if len(trades) == 0:
            return self._empty_metrics()
        
        metrics = {
            # Risk Metrics
            'sharpe_ratio': self._calculate_sharpe_ratio(trades),
            'sortino_ratio': self._calculate_sortino_ratio(trades),
            'max_drawdown': self._calculate_max_drawdown(trades),
            'max_drawdown_duration': self._calculate_dd_duration(trades),
            'calmar_ratio': self._calculate_calmar_ratio(trades),
            
            # Performance Metrics
            'total_trades': len(trades),
            'winning_trades': len([t for t in trades if t['pnl'] > 0]),
            'losing_trades': len([t for t in trades if t['pnl'] <= 0]),
            'win_rate': self._calculate_win_rate(trades),
            'profit_factor': self._calculate_profit_factor(trades),
            'expectancy': self._calculate_expectancy(trades),
            
            # P&L Metrics
            'total_pnl': sum(t['pnl'] for t in trades),
            'avg_win': self._calculate_avg_win(trades),
            'avg_loss': self._calculate_avg_loss(trades),
            'largest_win': max([t['pnl'] for t in trades]),
            'largest_loss': min([t['pnl'] for t in trades]),
            'avg_pnl': np.mean([t['pnl'] for t in trades]),
            
            # Timing Metrics
            'avg_hold_time': self._calculate_avg_hold_time(trades),
            'best_entry_hours': self._find_best_hours(trades, 'entry'),
            'best_exit_hours': self._find_best_hours(trades, 'exit'),
            
            # Symbol Performance
            'best_symbols': self._rank_symbols(trades)[:3],
            'worst_symbols': self._rank_symbols(trades)[-3:],
            
            # Advanced Metrics
            'consecutive_wins': self._max_consecutive(trades, win=True),
            'consecutive_losses': self._max_consecutive(trades, win=False),
            'recovery_factor': self._calculate_recovery_factor(trades),
            'ulcer_index': self._calculate_ulcer_index(trades),
        }
        
        return metrics
    
    def _load_trades(self, lookback_days: int) -> List[Dict]:
        """Carica trades dal database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=lookback_days)).isoformat()
            
            cursor.execute("""
                SELECT symbol, action, price, quantity, total, timestamp, notes
                FROM trades
                WHERE timestamp >= ?
                ORDER BY timestamp
            """, (cutoff_date,))
            
            trades_raw = cursor.fetchall()
            conn.close()
            
            # Pair BUY/SELL trades
            trades = []
            positions = {}
            
            for trade in trades_raw:
                symbol, action, price, quantity, total, timestamp, notes = trade
                
                if action == 'BUY':
                    positions[symbol] = {
                        'entry_price': price,
                        'quantity': quantity,
                        'entry_time': timestamp,
                        'entry_total': total
                    }
                elif action == 'SELL' and symbol in positions:
                    entry = positions[symbol]
                    pnl = total - entry['entry_total']
                    pnl_pct = (pnl / entry['entry_total']) * 100
                    
                    hold_time = self._calculate_hold_duration(
                        entry['entry_time'], 
                        timestamp
                    )
                    
                    trades.append({
                        'symbol': symbol,
                        'entry_price': entry['entry_price'],
                        'exit_price': price,
                        'quantity': quantity,
                        'pnl': pnl,
                        'pnl_pct': pnl_pct,
                        'entry_time': entry['entry_time'],
                        'exit_time': timestamp,
                        'hold_time': hold_time,
                        'exit_reason': notes
                    })
                    
                    del positions[symbol]
            
            return trades
            
        except Exception as e:
            self.logger.error(f"Error loading trades: {e}")
            return []
    
    def _calculate_sharpe_ratio(self, trades: List[Dict]) -> float:
        """Sharpe Ratio (annualized)"""
        if len(trades) < 2:
            return 0.0
        
        returns = [t['pnl_pct'] / 100 for t in trades]
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        # Annualize (assume ~252 trading days, ~50 trades/year)
        sharpe = (mean_return / std_return) * np.sqrt(50)
        
        return round(sharpe, 2)
    
    def _calculate_sortino_ratio(self, trades: List[Dict]) -> float:
        """Sortino Ratio (only downside deviation)"""
        if len(trades) < 2:
            return 0.0
        
        returns = [t['pnl_pct'] / 100 for t in trades]
        mean_return = np.mean(returns)
        
        # Downside deviation (only negative returns)
        downside_returns = [r for r in returns if r < 0]
        
        if len(downside_returns) == 0:
            return float('inf')
        
        downside_std = np.std(downside_returns)
        
        if downside_std == 0:
            return 0.0
        
        sortino = (mean_return / downside_std) * np.sqrt(50)
        
        return round(sortino, 2)
    
    def _calculate_max_drawdown(self, trades: List[Dict]) -> float:
        """Maximum Drawdown %"""
        if len(trades) == 0:
            return 0.0
        
        cumulative = 0
        peak = 0
        max_dd = 0
        
        for trade in trades:
            cumulative += trade['pnl_pct']
            peak = max(peak, cumulative)
            drawdown = peak - cumulative
            max_dd = max(max_dd, drawdown)
        
        return round(max_dd, 2)
    
    def _calculate_dd_duration(self, trades: List[Dict]) -> int:
        """Max Drawdown Duration (days)"""
        if len(trades) == 0:
            return 0
        
        cumulative = 0
        peak = 0
        current_dd_start = None
        max_duration = 0
        
        for trade in trades:
            cumulative += trade['pnl_pct']
            
            if cumulative >= peak:
                peak = cumulative
                current_dd_start = None
            else:
                if current_dd_start is None:
                    current_dd_start = trade['exit_time']
                
                duration = (datetime.fromisoformat(trade['exit_time']) - 
                           datetime.fromisoformat(current_dd_start)).days
                max_duration = max(max_duration, duration)
        
        return max_duration
    
    def _calculate_calmar_ratio(self, trades: List[Dict]) -> float:
        """Calmar Ratio = Annual Return / Max Drawdown"""
        if len(trades) == 0:
            return 0.0
        
        total_return = sum(t['pnl_pct'] for t in trades)
        max_dd = self._calculate_max_drawdown(trades)
        
        if max_dd == 0:
            return 0.0
        
        # Annualize return
        days = (datetime.fromisoformat(trades[-1]['exit_time']) - 
                datetime.fromisoformat(trades[0]['entry_time'])).days
        
        if days == 0:
            return 0.0
        
        annual_return = (total_return / days) * 365
        
        calmar = annual_return / max_dd
        
        return round(calmar, 2)
    
    def _calculate_win_rate(self, trades: List[Dict]) -> float:
        """Win Rate %"""
        if len(trades) == 0:
            return 0.0
        
        wins = len([t for t in trades if t['pnl'] > 0])
        
        return round((wins / len(trades)) * 100, 2)
    
    def _calculate_profit_factor(self, trades: List[Dict]) -> float:
        """Profit Factor = Gross Profit / Gross Loss"""
        gross_profit = sum(t['pnl'] for t in trades if t['pnl'] > 0)
        gross_loss = abs(sum(t['pnl'] for t in trades if t['pnl'] < 0))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        return round(gross_profit / gross_loss, 2)
    
    def _calculate_expectancy(self, trades: List[Dict]) -> float:
        """Expectancy = (Win% × Avg Win) - (Loss% × Avg Loss)"""
        if len(trades) == 0:
            return 0.0
        
        wins = [t['pnl_pct'] for t in trades if t['pnl'] > 0]
        losses = [abs(t['pnl_pct']) for t in trades if t['pnl'] < 0]
        
        win_rate = len(wins) / len(trades)
        loss_rate = len(losses) / len(trades)
        
        avg_win = np.mean(wins) if wins else 0
        avg_loss = np.mean(losses) if losses else 0
        
        expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)
        
        return round(expectancy, 2)
    
    def _calculate_avg_win(self, trades: List[Dict]) -> float:
        """Average Winning Trade %"""
        wins = [t['pnl_pct'] for t in trades if t['pnl'] > 0]
        
        return round(np.mean(wins), 2) if wins else 0.0
    
    def _calculate_avg_loss(self, trades: List[Dict]) -> float:
        """Average Losing Trade %"""
        losses = [t['pnl_pct'] for t in trades if t['pnl'] < 0]
        
        return round(np.mean(losses), 2) if losses else 0.0
    
    def _calculate_avg_hold_time(self, trades: List[Dict]) -> str:
        """Average Hold Time"""
        if len(trades) == 0:
            return "0h 0m"
        
        hold_times = [t['hold_time'] for t in trades]
        avg_seconds = np.mean(hold_times)
        
        hours = int(avg_seconds // 3600)
        minutes = int((avg_seconds % 3600) // 60)
        
        return f"{hours}h {minutes}m"
    
    def _calculate_hold_duration(self, entry_time: str, exit_time: str) -> int:
        """Calculate hold duration in seconds"""
        entry = datetime.fromisoformat(entry_time)
        exit = datetime.fromisoformat(exit_time)
        
        return int((exit - entry).total_seconds())
    
    def _find_best_hours(self, trades: List[Dict], time_type: str) -> List[int]:
        """Find best hours for entry/exit"""
        if len(trades) == 0:
            return []
        
        time_key = f'{time_type}_time'
        hour_performance = {}
        
        for trade in trades:
            hour = datetime.fromisoformat(trade[time_key]).hour
            
            if hour not in hour_performance:
                hour_performance[hour] = []
            
            hour_performance[hour].append(trade['pnl_pct'])
        
        # Calculate average P&L per hour
        hour_avg = {
            hour: np.mean(pnls) 
            for hour, pnls in hour_performance.items()
        }
        
        # Sort by performance
        sorted_hours = sorted(hour_avg.items(), key=lambda x: x[1], reverse=True)
        
        # Return top 3 hours
        return [hour for hour, _ in sorted_hours[:3]]
    
    def _rank_symbols(self, trades: List[Dict]) -> List[tuple]:
        """Rank symbols by performance"""
        symbol_performance = {}
        
        for trade in trades:
            symbol = trade['symbol']
            
            if symbol not in symbol_performance:
                symbol_performance[symbol] = []
            
            symbol_performance[symbol].append(trade['pnl_pct'])
        
        # Calculate average P&L per symbol
        symbol_avg = {
            symbol: np.mean(pnls)
            for symbol, pnls in symbol_performance.items()
        }
        
        # Sort by performance
        sorted_symbols = sorted(symbol_avg.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_symbols
    
    def _max_consecutive(self, trades: List[Dict], win: bool) -> int:
        """Maximum consecutive wins/losses"""
        if len(trades) == 0:
            return 0
        
        current_streak = 0
        max_streak = 0
        
        for trade in trades:
            is_win = trade['pnl'] > 0
            
            if is_win == win:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def _calculate_recovery_factor(self, trades: List[Dict]) -> float:
        """Recovery Factor = Net Profit / Max Drawdown"""
        if len(trades) == 0:
            return 0.0
        
        net_profit = sum(t['pnl'] for t in trades)
        max_dd_pct = self._calculate_max_drawdown(trades)
        
        if max_dd_pct == 0:
            return 0.0
        
        # Assuming $200 starting capital
        max_dd_dollars = (max_dd_pct / 100) * 200
        
        if max_dd_dollars == 0:
            return 0.0
        
        recovery = net_profit / max_dd_dollars
        
        return round(recovery, 2)
    
    def _calculate_ulcer_index(self, trades: List[Dict]) -> float:
        """Ulcer Index - measures depth and duration of drawdowns"""
        if len(trades) == 0:
            return 0.0
        
        cumulative = 0
        peak = 0
        squared_drawdowns = []
        
        for trade in trades:
            cumulative += trade['pnl_pct']
            peak = max(peak, cumulative)
            
            if peak > 0:
                drawdown_pct = ((peak - cumulative) / peak) * 100
                squared_drawdowns.append(drawdown_pct ** 2)
        
        if not squared_drawdowns:
            return 0.0
        
        ulcer = np.sqrt(np.mean(squared_drawdowns))
        
        return round(ulcer, 2)
    
    def _empty_metrics(self) -> Dict:
        """Return empty metrics when no trades"""
        return {
            'sharpe_ratio': 0.0,
            'sortino_ratio': 0.0,
            'max_drawdown': 0.0,
            'max_drawdown_duration': 0,
            'calmar_ratio': 0.0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'expectancy': 0.0,
            'total_pnl': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'largest_win': 0.0,
            'largest_loss': 0.0,
            'avg_pnl': 0.0,
            'avg_hold_time': '0h 0m',
            'best_entry_hours': [],
            'best_exit_hours': [],
            'best_symbols': [],
            'worst_symbols': [],
            'consecutive_wins': 0,
            'consecutive_losses': 0,
            'recovery_factor': 0.0,
            'ulcer_index': 0.0
        }
    
    def print_report(self, metrics: Dict):
        """Print formatted performance report"""
        print("\n" + "="*60)
        print("📊 QUANTUM V3.1 - PERFORMANCE ANALYTICS REPORT")
        print("="*60)
        
        print(f"\n🎯 RISK METRICS:")
        print(f"   Sharpe Ratio:        {metrics['sharpe_ratio']}")
        print(f"   Sortino Ratio:       {metrics['sortino_ratio']}")
        print(f"   Max Drawdown:        {metrics['max_drawdown']}%")
        print(f"   DD Duration:         {metrics['max_drawdown_duration']} days")
        print(f"   Calmar Ratio:        {metrics['calmar_ratio']}")
        print(f"   Ulcer Index:         {metrics['ulcer_index']}")
        
        print(f"\n📈 PERFORMANCE METRICS:")
        print(f"   Total Trades:        {metrics['total_trades']}")
        print(f"   Winning Trades:      {metrics['winning_trades']}")
        print(f"   Losing Trades:       {metrics['losing_trades']}")
        print(f"   Win Rate:            {metrics['win_rate']}%")
        print(f"   Profit Factor:       {metrics['profit_factor']}")
        print(f"   Expectancy:          {metrics['expectancy']}%")
        
        print(f"\n💰 P&L METRICS:")
        print(f"   Total P&L:           ${metrics['total_pnl']:.2f}")
        print(f"   Average Win:         {metrics['avg_win']}%")
        print(f"   Average Loss:        {metrics['avg_loss']}%")
        print(f"   Largest Win:         ${metrics['largest_win']:.2f}")
        print(f"   Largest Loss:        ${metrics['largest_loss']:.2f}")
        print(f"   Average P&L:         ${metrics['avg_pnl']:.2f}")
        
        print(f"\n⏱️  TIMING METRICS:")
        print(f"   Avg Hold Time:       {metrics['avg_hold_time']}")
        print(f"   Best Entry Hours:    {metrics['best_entry_hours']}")
        print(f"   Best Exit Hours:     {metrics['best_exit_hours']}")
        
        print(f"\n📊 SYMBOL PERFORMANCE:")
        print(f"   Best Symbols:        {metrics['best_symbols']}")
        print(f"   Worst Symbols:       {metrics['worst_symbols']}")
        
        print(f"\n🔄 STREAKS:")
        print(f"   Max Consecutive Wins:   {metrics['consecutive_wins']}")
        print(f"   Max Consecutive Losses: {metrics['consecutive_losses']}")
        print(f"   Recovery Factor:        {metrics['recovery_factor']}")
        
        print("\n" + "="*60)


# CLI for manual testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Quantum Performance Analytics')
    parser.add_argument('--days', type=int, default=30, help='Lookback days (default: 30)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    engine = PerformanceAnalyticsEngine()
    metrics = engine.calculate_all_metrics(lookback_days=args.days)
    
    if args.json:
        print(json.dumps(metrics, indent=2))
    else:
        engine.print_report(metrics)
PYEOF

echo "✅ quantum_performance_analytics.py creato!"

# STEP 2: Test Analytics Engine
echo ""
echo "🧪 Step 2: Test Performance Analytics..."
python3 quantum_performance_analytics.py --days 30

# STEP 3: Integra nel sistema principale
echo ""
echo "🔧 Step 3: Integrazione nel sistema..."

cat > integrate_analytics.py << 'INTEGRATE_EOF'
#!/usr/bin/env python3
"""
Integra Performance Analytics in Quantum V3.1
"""

# Verifica che il file esista
import os
if not os.path.exists('quantum_v31_wrapper.py'):
    print("❌ quantum_v31_wrapper.py non trovato!")
    print("   Analytics engine creato, ma non integrato automaticamente")
    print("   Puoi usarlo manualmente con:")
    print("   python3 quantum_performance_analytics.py")
    exit(0)

print("✅ Analytics Engine pronto!")
print("")
print("📊 USO:")
print("   # Report completo ultimi 30 giorni:")
print("   python3 quantum_performance_analytics.py")
print("")
print("   # Report ultimi 7 giorni:")
print("   python3 quantum_performance_analytics.py --days 7")
print("")
print("   # Output JSON:")
print("   python3 quantum_performance_analytics.py --json")
print("")
print("🎯 PROSSIMI STEP:")
print("   1. Lascia girare il bot 3-7 giorni")
print("   2. Esegui analytics per vedere metriche")
print("   3. Decidi ottimizzazioni basate su dati")

INTEGRATE_EOF

python3 integrate_analytics.py

echo ""
echo "✅ INSTALLAZIONE COMPLETATA!"
echo ""
echo "📊 COMANDI DISPONIBILI:"
echo "   python3 quantum_performance_analytics.py           # Report 30 giorni"
echo "   python3 quantum_performance_analytics.py --days 7  # Report 7 giorni"
echo "   python3 quantum_performance_analytics.py --json    # Output JSON"
echo ""
