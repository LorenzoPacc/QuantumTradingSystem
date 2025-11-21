#!/bin/bash
echo "💾 QUANTUM BACKUP $(date '+%Y-%m-%d %H:%M')"
cp trading_performance.db "backup_$(date +%Y%m%d_%H%M).db"
git add .
git commit -m "Backup auto $(date '+%Y%m%d_%H%M')"
git push
echo "✅ Backup completato"
