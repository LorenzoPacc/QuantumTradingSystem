#!/bin/bash
# Backup automatico del sistema trading

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=~/trading_backups

mkdir -p $BACKUP_DIR

cd ~/trading_project/QuantumTradingSystem

# Git commit + push
git add *.py
git commit -m "Auto backup $DATE" || true
git push origin main

# Backup dati locali
tar -czf $BACKUP_DIR/data_$DATE.tar.gz \
  paper_trading_30d/ \
  .env

# Mantieni solo ultimi 7 backup
ls -t $BACKUP_DIR/data_*.tar.gz | tail -n +8 | xargs rm -f

echo "✅ Backup completato: $DATE"
