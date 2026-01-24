#!/usr/bin/env python3
"""
Fix: Migliora labeling exit_reason in paper_trading_30d/trades.json
"""
import json
from datetime import datetime

# Backup
import shutil
shutil.copy('paper_trading_30d/trades.json', f'paper_trading_30d/trades_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')

# Carica trade
with open('paper_trading_30d/trades.json', 'r') as f:
    trades = json.load(f)

print(f"📊 Trovati {len(trades)} trade")

# Fix labels
fixed_count = 0
for trade in trades:
    old_reason = trade.get('reason', '')
    pnl_pct = trade.get('pnl_pct', 0)
    
    # Classifica exit reason
    if old_reason == "Stop loss hit":
        if pnl_pct > 0:
            trade['exit_reason'] = "TRAILING_STOP_PROFIT"
            fixed_count += 1
        else:
            trade['exit_reason'] = "HARD_STOP_LOSS"
            fixed_count += 1
    elif "target" in old_reason.lower() or "profit" in old_reason.lower():
        trade['exit_reason'] = "TAKE_PROFIT"
        fixed_count += 1
    else:
        # Mantieni reason originale se sconosciuto
        trade['exit_reason'] = old_reason
        
    # Mantieni anche 'reason' per compatibilità
    # (così non rompiamo niente)

# Salva
with open('paper_trading_30d/trades.json', 'w') as f:
    json.dump(trades, f, indent=2)

print(f"✅ Fixati {fixed_count} trade")
print(f"💾 Backup salvato in paper_trading_30d/trades_backup_*.json")

# Mostra distribuzione
from collections import Counter
reasons = Counter(t['exit_reason'] for t in trades)
print(f"\n📋 Distribuzione exit_reason:")
for reason, count in reasons.most_common():
    print(f"   {reason}: {count}")
