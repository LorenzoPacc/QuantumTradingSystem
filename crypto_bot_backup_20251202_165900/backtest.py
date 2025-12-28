"""
Quick Backtest Script
Testa la strategia su dati storici
"""

import yaml
import pandas as pd
from strategy import QuantumStrategy, Signal
from datetime import datetime, timedelta

def run_quick_backtest():
    """Backtest rapido su dati simulati"""
    
    with open('config/config.yaml') as f:
        config = yaml.safe_load(f)
    
    strategy = QuantumStrategy(config)
    
    print("🧪 BACKTEST RAPIDO")
    print("="*60)
    
    # Simula scenari tipici
    scenarios = [
        {
            'name': 'Extreme Fear + RSI Low',
            'data': {
                'symbol': 'BTC/USDT',
                'price': 40000,
                'rsi': 28,
                'price_change_24h': -5.2,
                'volume_change_24h': 80,
                'ema_9': 39500,
                'ema_21': 41000
            },
            'fear_greed': 22
        },
        {
            'name': 'High RSI + Greed',
            'data': {
                'symbol': 'ETH/USDT',
                'price': 2500,
                'rsi': 78,
                'price_change_24h': 8.5,
                'volume_change_24h': 30,
                'ema_9': 2520,
                'ema_21': 2350
            },
            'fear_greed': 72
        },
        {
            'name': 'Neutral Market',
            'data': {
                'symbol': 'BNB/USDT',
                'price': 300,
                'rsi': 52,
                'price_change_24h': -1.2,
                'volume_change_24h': 15,
                'ema_9': 301,
                'ema_21': 299
            },
            'fear_greed': 50
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📍 {scenario['name']}")
        print("-" * 60)
        
        signal = strategy.calculate_signal(scenario['data'], scenario['fear_greed'])
        
        print(f"Segnale: {signal.signal.name}")
        print(f"Confidence: {signal.confidence:.1f}%")
        print(f"Motivi: {' | '.join(signal.reasons)}")
        
        size = strategy.calculate_position_size(
            signal, 
            portfolio_value=200,
            available_cash=200,
            num_positions=0
        )
        
        if size > 0:
            print(f"✅ Position size: ${size:.2f} ({size/200*100:.1f}% del capitale)")
        else:
            print(f"⚠️  Nessun trade (confidence {signal.confidence:.0f}% < {strategy.min_confidence}%)")
    
    print("\n" + "="*60)
    print("✅ Backtest completato")

if __name__ == "__main__":
    run_quick_backtest()
