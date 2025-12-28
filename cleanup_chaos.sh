#!/bin/bash

echo "🧹 PULIZIA MASSIVA IN CORSO..."
echo "=============================="

# Conta file prima
BEFORE=$(ls -1 *.py 2>/dev/null | wc -l)
echo "📊 File Python prima: $BEFORE"

# Crea mega-backup di TUTTO
BACKUP_DIR="mega_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp *.py "$BACKUP_DIR/" 2>/dev/null
echo "✅ Backup completo in: $BACKUP_DIR"

# File da MANTENERE (lista bianca)
KEEP_FILES=(
    "quantum_v33_ultimate_final.py"
    "quantum_v33_ultimate_final_BEFORE_FIXES_*.py"
    "fix_critical_bugs.py"
    "integrate_fixes.py"
    "quantum_dashboard*.py"
    "quantum_database.py"
)

# Crea directory per archiviare vecchi file
mkdir -p archived_old_versions

# Sposta tutto tranne i file da mantenere
for file in *.py; do
    KEEP=false
    
    for pattern in "${KEEP_FILES[@]}"; do
        if [[ "$file" == $pattern ]]; then
            KEEP=true
            break
        fi
    done
    
    if [ "$KEEP" = false ]; then
        mv "$file" archived_old_versions/ 2>/dev/null
    fi
done

# Conta file dopo
AFTER=$(ls -1 *.py 2>/dev/null | wc -l)
REMOVED=$((BEFORE - AFTER))

echo ""
echo "=============================="
echo "✅ PULIZIA COMPLETATA!"
echo "=============================="
echo "📊 File prima: $BEFORE"
echo "📊 File dopo: $AFTER"
echo "🗑️  File archiviati: $REMOVED"
echo ""
echo "📁 File attivi rimasti:"
ls -1 *.py
echo ""
echo "📂 Vecchi file in: archived_old_versions/"
echo "📂 Backup completo in: $BACKUP_DIR/"

