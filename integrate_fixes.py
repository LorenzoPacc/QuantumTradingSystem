#!/usr/bin/env python3
"""
Script di integrazione automatica dei fix critici
"""

import re
import shutil
from datetime import datetime

# Backup
backup_name = f"quantum_v33_ultimate_final_BEFORE_FIXES_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy('quantum_v33_ultimate_final.py', backup_name)
print(f"✅ Backup creato: {backup_name}")

# Leggi il file
with open('quantum_v33_ultimate_final.py', 'r') as f:
    content = f.read()

# ============================================================================
# FIX 1: Aggiungi importazione
# ============================================================================
if 'from fix_critical_bugs import CriticalFixes' not in content:
    # Trova la sezione imports
    import_section = content.find('import')
    if import_section != -1:
        # Inserisci dopo gli altri import
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('import') or line.startswith('from'):
                continue
            else:
                lines.insert(i, 'from fix_critical_bugs import CriticalFixes')
                break
        content = '\n'.join(lines)
        print("✅ Import aggiunto")

# ============================================================================
# FIX 2: Aggiungi istanza CriticalFixes nella classe
# ============================================================================
if 'self.fixes = CriticalFixes()' not in content:
    # Cerca __init__ method
    init_pattern = r'(def __init__\(self[^)]*\):.*?)(def\s+\w+)'
    
    def add_fixes_init(match):
        init_body = match.group(1)
        next_method = match.group(2)
        
        # Aggiungi dopo l'init esistente
        if 'self.fixes = CriticalFixes()' not in init_body:
            # Trova l'ultimo statement dell'init
            lines = init_body.split('\n')
            # Aggiungi prima dell'ultimo def
            lines.insert(-1, '        self.fixes = CriticalFixes()  # ✅ FIX INTEGRATI')
            init_body = '\n'.join(lines)
        
        return init_body + next_method
    
    content = re.sub(init_pattern, add_fixes_init, content, flags=re.DOTALL)
    print("✅ CriticalFixes instance aggiunta")

# ============================================================================
# FIX 3: Sostituisci logica should_close_position
# ============================================================================
should_close_pattern = r'(def should_close_position\([^)]+\):.*?)((?=\n    def\s+)|(?=\nclass\s+)|$)'

new_should_close = '''def should_close_position(self, symbol, position, current_price, current_rsi):
        """
        ✅ FIXED: Trailing stop corretto con tracking max profit
        """
        # Update max tracking
        if current_price > position['max_price_reached']:
            position['max_price_reached'] = current_price
            position['max_profit_pct'] = ((current_price - position['entry_price']) / 
                                         position['entry_price']) * 100
        
        # Usa il fix corretto
        should_sell, reason = self.fixes.fix_trailing_stop_logic(
            current_price=current_price,
            entry_price=position['entry_price'],
            max_price_reached=position['max_price_reached'],
            activation_pct=8.0,
            protection_pct=0.6
        )
        
        if should_sell:
            return True, reason
        
        # Calcola giorni tenuta
        days_held = (datetime.now() - position['entry_time']).days
        current_pnl_pct = ((current_price - position['entry_price']) / 
                          position['entry_price']) * 100
        
        # Stop loss progressivo
        if days_held < 2:
            sl = -3
        elif days_held < 7:
            sl = -5
        else:
            sl = -7
        
        if current_pnl_pct <= sl:
            return True, f"Stop-loss {sl}% ({current_pnl_pct:.1f}%)"
        
        # Take profit
        if current_pnl_pct >= 15:
            return True, f"Take-profit +15% ({current_pnl_pct:.1f}%)"
        elif current_pnl_pct >= 10 and current_rsi > 75:
            return True, f"Take-profit +10%+RSI75 ({current_pnl_pct:.1f}%)"
        elif current_pnl_pct >= 5 and current_rsi > 80:
            return True, f"Take-profit +5%+RSI80 ({current_pnl_pct:.1f}%)"
        
        return False, "Hold"
    
    '''

content = re.sub(should_close_pattern, new_should_close, content, flags=re.DOTALL)
print("✅ should_close_position sostituita")

# ============================================================================
# FIX 4: Aggiungi confidence check in calculate_position_size
# ============================================================================
if 'MIN_CONFIDENCE = 60' not in content:
    # Aggiungi costante
    content = content.replace(
        'MAX_POSITIONS = 3',
        'MAX_POSITIONS = 3\n    MIN_CONFIDENCE = 60  # ✅ FIX: Soglia minima confidence'
    )
    print("✅ MIN_CONFIDENCE aggiunta")

# Aggiungi check confidence
position_size_pattern = r'(def calculate_position_size\([^)]+\):.*?)(return\s+)'

def add_confidence_check(match):
    body = match.group(1)
    return_stmt = match.group(2)
    
    if 'MIN_CONFIDENCE' not in body:
        # Aggiungi check all'inizio
        lines = body.split('\n')
        # Trova la prima linea dopo la docstring
        for i, line in enumerate(lines):
            if '"""' in line or "'''" in line:
                continue
            if line.strip() and not line.strip().startswith('#'):
                lines.insert(i + 1, '''
        # ✅ FIX: Check confidence threshold
        if confidence < self.MIN_CONFIDENCE:
            return 0.0
''')
                break
        body = '\n'.join(lines)
    
    return body + return_stmt

content = re.sub(position_size_pattern, add_confidence_check, content, flags=re.DOTALL, count=1)
print("✅ Confidence check aggiunto")

# Salva
with open('quantum_v33_ultimate_final.py', 'w') as f:
    f.write(content)

print("\n" + "="*70)
print("✅ TUTTI I FIX INTEGRATI!")
print("="*70)
print(f"\n📂 File modificato: quantum_v33_ultimate_final.py")
print(f"📂 Backup salvato: {backup_name}")
print("\n🧪 Testa con: python quantum_v33_ultimate_final.py")

