#!/usr/bin/env python3
"""Fix definitivo per il parametro fear_greed"""

# Leggi il file attuale
with open('fix_critical_bugs.py', 'r') as f:
    content = f.read()

# Trova e sostituisci la firma della funzione
old_def = '''    @staticmethod
    def fix_confidence_threshold(fg: int = None, 
                                rsi: float = 50.0, 
                                price_change: float = 0.0, 
                                min_confidence: float = 60.0) -> Tuple[bool, float, str]:'''

new_def = '''    @staticmethod
    def fix_confidence_threshold(fg: int = None, 
                                rsi: float = 50.0, 
                                price_change: float = 0.0, 
                                min_confidence: float = 60.0,
                                fear_greed: int = None) -> Tuple[bool, float, str]:'''

if old_def in content:
    content = content.replace(old_def, new_def)
    print("✅ Firma della funzione aggiornata")
    
    # Trova la docstring e aggiungi il supporto per fear_greed
    # Cerca la prima linea di codice dopo la docstring
    lines = content.split('\n')
    new_lines = []
    in_function = False
    added_compat = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # Trova l'inizio della funzione fix_confidence_threshold
        if 'def fix_confidence_threshold' in line:
            in_function = True
        
        # Aggiungi la compatibilità dopo la docstring
        if in_function and not added_compat and '"""' in line and i > 0:
            # Controlla se questa è la chiusura della docstring
            prev_lines = '\n'.join(lines[max(0, i-10):i+1])
            if prev_lines.count('"""') >= 2:
                # Aggiungi le righe di compatibilità
                new_lines.append('        # Supporta sia fg che fear_greed')
                new_lines.append('        if fear_greed is not None and fg is None:')
                new_lines.append('            fg = fear_greed')
                new_lines.append('        if fg is None:')
                new_lines.append('            fg = 50')
                added_compat = True
                in_function = False
    
    content = '\n'.join(new_lines)
    
    # Salva il file
    with open('fix_critical_bugs.py', 'w') as f:
        f.write(content)
    
    print("✅ Compatibilità aggiunta alla funzione")
else:
    print("⚠️ Pattern non trovato, uso metodo alternativo...")
    
    # Metodo alternativo: trova e modifica usando regex
    import re
    
    # Pattern per trovare la definizione
    pattern = r'(@staticmethod\s+def fix_confidence_threshold\([^)]+)\)'
    
    def replacer(match):
        return match.group(1) + ', fear_greed: int = None)'
    
    content = re.sub(pattern, replacer, content)
    
    # Aggiungi la compatibilità
    pattern2 = r'(def fix_confidence_threshold.*?""")\s*\n'
    
    def replacer2(match):
        return match.group(1) + '\n        # Supporta sia fg che fear_greed\n        if fear_greed is not None and fg is None:\n            fg = fear_greed\n        if fg is None:\n            fg = 50\n'
    
    content = re.sub(pattern2, replacer2, content, flags=re.DOTALL)
    
    with open('fix_critical_bugs.py', 'w') as f:
        f.write(content)
    
    print("✅ Fix applicato con metodo alternativo")

print("\n🧪 Test del fix...")
