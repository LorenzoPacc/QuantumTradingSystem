#!/bin/bash
echo "🚀 LAUNCHING QUANTUM TRADER V3"
echo "================================"
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found"
    exit 1
fi
if [ ! -f "quantum_v3_enhanced.py" ]; then
    echo "❌ Enhanced bot not found. Run installer first."
    exit 1
fi
echo ""
echo "🎯 QUANTUM V3 FEATURES:"
echo "   • Advanced 6-Gate Entry Validation"
echo "   • Intelligent Position Sizing"
echo "   • Multi-Timeframe Analysis"
echo "   • Portfolio Risk Management"
echo "   • Market Regime Detection"
echo ""
echo "⚠️  MODE: DRY RUN (No live trades)"
echo "   To enable live trading, set: integration_manager.dry_run_mode = False"
echo ""
echo "Starting bot..."
echo "================================"
python3 quantum_v3_enhanced.py
