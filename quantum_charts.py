#!/usr/bin/env python3
"""
Quantum Trading Charts - Visualizzazione Performance
"""
import re
from datetime import datetime, timedelta
from collections import defaultdict

def create_simple_chart(data, title, width=50):
    """Crea chart ASCII semplice"""
    if not data:
        return "No data"
    
    lines = []
    lines.append(f"\n{title}")
    lines.append("─" * width)
    
    max_val = max(data.values()) if data else 1
    min_val = min(data.values()) if data else 0
    range_val = max_val - min_val if max_val != min_val else 1
    
    for key, value in sorted(data.items()):
        bar_len = int(((value - min_val) / range_val) * (width - 20))
        bar = "█" * bar_len
        lines.append(f"{key:12} │{bar} {value:.1f}")
    
    return "\n".join(lines)

def analyze_hourly_performance(log_file="quantum_v33_ultimate_final.log"):
    """Analizza performance per ora del giorno"""
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
    except:
        return {}
    
    hourly_buys = defaultdict(int)
    hourly_sells = defaultdict(int)
    
    for line in lines:
        match = re.match(r'(\d{4}-\d{2}-\d{2} (\d{2}):\d{2}:\d{2})', line)
        if match:
            hour = int(match.group(2))
            
            if 'BUY ' in line and '@' in line:
                hourly_buys[f"{hour:02d}:00"] += 1
            
            if 'SELL' in line or 'TRAILING' in line:
                hourly_sells[f"{hour:02d}:00"] += 1
    
    return {
        'buys': dict(hourly_buys),
        'sells': dict(hourly_sells)
    }

if __name__ == "__main__":
    print("📊 GENERATING CHARTS...")
    
    data = analyze_hourly_performance()
    
    if data['buys']:
        print(create_simple_chart(data['buys'], "🟢 BUYS BY HOUR"))
    
    if data['sells']:
        print(create_simple_chart(data['sells'], "🔴 SELLS BY HOUR"))
