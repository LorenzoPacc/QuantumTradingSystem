#!/usr/bin/env python3
"""
🎯 TRAILING STOP MANAGER - QUANTUM V3
Protezione dinamica dei profitti per posizioni attive
"""

import json
from datetime import datetime
from typing import Dict, Optional

class TrailingStopManager:
    """
    🎯 Trailing Stop Dinamico per Quantum V3
    Protegge i profitti mentre lascia correre i trend
    """
    
    def __init__(self, 
                 activation_profit: float = 0.02,    # Attiva a +2%
                 trailing_distance: float = 0.01,    # Segue a -1%
                 min_profit_lock: float = 0.015):    # Blocca min +1.5%
        
        self.activation_profit = activation_profit
        self.trailing_distance = trailing_distance
        self.min_profit_lock = min_profit_lock
        self.trailing_stops = {}  # {symbol: stop_price}
        self.peak_prices = {}     # {symbol: highest_price_reached}
        
    def update_stop(self, 
                    symbol: str,
                    entry_price: float,
                    current_price: float,
                    current_stop: float) -> Dict:
        """
        Aggiorna trailing stop per una posizione
        
        Returns: {
            'new_stop': float,
            'stop_moved': bool,
            'profit_locked': float,
            'status': str
        }
        """
        
        # Calcola profit attuale
        unrealized_pnl = (current_price - entry_price) / entry_price
        
        # Traccia il picco raggiunto
        if symbol not in self.peak_prices:
            self.peak_prices[symbol] = current_price
        else:
            self.peak_prices[symbol] = max(self.peak_prices[symbol], current_price)
        
        # Trailing stop NON attivo ancora
        if unrealized_pnl < self.activation_profit:
            return {
                'new_stop': current_stop,
                'stop_moved': False,
                'profit_locked': 0,
                'status': f'WAITING_ACTIVATION ({unrealized_pnl*100:.2f}% < {self.activation_profit*100:.0f}%)',
                'peak_price': self.peak_prices[symbol]
            }
        
        # 🚀 TRAILING ATTIVO
        peak = self.peak_prices[symbol]
        
        # Calcola nuovo stop dal picco
        trailing_stop = peak * (1 - self.trailing_distance)
        
        # Assicura profitto minimo bloccato
        min_profit_stop = entry_price * (1 + self.min_profit_lock)
        
        # Nuovo stop = max tra trailing, min_profit, e stop precedente
        new_stop = max(trailing_stop, min_profit_stop, current_stop)
        
        # Aggiorna trailing stops
        self.trailing_stops[symbol] = new_stop
        
        # Calcola profitto bloccato
        profit_locked = (new_stop - entry_price) / entry_price
        
        stop_moved = new_stop > current_stop
        
        return {
            'new_stop': round(new_stop, 6),
            'stop_moved': stop_moved,
            'profit_locked': round(profit_locked * 100, 2),
            'status': 'ACTIVE_TRAILING',
            'peak_price': peak,
            'distance_from_peak': round((peak - current_price) / peak * 100, 2)
        }
    
    def should_exit(self, symbol: str, current_price: float) -> bool:
        """Verifica se prezzo ha colpito lo stop"""
        if symbol not in self.trailing_stops:
            return False
        return current_price <= self.trailing_stops[symbol]
    
    def get_stop_info(self, symbol: str) -> Optional[Dict]:
        """Info complete sullo stop di un symbol"""
        if symbol not in self.trailing_stops:
            return None
        
        return {
            'symbol': symbol,
            'stop_price': self.trailing_stops[symbol],
            'peak_price': self.peak_prices.get(symbol, 0),
            'timestamp': datetime.now().isoformat()
        }
    
    def reset_stop(self, symbol: str):
        """Reset stop per un symbol (dopo exit)"""
        self.trailing_stops.pop(symbol, None)
        self.peak_prices.pop(symbol, None)

# 📊 TEST IMMEDIATO
if __name__ == "__main__":
    print("🧪 TEST TRAILING STOP - DOTUSDT")
    print("=" * 60)
    
    tsm = TrailingStopManager(
        activation_profit=0.02,
        trailing_distance=0.01,
        min_profit_lock=0.015
    )
    
    # Test con DOTUSDT
    symbol = "DOTUSDT"
    entry = 2.662
    current = 2.748
    current_stop = 2.662
    
    result = tsm.update_stop(symbol, entry, current, current_stop)
    
    print(f"Entry: ${entry}")
    print(f"Current: ${current}")
    print(f"New Stop: ${result['new_stop']}")
    print(f"Profit Locked: +{result['profit_locked']}%")
    print(f"Status: {result['status']}")
    
    if result['stop_moved']:
        print("✅ TRAILING STOP ATTIVO!")
    else:
        print("⏳ In attesa di attivazione...")
