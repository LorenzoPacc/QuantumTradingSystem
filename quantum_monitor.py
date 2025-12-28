#!/usr/bin/env python3
"""
Quantum Trading Monitor - Analisi Performance Automatica
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import re
from collections import defaultdict

class QuantumMonitor:
    def __init__(self, log_file="quantum_v33_ultimate_final.log"):
        self.log_file = log_file
        self.report_file = "reports/monitor_report.txt"
        Path("reports").mkdir(exist_ok=True)
        
    def parse_log(self, hours=24):
        """Parse log degli ultimi N ore"""
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            return []
        
        # Filtra ultimi N ore
        cutoff = datetime.now() - timedelta(hours=hours)
        filtered = []
        
        for line in lines:
            try:
                # Estrai timestamp
                match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                if match:
                    ts = datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
                    if ts >= cutoff:
                        filtered.append(line)
            except:
                continue
        
        return filtered
    
    def analyze_trades(self, lines):
        """Analizza trade eseguiti"""
        trades = {
            'buy': [],
            'sell': []
        }
        
        for line in lines:
            # BUY
            if 'BUY ' in line and '@' in line:
                match = re.search(r'BUY ([A-Z]+/USDT) @ \$([0-9.]+)', line)
                if match:
                    trades['buy'].append({
                        'symbol': match.group(1),
                        'price': float(match.group(2)),
                        'time': line[:19]
                    })
            
            # SELL
            if 'SELL' in line or 'TRAILING' in line or 'TAKE_PROFIT' in line or 'STOP_LOSS' in line:
                match = re.search(r'([A-Z]+/USDT).*?([+-]\d+\.\d+)%', line)
                if match:
                    trades['sell'].append({
                        'symbol': match.group(1),
                        'pnl': float(match.group(2)),
                        'time': line[:19]
                    })
        
        return trades
    
    def analyze_mtf(self, lines):
        """Analizza MTF alignment"""
        mtf_stats = {
            'checks': 0,
            'passed': 0,
            'failed': 0,
            'alignments': []
        }
        
        for line in lines:
            if 'Alignment:' in line and '%' in line:
                mtf_stats['checks'] += 1
                
                match = re.search(r'(\d+)% (✅|❌)', line)
                if match:
                    alignment = int(match.group(1))
                    mtf_stats['alignments'].append(alignment)
                    
                    if match.group(2) == '✅':
                        mtf_stats['passed'] += 1
                    else:
                        mtf_stats['failed'] += 1
        
        return mtf_stats
    
    def get_portfolio_stats(self, lines):
        """Estrai ultime stats portfolio"""
        stats = {}
        
        for line in reversed(lines):
            if 'Total PnL:' in line:
                match = re.search(r'PnL: \$([+-]?\d+\.\d+) \(([+-]?\d+\.\d+)%\)', line)
                if match:
                    stats['pnl_usd'] = float(match.group(1))
                    stats['pnl_pct'] = float(match.group(2))
                    break
        
        for line in reversed(lines):
            if 'Win Rate:' in line:
                match = re.search(r'Win Rate: (\d+\.\d+)%', line)
                if match:
                    stats['win_rate'] = float(match.group(1))
                    break
        
        for line in reversed(lines):
            if 'Max Drawdown:' in line:
                match = re.search(r'Max Drawdown: (\d+\.\d+)%', line)
                if match:
                    stats['max_dd'] = float(match.group(1))
                    break
        
        for line in reversed(lines):
            if 'Trades:' in line:
                match = re.search(r'Trades: (\d+)', line)
                if match:
                    stats['total_trades'] = int(match.group(1))
                    break
        
        for line in reversed(lines):
            if 'Cash:' in line:
                match = re.search(r'Cash: \$(\d+\.\d+)', line)
                if match:
                    stats['cash'] = float(match.group(1))
                    break
        
        return stats
    
    def calculate_metrics(self, trades, mtf_stats, hours=24):
        """Calcola metriche chiave"""
        metrics = {
            'period_hours': hours,
            'total_buys': len(trades['buy']),
            'total_sells': len(trades['sell']),
            'mtf_pass_rate': 0,
            'avg_alignment': 0
        }
        
        # MTF stats
        if mtf_stats['checks'] > 0:
            metrics['mtf_pass_rate'] = (mtf_stats['passed'] / mtf_stats['checks']) * 100
        
        if mtf_stats['alignments']:
            metrics['avg_alignment'] = sum(mtf_stats['alignments']) / len(mtf_stats['alignments'])
        
        # Trade PnL
        if trades['sell']:
            wins = [t for t in trades['sell'] if t['pnl'] > 0]
            losses = [t for t in trades['sell'] if t['pnl'] <= 0]
            
            metrics['period_wins'] = len(wins)
            metrics['period_losses'] = len(losses)
            metrics['period_wr'] = (len(wins) / len(trades['sell'])) * 100 if trades['sell'] else 0
            
            if wins:
                metrics['avg_win'] = sum(t['pnl'] for t in wins) / len(wins)
            if losses:
                metrics['avg_loss'] = sum(t['pnl'] for t in losses) / len(losses)
        
        return metrics
    
    def generate_report(self, hours=24):
        """Genera report completo"""
        lines = self.parse_log(hours)
        
        if not lines:
            return "❌ No log data available"
        
        trades = self.analyze_trades(lines)
        mtf_stats = self.analyze_mtf(lines)
        portfolio = self.get_portfolio_stats(lines)
        metrics = self.calculate_metrics(trades, mtf_stats, hours)
        
        # Header
        report = []
        report.append("╔══════════════════════════════════════════════════════════════╗")
        report.append("║         📊 QUANTUM TRADING - PERFORMANCE REPORT         ║")
        report.append("╚══════════════════════════════════════════════════════════════╝")
        report.append(f"\n📅 Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"⏰ Period: Last {hours} hours\n")
        
        # Portfolio Status
        report.append("═" * 64)
        report.append("💼 PORTFOLIO STATUS")
        report.append("═" * 64)
        
        if portfolio:
            pnl_icon = "📈" if portfolio.get('pnl_pct', 0) > 0 else "📉"
            report.append(f"{pnl_icon} PnL: ${portfolio.get('pnl_usd', 0):.2f} ({portfolio.get('pnl_pct', 0):+.2f}%)")
            report.append(f"💰 Cash: ${portfolio.get('cash', 0):.2f}")
            report.append(f"📊 Total Trades: {portfolio.get('total_trades', 0)}")
            report.append(f"🎯 Win Rate: {portfolio.get('win_rate', 0):.1f}%")
            report.append(f"⚠️  Max Drawdown: {portfolio.get('max_dd', 0):.2f}%")
        
        # Period Activity
        report.append(f"\n{'═' * 64}")
        report.append(f"📈 ACTIVITY ({hours}H)")
        report.append("═" * 64)
        report.append(f"🟢 Buys: {metrics['total_buys']}")
        report.append(f"🔴 Sells: {metrics['total_sells']}")
        
        if 'period_wr' in metrics:
            wr_icon = "✅" if metrics['period_wr'] >= 50 else "⚠️" if metrics['period_wr'] >= 40 else "❌"
            report.append(f"{wr_icon} Period Win Rate: {metrics['period_wr']:.1f}% ({metrics.get('period_wins', 0)}W/{metrics.get('period_losses', 0)}L)")
            
            if 'avg_win' in metrics:
                report.append(f"💚 Avg Win: +{metrics['avg_win']:.2f}%")
            if 'avg_loss' in metrics:
                report.append(f"💔 Avg Loss: {metrics['avg_loss']:.2f}%")
        
        # MTF Analysis
        report.append(f"\n{'═' * 64}")
        report.append("📊 MULTI-TIMEFRAME ANALYSIS")
        report.append("═" * 64)
        report.append(f"🔍 Total Checks: {mtf_stats['checks']}")
        report.append(f"✅ Passed: {mtf_stats['passed']}")
        report.append(f"❌ Failed: {mtf_stats['failed']}")
        
        if mtf_stats['checks'] > 0:
            pass_icon = "🎯" if metrics['mtf_pass_rate'] >= 20 else "⚠️" if metrics['mtf_pass_rate'] >= 10 else "❌"
            report.append(f"{pass_icon} Pass Rate: {metrics['mtf_pass_rate']:.1f}%")
            report.append(f"📈 Avg Alignment: {metrics['avg_alignment']:.0f}%")
        
        # Recommendations
        report.append(f"\n{'═' * 64}")
        report.append("💡 RECOMMENDATIONS")
        report.append("═" * 64)
        
        recs = []
        
        # Win rate recommendations
        if portfolio.get('win_rate', 0) < 35:
            recs.append("⚠️  Win Rate < 35% - Consider more selective entries")
        elif portfolio.get('win_rate', 0) >= 50:
            recs.append("✅ Win Rate > 50% - Strategy performing well!")
        
        # MTF recommendations
        if metrics['mtf_pass_rate'] < 5:
            recs.append("🐻 MTF Pass Rate < 5% - Market is strongly bearish, patience!")
        elif metrics['mtf_pass_rate'] > 30:
            recs.append("🐂 MTF Pass Rate > 30% - Market showing bullish signs")
        
        # Drawdown
        if portfolio.get('max_dd', 0) > 25:
            recs.append("🚨 Drawdown > 25% - Consider reducing position sizes")
        
        # Activity
        if metrics['total_buys'] == 0 and hours >= 12:
            recs.append("💤 No buys in {hours}h - MTF filtering properly or market bearish")
        
        if not recs:
            recs.append("✅ System operating normally, no issues detected")
        
        for rec in recs:
            report.append(f"   {rec}")
        
        # Footer
        report.append(f"\n{'═' * 64}")
        report.append("📊 Next report in 6 hours")
        report.append("🔔 Check ~/trading_project/QuantumTradingSystem/reports/")
        report.append("═" * 64)
        
        return "\n".join(report)
    
    def save_report(self, report):
        """Salva report su file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reports/report_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(report)
        
        # Salva anche come latest
        with open(self.report_file, 'w') as f:
            f.write(report)
        
        return filename

if __name__ == "__main__":
    import sys
    
    hours = 24
    if len(sys.argv) > 1:
        hours = int(sys.argv[1])
    
    monitor = QuantumMonitor()
    report = monitor.generate_report(hours)
    
    print(report)
    
    filename = monitor.save_report(report)
    print(f"\n💾 Report saved: {filename}")
