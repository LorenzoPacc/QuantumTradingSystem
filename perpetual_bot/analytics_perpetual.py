#!/usr/bin/env python3
"""
Analytics per Perpetual Bot
"""
import json

def show_stats():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║       📊 PERPETUAL BOT V1 - ANALYTICS                     ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print("")
    
    # Load config
    with open('perpetual_config.json') as f:
        config = json.load(f)
    
    print("⚙️  CONFIGURATION:")
    print(f"   Capital: ${config['capital']['initial']}")
    print(f"   Leverage: {config['leverage']['default']}x (max {config['leverage']['max']}x)")
    print(f"   Position Size: {config['position']['max_size_pct']*100:.0f}% capital")
    print(f"   Stop Loss: {config['risk']['stop_loss_pct']*100:.1f}%")
    print(f"   Take Profit: {config['risk']['take_profit_pct']*100:.1f}%")
    print(f"   Daily Loss Limit: {config['limits']['daily_loss_limit_pct']*100:.1f}%")
    print("")
    
    print("🎯 TARGETS:")
    print(f"   Win Rate: {config['targets']['win_rate'][0]*100:.0f}-{config['targets']['win_rate'][1]*100:.0f}%")
    print(f"   Sharpe: {config['targets']['sharpe'][0]:.1f}-{config['targets']['sharpe'][1]:.1f}")
    print(f"   Trades/Month: {config['targets']['trades_per_month'][0]}-{config['targets']['trades_per_month'][1]}")
    print(f"   Max DD: {config['targets']['max_drawdown']*100:.0f}%")
    print("")
    
    print("📋 FILES:")
    import os
    for f in ['perpetual_bot.py', 'signal_generator.py', 'risk_manager.py', 'indicators.py']:
        size = os.path.getsize(f) / 1024
        print(f"   ✅ {f} ({size:.1f}KB)")
    
    print("")
    print("════════════════════════════════════════════════════════════")

if __name__ == "__main__":
    show_stats()
