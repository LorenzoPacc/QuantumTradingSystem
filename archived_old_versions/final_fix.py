#!/usr/bin/env python3
"""
ULTIMO FIX - Completa il backtesting
"""

with open('quantum_v3_mvp.py', 'r') as f:
    content = f.read()

# Fix per il backtester - riduci cicli per test veloce
old_cycles = "cycles = min(days * 4, 12)  # Max 12 cicli per test veloce"
new_cycles = "cycles = min(days * 2, 8)  # Max 8 cicli per test veloce"

# Fix per mostra progresso
old_progress = '''                print(f"  🔄 Cycle {i+1}/{cycles}...")
                self.trader.run_cycle()
                
                # Mostra stato dopo ogni ciclo
                current_cash = self.trader.cash_balance
                current_positions = len(self.trader.portfolio)
                if current_positions > positions_created:
                    positions_created = current_positions
                    print(f"     📈 Positions: {current_positions}, Cash: ${current_cash:.2f}")'''

new_progress = '''                print(f"  🔄 Cycle {i+1}/{cycles}...")
                self.trader.run_cycle()
                
                # Mostra stato dopo ogni ciclo
                current_cash = self.trader.cash_balance
                current_positions = len(self.trader.portfolio)
                total_value = current_cash + sum(pos['total_cost'] for pos in self.trader.portfolio.values())
                print(f"     💰 Cash: ${current_cash:.2f}, 📈 Positions: {current_positions}, 💎 Total: ${total_value:.2f}")'''

content = content.replace(old_cycles, new_cycles)
content = content.replace(old_progress, new_progress)

with open('quantum_v3_mvp.py', 'w') as f:
    f.write(content)

print("✅ ULTIMO FIX APPLICATO!")
