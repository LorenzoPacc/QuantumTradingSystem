#!/bin/bash
echo "💾 BACKUP AUTOMATICO QUANTUM..."
git add .
git commit -m "Auto-backup: $(date '+%Y-%m-%d %H:%M') - Quantum V3.1"
git push
echo "✅ Backup completato!"
