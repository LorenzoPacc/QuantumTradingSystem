#!/usr/bin/env python3
"""
🔍 TROVA DOVE È IL BUG NEGLI ACQUISTI
"""

import os

print("🔍 CERCA BUG ACQUISTI IN TUTTI I FILE...")
print("=" * 50)

files_to_check = [
    'quantum_v31_wrapper.py',
    'quantum_v3_enhanced.py', 
    'quantum_trader_v2.py'
]

for file in files_to_check:
    if os.path.exists(file):
        print(f"\n📁 {file}:")
        with open(file, 'r') as f:
            content = f.read()
            
        # Cerca pattern di acquisto
        if "BUY" in content and "DOTUSDT" in content:
            print("   ✅ Contiene log BUY")
            
        if "portfolio" in content and "cash_balance" in content:
            print("   ✅ Gestisce portfolio e cash")
            
        # Cerca dove logga vs dove aggiorna
        buy_lines = []
        for i, line in enumerate(content.split('\n'), 1):
            if "BUY" in line and "DOTUSDT" in line:
                buy_lines.append(f"   Linea {i}: {line.strip()}")
        
        if buy_lines:
            print("   📍 Log BUY trovato in:")
            for bl in buy_lines[:3]:  # Prime 3 occorrenze
                print(bl)
