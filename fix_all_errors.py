print("🔧 CORREZIONE COMPLETA ERRORI SINTASSI...")

# Leggi il file
with open('quantum_ultimate_fixed.py', 'r') as f:
    content = f.read()

# Fix 1: Corregi tutti i print(f" malformati
import re

# Trova e correggi print(f" incompleti
pattern = r'print\(f"[^"]*$'
lines = content.split('\n')
fixed_lines = []

for i, line in enumerate(lines):
    if 'print(f"' in line and line.count('"') % 2 != 0:
        # Questa riga ha un f-string non chiuso
        print(f"❌ Riga {i+1} con f-string non chiuso: {line[:50]}...")
        
        # Correggi la riga
        if 'portfolio_value' in line:
            fixed_line = '        print(f"💰 Portfolio Value: ${portfolio_value:.2f}")'
        elif 'cash_balance' in line:
            fixed_line = '        print(f"💸 Cash Balance: ${self.cash_balance:.2f}")'
        elif 'positions_active' in line:
            fixed_line = '        print(f"🎯 Active Positions: {positions_active}")'
        elif 'total_value' in line:
            fixed_line = '        print(f"💎 TOTAL: ${total_value:.2f} (+{profit:.2f} / +{profit_pct:.1f}%)")'
        elif 'buy_orders_executed' in line:
            fixed_line = '        print(f"🤖 Buy Orders Executed: {buy_orders_executed}")'
        elif 'prossimo ciclo' in line.lower():
            fixed_line = '        print(f"⏳ Prossimo ciclo in {self.cycle_delay}s...")'
        else:
            # Rimuovi semplicemente la riga problematica
            fixed_line = '# RIMOSSA: ' + line
        
        fixed_lines.append(fixed_line)
        print(f"✅ Corretto: {fixed_line}")
    else:
        fixed_lines.append(line)

# Ricostruisci il contenuto
content = '\n'.join(fixed_lines)

# Fix 2: Rimuovi caratteri di escape problematici
content = content.replace('\\$', '$')
content = content.replace('\\n', '\n')

# Fix 3: Assicurati che tutte le funzioni siano indentate correttamente
content = re.sub(r'^def ', '    def ', content, flags=re.MULTILINE)

# Salva il file corretto
with open('quantum_ultimate_fixed.py', 'w') as f:
    f.write(content)

print("✅ FILE CORRETTO!")
print("🔍 Verifica finale...")

# Testa se il file è valido
try:
    with open('quantum_ultimate_fixed.py', 'r') as f:
        compile(f.read(), 'quantum_ultimate_fixed.py', 'exec')
    print("✅ Sintassi Python valida!")
except SyntaxError as e:
    print(f"❌ Ancora errori: {e}")
