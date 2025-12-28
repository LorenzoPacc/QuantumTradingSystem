#!/usr/bin/env python3
"""Analizza se MTF filtering sta aiutando o danneggiando"""

import re
from collections import defaultdict

def analyze_mtf_impact(log_file):
    print("\n📊 MTF FILTERING ANALYSIS")
    print("="*70)
    
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    # Conta MTF failures per coin
    mtf_failures = defaultdict(int)
    mtf_alignment_values = defaultdict(list)
    
    for line in lines:
        if "MTF_FAIL" in line:
            # Estrai coin e alignment
            match = re.search(r'(\w+/USDT).*alignment=(\d+)%', line)
            if match:
                coin = match.group(1)
                alignment = int(match.group(2))
                mtf_failures[coin] += 1
                mtf_alignment_values[coin].append(alignment)
    
    print("\n🚫 MTF Failures per Coin:")
    for coin, count in sorted(mtf_failures.items(), key=lambda x: x[1], reverse=True):
        avg_alignment = sum(mtf_alignment_values[coin]) / len(mtf_alignment_values[coin])
        print(f"   {coin}: {count} failures, avg alignment: {avg_alignment:.1f}%")
    
    # Analisi threshold
    all_alignments = []
    for values in mtf_alignment_values.values():
        all_alignments.extend(values)
    
    if all_alignments:
        avg_alignment = sum(all_alignments) / len(all_alignments)
        print(f"\n📈 Average MTF Alignment: {avg_alignment:.1f}%")
        print(f"   Current threshold: 60%")
        
        # Conta quanti passerebbero con threshold diversi
        for threshold in [40, 45, 50, 55, 60]:
            passed = sum(1 for a in all_alignments if a >= threshold)
            pct = (passed / len(all_alignments)) * 100
            print(f"   Con threshold {threshold}%: {passed}/{len(all_alignments)} passerebbero ({pct:.1f}%)")
    
    # Raccomandazione
    print("\n💡 RACCOMANDAZIONE MTF:")
    if avg_alignment < 50:
        print("   ⚠️  MTF threshold 60% è TROPPO RIGIDO")
        print("   ✅ Prova threshold 40-45% per più opportunità")
    else:
        print("   ✅ MTF threshold attuale sembra appropriato")
    
    print("="*70)

# Run
analyze_mtf_impact('v34_startup.log')
