#!/bin/bash
echo "🚀 QUANTUM SIMPLE RUNNER - Loop esterno bash"
echo "============================================="
echo "⏰ Started: $(date)"
echo ""

cd /home/orenzo/trading_project/QuantumTradingSystem
source venv/bin/activate

CYCLE_NUM=0

while true; do
    CYCLE_NUM=$((CYCLE_NUM + 1))
    echo ""
    echo "============================================="
    echo "🎯 CYCLE $CYCLE_NUM - $(date +%H:%M:%S)"
    echo "============================================="
    
    # Esegui UN ciclo e scrivi nel log
    python3 << 'PYEOF'
from quantum_v31_wrapper import QuantumTraderV31
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quantum_trader.log', mode='a'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

try:
    logger.info("=" * 60)
    logger.info(f"🎯 Starting cycle at {datetime.now().strftime('%H:%M:%S')}")
    
    trader = QuantumTraderV31(dry_run=True)
    trader.run_cycle()
    
    logger.info("✅ Cycle completed successfully")
    logger.info("=" * 60)
    
except Exception as e:
    logger.error(f"❌ Cycle failed: {e}")
    import traceback
    logger.error(traceback.format_exc())
PYEOF
    
    NEXT_TIME=$(date -d "+10 minutes" +%H:%M:%S)
    echo ""
    echo "✅ Cycle $CYCLE_NUM completed"
    echo "⏳ Waiting 600 seconds..."
    echo "⏰ Next cycle at: $NEXT_TIME"
    
    # Attendi 10 minuti
    sleep 600
done
