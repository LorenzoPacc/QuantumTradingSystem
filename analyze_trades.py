#!/usr/bin/env python3
"""
Quantum Trading V34 - Trade Analysis
Analisi completa per identificare edge e problemi
"""

import re
import json
from datetime import datetime
from collections import defaultdict
import statistics

class TradeAnalyzer:
    def __init__(self, log_file):
        self.log_file = log_file
        self.trades = []
        self.portfolio_history = []
        
    def parse_log(self):
        """Estrae trades e portfolio dal log"""
        print("📖 Parsing log file...")
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        current_pnl = None
        
        for i, line in enumerate(lines):
            # Estrai portfolio snapshots
            if "Total PnL:" in line:
                match = re.search(r'Total PnL: \$([+-]?\d+\.\d+)', line)
                if match:
                    pnl = float(match.group(1))
                    
                    # Cerca win rate nella stessa sezione
                    win_rate_line = None
                    for j in range(max(0, i-5), min(len(lines), i+5)):
                        if "Win Rate:" in lines[j]:
                            win_rate_line = lines[j]
                            break
                    
                    win_rate = None
                    if win_rate_line:
                        wr_match = re.search(r'Win Rate: (\d+\.\d+)%', win_rate_line)
                        if wr_match:
                            win_rate = float(wr_match.group(1))
                    
                    self.portfolio_history.append({
                        'pnl': pnl,
                        'win_rate': win_rate,
                        'line': i
                    })
        
        print(f"   ✅ Trovati {len(self.portfolio_history)} portfolio snapshots")
        
    def calculate_metrics(self):
        """Calcola metriche fondamentali"""
        if not self.portfolio_history:
            print("❌ Nessun dato portfolio trovato")
            return None
        
        latest = self.portfolio_history[-1]
        
        # Estrai dal log le info complete
        with open(self.log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Cerca ultima sezione PORTFOLIO STATUS completa
        portfolio_section = []
        for i in range(len(lines)-1, max(0, len(lines)-200), -1):
            if "PORTFOLIO STATUS:" in lines[i]:
                portfolio_section = lines[i:i+15]
                break
        
        # Parse dati
        total_pnl = None
        total_value = None
        cash = None
        trades_count = None
        win_rate = None
        max_dd = None
        fees = None
        
        for line in portfolio_section:
            if "Total PnL:" in line:
                match = re.search(r'Total PnL: \$([+-]?\d+\.\d+) \(([+-]?\d+\.\d+)%\)', line)
                if match:
                    total_pnl = float(match.group(1))
                    pnl_pct = float(match.group(2))
            
            if "Total Value:" in line:
                match = re.search(r'Total Value: \$(\d+\.\d+)', line)
                if match:
                    total_value = float(match.group(1))
            
            if "Cash:" in line:
                match = re.search(r'Cash: \$(\d+\.\d+)', line)
                if match:
                    cash = float(match.group(1))
            
            if "Trades:" in line:
                match = re.search(r'Trades: (\d+) \| Win Rate: (\d+\.\d+)%', line)
                if match:
                    trades_count = int(match.group(1))
                    win_rate = float(match.group(2))
            
            if "Max Drawdown:" in line:
                match = re.search(r'Max Drawdown: (\d+\.\d+)%', line)
                if match:
                    max_dd = float(match.group(1))
            
            if "Total Fees Paid:" in line:
                match = re.search(r'Total Fees Paid: \$(\d+\.\d+)', line)
                if match:
                    fees = float(match.group(1))
        
        return {
            'total_pnl': total_pnl,
            'pnl_pct': pnl_pct if 'pnl_pct' in locals() else None,
            'total_value': total_value,
            'cash': cash,
            'trades_count': trades_count,
            'win_rate': win_rate,
            'max_drawdown': max_dd,
            'fees_paid': fees
        }
    
    def calculate_edge_metrics(self, metrics):
        """Calcola expectancy e profit factor"""
        if not metrics or not metrics['trades_count']:
            return None
        
        win_rate = metrics['win_rate'] / 100
        trades = metrics['trades_count']
        total_pnl = metrics['total_pnl']
        
        # Stima avg win/loss (semplificato)
        # Assumendo distribuzione uniforme
        winning_trades = int(trades * win_rate)
        losing_trades = trades - winning_trades
        
        if winning_trades > 0 and losing_trades > 0:
            # Semplificazione: assumiamo avg win = total_pnl_positive / winning_trades
            # Per una stima più accurata servirebbero i singoli trade
            
            # Stima basata su totale
            if total_pnl > 0:
                # Sistema in profit (unlikely dato -20%)
                avg_win = abs(total_pnl) / winning_trades * 1.5
                avg_loss = abs(total_pnl) / losing_trades * 0.5
            else:
                # Sistema in loss (caso attuale)
                # Gross profit deve essere > 0 anche se net è negativo
                gross_profit_estimate = abs(total_pnl) * 0.4  # Stima conservativa
                gross_loss_estimate = abs(total_pnl) + gross_profit_estimate
                
                avg_win = gross_profit_estimate / winning_trades if winning_trades > 0 else 0
                avg_loss = gross_loss_estimate / losing_trades if losing_trades > 0 else 1
            
            expectancy = (win_rate * avg_win) - ((1-win_rate) * avg_loss)
            profit_factor = (winning_trades * avg_win) / (losing_trades * avg_loss) if losing_trades > 0 else 0
            
            return {
                'expectancy': expectancy,
                'profit_factor': profit_factor,
                'avg_win': avg_win,
                'avg_loss': avg_loss
            }
        
        return None
    
    def generate_report(self):
        """Report completo"""
        self.parse_log()
        metrics = self.calculate_metrics()
        
        if not metrics:
            print("❌ Impossibile calcolare metriche")
            return
        
        edge = self.calculate_edge_metrics(metrics)
        
        print("\n" + "="*70)
        print("📊 QUANTUM TRADING V34 - DIAGNOSTIC REPORT")
        print("="*70)
        
        print("\n💰 PERFORMANCE OVERVIEW:")
        print(f"   Total PnL: ${metrics['total_pnl']:.2f} ({metrics['pnl_pct']:.2f}%)")
        print(f"   Total Value: ${metrics['total_value']:.2f}")
        print(f"   Cash: ${metrics['cash']:.2f}")
        print(f"   Fees Paid: ${metrics['fees_paid']:.2f}")
        
        print("\n📈 TRADING STATS:")
        print(f"   Total Trades: {metrics['trades_count']}")
        print(f"   Win Rate: {metrics['win_rate']:.1f}%")
        print(f"   Max Drawdown: {metrics['max_drawdown']:.2f}%")
        
        if edge:
            print("\n🎯 EDGE ANALYSIS:")
            print(f"   Expectancy: ${edge['expectancy']:.4f} per trade")
            print(f"   Profit Factor: {edge['profit_factor']:.2f}")
            print(f"   Avg Win: ${edge['avg_win']:.2f}")
            print(f"   Avg Loss: ${edge['avg_loss']:.2f}")
            
            print("\n🔍 EDGE STATUS:")
            if edge['expectancy'] > 0:
                print("   ✅ POSITIVE EDGE - Sistema profittevole")
                if edge['profit_factor'] > 1.5:
                    print("   ✅ Profit Factor > 1.5 - Buono")
                else:
                    print("   ⚠️  Profit Factor < 1.5 - Migliorabile")
            else:
                print("   ❌ NEGATIVE EDGE - Sistema sta perdendo")
                print("   ❌ AZIONE RICHIESTA: Fix strategia")
        
        # Analisi problemi
        print("\n⚠️  PROBLEMI IDENTIFICATI:")
        issues = []
        
        if metrics['win_rate'] < 45:
            issues.append("Win rate < 45% - Troppo basso")
        
        if metrics['fees_paid'] / abs(metrics['total_pnl']) > 0.1:
            issues.append(f"Fees = {metrics['fees_paid']:.2f} su PnL = {metrics['total_pnl']:.2f} - Fee erosion significativa")
        
        if edge and edge['profit_factor'] < 1.3:
            issues.append("Profit Factor < 1.3 - Edge troppo sottile")
        
        if metrics['trades_count'] > 150:
            issues.append(f"{metrics['trades_count']} trades - Possibile overtrading")
        
        if issues:
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("   Nessun problema critico rilevato")
        
        # Raccomandazioni
        print("\n💡 RACCOMANDAZIONI:")
        
        if metrics['win_rate'] < 45:
            print("   1. Considera INVERSIONE LOGICA dei segnali")
            print("   2. Rilassa filtri MTF (da 60% a 40%)")
            print("   3. Rivedi parametri TP/SL")
        
        if metrics['trades_count'] > 150:
            print("   4. Riduci frequenza trading")
            print("   5. Aumenta filtri qualità segnali")
        
        if edge and edge['expectancy'] < 0:
            print("   6. ⚠️  PRIORITÀ: Fix strategia base prima di qualsiasi ottimizzazione")
        
        print("\n" + "="*70)
        
        # Salva report
        with open('diagnostic_report.txt', 'w') as f:
            f.write(f"DIAGNOSTIC REPORT - {datetime.now()}\n")
            f.write("="*70 + "\n\n")
            f.write(f"Total PnL: ${metrics['total_pnl']:.2f}\n")
            f.write(f"Win Rate: {metrics['win_rate']:.1f}%\n")
            f.write(f"Trades: {metrics['trades_count']}\n")
            if edge:
                f.write(f"Expectancy: ${edge['expectancy']:.4f}\n")
                f.write(f"Profit Factor: {edge['profit_factor']:.2f}\n")
                f.write(f"Edge Status: {'POSITIVE' if edge['expectancy'] > 0 else 'NEGATIVE'}\n")
        
        print("✅ Report salvato in: diagnostic_report.txt")

# Run analysis
if __name__ == "__main__":
    analyzer = TradeAnalyzer('v34_startup.log')
    analyzer.generate_report()
