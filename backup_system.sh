#!/bin/bash
# Backup automatico COMPLETO (V37 + Perpetual + Journal)

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=~/trading_backups

mkdir -p $BACKUP_DIR
cd ~/trading_project/QuantumTradingSystem

echo "🔄 Starting backup: $DATE"

# Backup COMPLETO
tar -czf $BACKUP_DIR/full_backup_$DATE.tar.gz \
  autonomous_trading_bot_improved.py \
  regime_controller.py \
  cost_calculator.py \
  create_trading_journal.py \
  bot_improvements_config.json \
  paper_trading_30d/ \
  perpetual_bot/ \
  Trading_Journal_LIVE.xlsx \
  .env 2>/dev/null

# Verifica dimensione backup
BACKUP_SIZE=$(du -h $BACKUP_DIR/full_backup_$DATE.tar.gz | cut -f1)
echo "✅ Backup creato: full_backup_$DATE.tar.gz ($BACKUP_SIZE)"

# Mantieni solo ultimi 7 backup
ls -t $BACKUP_DIR/full_backup_*.tar.gz | tail -n +8 | xargs rm -f 2>/dev/null
echo "🗑️ Backup vecchi rimossi (keep last 7)"

# Lista backup attuali
echo "📋 Backup disponibili:"
ls -lh $BACKUP_DIR/full_backup_*.tar.gz | tail -3

echo "✅ Backup completato: $DATE"
