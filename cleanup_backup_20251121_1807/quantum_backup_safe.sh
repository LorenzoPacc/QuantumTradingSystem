#!/bin/bash
echo "💾 QUANTUM TRADING - BACKUP SICURO"
echo "=================================="

# 1. Backup locale principale
echo "📁 Backup locale..."
MAIN_BACKUP="$HOME/Quantum_Main_Backup_$(date +%Y%m%d_%H%M%S)"
cp -r $(pwd) "$MAIN_BACKUP"

# 2. Backup configurazioni (lightweight)
echo "📋 Backup configurazioni..."
CONFIG_BACKUP="$HOME/Quantum_Config_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf "$CONFIG_BACKUP" *.py *.sh *.json *.log 2>/dev/null

# 3. Statistiche
echo ""
echo "✅ BACKUP COMPLETATO:"
echo "   📦 Locale completo: $MAIN_BACKUP"
echo "   🔧 Configurazioni: $CONFIG_BACKUP"
echo "   📊 File Python: $(find "$MAIN_BACKUP" -name "*.py" | wc -l)"
echo "   ⚡ Script: $(find "$MAIN_BACKUP" -name "*.sh" | wc -l)"
echo "   🕒 Data: $(date)"

# 4. Lista backup recenti
echo ""
echo "📋 BACKUP RECENTI:"
ls -lt ~/Quantum_*_Backup_* 2>/dev/null | head -3
