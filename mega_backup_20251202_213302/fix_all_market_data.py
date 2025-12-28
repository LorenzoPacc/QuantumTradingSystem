#!/usr/bin/env python3

with open('quantum_v3_enhanced.py', 'r') as f:
    lines = f.readlines()

fixed_lines = []
in_run_cycle = False

for line in lines:
    # Identifica se siamo in run_cycle
    if 'def run_cycle(self)' in line:
        in_run_cycle = True
    elif in_run_cycle and line.strip().startswith('def ') and 'run_cycle' not in line:
        in_run_cycle = False
    
    # Fix accessi market_data dentro run_cycle
    if in_run_cycle:
        # Fix: market_data['price'] -> market_data.get('5m', {}).get('price', 0)
        if "market_data['price']" in line or 'market_data.get(\'price\')' in line:
            line = line.replace(
                "market_data['price']",
                "market_data.get('5m', {}).get('price', 0)"
            ).replace(
                "market_data.get('price'",
                "market_data.get('5m', {}).get('price'"
            )
        
        # Fix: market_data['regime'] -> market_data.get('1h', {}).get('regime', 'UNKNOWN')
        if "market_data['regime']" in line or 'market_data.get(\'regime\')' in line:
            line = line.replace(
                "market_data['regime']",
                "market_data.get('1h', {}).get('regime', 'UNKNOWN')"
            ).replace(
                "market_data.get('regime'",
                "market_data.get('1h', {}).get('regime'"
            )
        
        # Fix: market_data['atr'] -> market_data.get('5m', {}).get('atr', 0)
        if "market_data['atr']" in line or 'market_data.get(\'atr\')' in line:
            line = line.replace(
                "market_data['atr']",
                "market_data.get('5m', {}).get('atr', 0)"
            ).replace(
                "market_data.get('atr'",
                "market_data.get('5m', {}).get('atr'"
            )
    
    fixed_lines.append(line)

with open('quantum_v3_enhanced.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Tutti gli accessi market_data fixati!")

import py_compile
try:
    py_compile.compile('quantum_v3_enhanced.py', doraise=True)
    print("✅ Sintassi OK")
except Exception as e:
    print(f"❌ Errore: {e}")

