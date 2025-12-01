#!/usr/bin/env python3
"""
ANALIZZATORE PERFORMANCE - Monitora e migliora la strategia
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta

class PerformanceAnalyzer:
    def __init__(self, db_path='quantum_final.db'):
        self.db_path = db_path
    
    def get_trading_metrics(self, days=30):
        """Calcola metriche di performance dai trade nel database"""
        conn = sqlite3.connect(self.db_path)
        
        query = """
        SELECT symbol, side, quantity, entry_price, timestamp, pnl, status
        FROM trades 
        WHERE timestamp >= datetime('now', '-{} days')
        ORDER BY timestamp
        """.format(days)
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return {"error": "Nessun trade trovato nel periodo specificato"}
        
        # Calcola metriche
        total_trades = len(df)
        winning_trades = len(df[df['pnl'] > 0])
        losing_trades = len(df[df['pnl'] < 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        total_profit = df[df['pnl'] > 0]['pnl'].sum()
        total_loss = abs(df[df['pnl'] < 0]['pnl'].sum())
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        avg_win = df[df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = df[df['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
        win_loss_ratio = avg_win / abs(avg_loss) if avg_loss != 0 else float('inf')
        
        # Drawdown
        df['cumulative_pnl'] = df['pnl'].cumsum()
        df['running_max'] = df['cumulative_pnl'].cummax()
        df['drawdown'] = df['running_max'] - df['cumulative_pnl']
        max_drawdown = df['drawdown'].max()
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'total_loss': total_loss,
            'profit_factor': profit_factor,
            'average_win': avg_win,
            'average_loss': avg_loss,
            'win_loss_ratio': win_loss_ratio,
            'max_drawdown': max_drawdown,
            'analysis_period_days': days
        }
    
    def print_detailed_report(self):
        """Stampa report dettagliato"""
        metrics = self.get_trading_metrics(30)
        
        print("📊 ANALISI PERFORMANCE DETTAGLIATA")
        print("="*50)
        
        for key, value in metrics.items():
            if isinstance(value, float):
                if 'rate' in key or 'factor' in key or 'ratio' in key:
                    print(f"{key.replace('_', ' ').title()}: {value:.2f}")
                else:
                    print(f"{key.replace('_', ' ').title()}: {value:.2f}")
            else:
                print(f"{key.replace('_', ' ').title()}: {value}")
        
        print("\n🎯 VALUTAZIONE STRATEGIA:")
        if metrics.get('win_rate', 0) >= 0.7:
            print("✅ ECCELLENTE - Win Rate >70%")
        elif metrics.get('win_rate', 0) >= 0.6:
            print("⚠️  BUONO - Win Rate 60-70% (migliorabile)")
        else:
            print("❌ DA MIGLIORARE - Win Rate <60%")
        
        if metrics.get('profit_factor', 0) >= 1.5:
            print("✅ ECCELLENTE - Profit Factor >1.5")
        elif metrics.get('profit_factor', 0) >= 1.2:
            print("⚠️  BUONO - Profit Factor 1.2-1.5")
        else:
            print("❌ RISCHIOSO - Profit Factor <1.2")

if __name__ == "__main__":
    analyzer = PerformanceAnalyzer()
    analyzer.print_detailed_report()
