#!/usr/bin/env python3
"""
🚀 QUANTUM LAUNCHER - Loop esplicito garantito
"""

import time
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quantum_trader.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 60)
    logger.info("🚀 QUANTUM LAUNCHER WITH EXPLICIT LOOP")
    logger.info(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    try:
        from quantum_v31_wrapper import QuantumTraderV31
        logger.info("✅ Module loaded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to load module: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return
    
    try:
        trader = QuantumTraderV31(dry_run=True)
        logger.info("✅ Trader initialized successfully")
        logger.info(f"💰 Cash: ${trader.cash_balance:.2f}")
        logger.info(f"📊 Positions: {len(trader.portfolio)}")
    except Exception as e:
        logger.error(f"❌ Failed to initialize trader: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return
    
    cycle_count = 0
    logger.info("")
    logger.info("🔄 STARTING MAIN LOOP")
    logger.info("=" * 60)
    
    while True:
        try:
            cycle_count += 1
            current_time = datetime.now().strftime('%H:%M:%S')
            
            logger.info("")
            logger.info("=" * 60)
            logger.info(f"🎯 CYCLE {cycle_count} - {current_time}")
            logger.info("=" * 60)
            
            # Esegui il ciclo di trading
            trader.run_cycle()
            
            next_cycle_time = datetime.fromtimestamp(time.time() + 600).strftime('%H:%M:%S')
            logger.info(f"✅ Cycle {cycle_count} completed successfully")
            logger.info(f"⏳ Sleeping 600s until next cycle...")
            logger.info(f"⏰ Next cycle at: {next_cycle_time}")
            
            # Attendi 10 minuti (600 secondi)
            time.sleep(600)
            
        except KeyboardInterrupt:
            logger.info("")
            logger.info("=" * 60)
            logger.info("🛑 SHUTDOWN - Stopped by user (Ctrl+C)")
            logger.info("=" * 60)
            break
            
        except Exception as e:
            logger.error(f"")
            logger.error(f"❌ ERROR in cycle {cycle_count}: {e}")
            logger.error("📋 Traceback:")
            import traceback
            logger.error(traceback.format_exc())
            logger.warning("⏳ Waiting 60s before retry...")
            time.sleep(60)

if __name__ == '__main__':
    main()
