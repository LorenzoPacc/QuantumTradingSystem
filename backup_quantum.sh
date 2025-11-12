#!/bin/bash
echo "💾 BACKUP QUANTUM V2.0"
cp quantum_v2_state.json "backup/quantum_state_$(date +%Y%m%d_%H%M).json"
cp quantum_v2_performance.db "backup/quantum_db_$(date +%Y%m%d_%H%M).db"
echo "✅ Backup completato"
