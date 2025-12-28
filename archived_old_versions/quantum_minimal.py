#!/usr/bin/env python3
"""
🚀 QUANTUM MINIMAL - Cattura tutto l'output
"""

import time
import sys
import logging
from datetime import datetime
from quantum_v31_wrapper import QuantumTraderV31

# Redirect stdout al log file
class LoggerWriter:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.strip():
            self.logger.log(self.level, message.strip())

    def flush(self):
        pass

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('quantum_trader.log', mode='a'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger()

# Redirect print() al logger
sys.stdout = LoggerWriter(logger, logging.INFO)
sys.stderr = LoggerWriter(logger, logging.ERROR)

logger.info("=" * 60)
logger.info("🚀 QUANTUM MINIMAL STARTED")
logger.info(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logger.info("=" * 60)

try:
    trader = QuantumTraderV31(dry_run=True)
    logger.info(f"💰 Cash: ${trader.cash_balance:.2f}")
    logger.info(f"📊 Positions: {len(trader.portfolio)}")
except Exception as e:
    logger.error(f"❌ Failed to initialize: {e}")
    sys.exit(1)

cycle = 0
logger.info("🔄 STARTING MAIN LOOP")
logger.info("=" * 60)

while True:
    try:
        cycle += 1
        current_time = datetime.now().strftime('%H:%M:%S')
        
        logger.info("")
        logger.info("=" * 60)
        logger.info(f"🎯 CYCLE {cycle} - {current_time}")
        logger.info("=" * 60)
        
        trader.run_cycle()
        
        next_time = datetime.fromtimestamp(time.time() + 600).strftime('%H:%M:%S')
        logger.info(f"✅ Cycle {cycle} completed")
        logger.info(f"⏳ Sleeping 600s until next cycle...")
        logger.info(f"⏰ Next cycle at: {next_time}")
        
        time.sleep(600)
        
    except KeyboardInterrupt:
        logger.info("")
        logger.info("=" * 60)
        logger.info("🛑 SHUTDOWN - Stopped by user")
        logger.info("=" * 60)
        break
        
    except Exception as e:
        logger.error(f"❌ Error in cycle {cycle}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        logger.info("⏳ Waiting 60s before retry...")
        time.sleep(60)
