#!/bin/bash
# Aggiorna il comando dashboard per usare quello funzionante

# Backup dello script originale
cp quantum_v31_commands.sh quantum_v31_commands_backup.sh

# Modifica la sezione dashboard
sed -i 's/python3 dashboard_simple\.py/python3 dashboard_perfetta.py 8098/' quantum_v31_commands.sh

echo "✅ Comando dashboard aggiornato!"
echo "🚀 Ora usa: ./quantum_v31_commands.sh dashboard"
