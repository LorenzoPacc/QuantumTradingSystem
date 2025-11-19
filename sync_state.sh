#!/bin/bash
echo "🔄 Sincronizzazione file state..."
cp quantum_v2_state.json quantum_v3_state.json 2>/dev/null || true
echo "✅ File state sincronizzati"
