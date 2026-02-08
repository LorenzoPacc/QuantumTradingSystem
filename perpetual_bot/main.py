#!/usr/bin/env python3
"""
Perpetual Bot V1 - Main Runner
"""
import time
import json
from datetime import datetime
from perpetual_bot import PerpetualBot

def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          🚀 PERPETUAL BOT V1 - STARTING               ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print("")
    
    # Load config
    with open('perpetual_config.json') as f:
        config = json.load(f)
    
    # Initialize bot
    bot = PerpetualBot()
    
    # Cycle interval (2 hours like V37)
    cycle_interval = 7200  # 2 hours
    
    print(f"⏱️  Cycle interval: {cycle_interval//3600} hours")
    print("")
    print("🚀 Starting trading loop...")
    print("")
    
    try:
        while True:
            bot.run_cycle()
            
            print("=" * 80)
            print(f"⏰ Next cycle in {cycle_interval//3600} hours ({cycle_interval} seconds)...")
            print("=" * 80)
            print("")
            
            time.sleep(cycle_interval)
            
    except KeyboardInterrupt:
        print("")
        print("🛑 Bot stopped by user")
        print("")
        print("📊 FINAL STATS:")
        print(f"   Total Trades: {len(bot.trades_history)}")
        print(f"   Final Capital: ${bot.risk_manager.current_capital:.2f}")
        
        if bot.trades_history:
            wins = len([t for t in bot.trades_history if t['pnl_usd'] > 0])
            wr = wins / len(bot.trades_history) * 100
            total_pnl = sum(t['pnl_usd'] for t in bot.trades_history)
            print(f"   Win Rate: {wr:.1f}%")
            print(f"   Total PnL: ${total_pnl:+.2f}")
        
        print("")
        print("✅ Shutdown complete")

if __name__ == "__main__":
    main()
