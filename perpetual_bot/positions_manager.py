"""
Position Persistence Manager
Salva e carica posizioni come V37
"""
import json
import os
from datetime import datetime

class PositionsPersistence:
    """Gestisce salvataggio posizioni e trade"""
    
    def __init__(self, data_dir='perpetual_data'):
        self.data_dir = data_dir
        self.positions_file = os.path.join(data_dir, 'positions.json')
        self.trades_file = os.path.join(data_dir, 'trades.json')
        
        # Crea directory se non esiste
        os.makedirs(data_dir, exist_ok=True)
        
        # Inizializza files se non esistono
        if not os.path.exists(self.positions_file):
            self._save_json(self.positions_file, {})
        
        if not os.path.exists(self.trades_file):
            self._save_json(self.trades_file, [])
    
    def save_positions(self, positions):
        """
        Salva posizioni aperte
        positions = dict con chiave symbol
        """
        data = {}
        
        for symbol, pos in positions.items():
            # Converti datetime in string
            pos_data = {
                'symbol': pos['symbol'],
                'direction': pos['direction'],
                'entry_price': pos['entry_price'],
                'entry_time': pos['entry_time'].isoformat(),
                'quantity': pos['quantity'],
                'notional': pos['notional'],
                'leverage': pos['leverage'],
                'stop_loss': pos['stop_loss'],
                'take_profit': pos['take_profit'],
                'trailing_stop': {
                    'enabled': pos['trailing_stop']['enabled'],
                    'activation_price': pos['trailing_stop']['activation_price'],
                    'trail_distance_pct': pos['trailing_stop']['trail_distance_pct'],
                    'active': pos['trailing_stop']['active'],
                    'current_stop': pos['trailing_stop']['current_stop']
                },
                'rr_ratio': pos['rr_ratio']
            }
            data[symbol] = pos_data
        
        self._save_json(self.positions_file, data)
        return True
    
    def load_positions(self):
        """
        Carica posizioni salvate
        Returns: dict con posizioni
        """
        data = self._load_json(self.positions_file)
        
        if not data:
            return {}
        
        positions = {}
        for symbol, pos_data in data.items():
            # Converti string in datetime
            pos_data['entry_time'] = datetime.fromisoformat(pos_data['entry_time'])
            positions[symbol] = pos_data
        
        return positions
    
    def save_trade(self, trade):
        """
        Salva trade completato (come V37)
        """
        trades = self._load_json(self.trades_file)
        
        # Aggiungi nuovo trade
        trades.append(trade)
        
        self._save_json(self.trades_file, trades)
        return True
    
    def load_trades(self):
        """Carica tutti i trade"""
        return self._load_json(self.trades_file)
    
    def get_trade_count(self):
        """Conta trade totali"""
        trades = self.load_trades()
        return len(trades)
    
    def get_capital_from_trades(self):
        """Recupera capitale dall'ultimo trade (come V37)"""
        trades = self.load_trades()
        
        if not trades:
            return None
        
        # Ultimo trade ha il capitale finale
        last_trade = trades[-1]
        return last_trade.get('final_capital')
    
    def _save_json(self, filename, data):
        """Helper per salvare JSON"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_json(self, filename):
        """Helper per caricare JSON"""
        try:
            with open(filename) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {} if 'positions' in filename else []

if __name__ == "__main__":
    # Test
    print("🧪 Testing Persistence...")
    
    pm = PositionsPersistence()
    
    # Test save positions
    test_pos = {
        'BTC/USDT:USDT': {
            'symbol': 'BTC/USDT:USDT',
            'direction': 'LONG',
            'entry_price': 78000,
            'entry_time': datetime.now(),
            'quantity': 0.001,
            'notional': 78,
            'leverage': 2,
            'stop_loss': 75660,
            'take_profit': 83460,
            'trailing_stop': {
                'enabled': True,
                'activation_price': 81120,
                'trail_distance_pct': 0.02,
                'active': False,
                'current_stop': 75660
            },
            'rr_ratio': 2.33
        }
    }
    
    pm.save_positions(test_pos)
    print("✅ Positions saved")
    
    # Test load
    loaded = pm.load_positions()
    print(f"✅ Positions loaded: {len(loaded)} position(s)")
    
    # Test trade
    test_trade = {
        'symbol': 'BTC/USDT:USDT',
        'direction': 'LONG',
        'entry_price': 78000,
        'exit_price': 80000,
        'entry_time': datetime.now().isoformat(),
        'exit_time': datetime.now().isoformat(),
        'quantity': 0.001,
        'pnl_usd': 2.0,
        'pnl_pct': 0.026,
        'exit_reason': 'TAKE_PROFIT',
        'final_capital': 102.0
    }
    
    pm.save_trade(test_trade)
    print("✅ Trade saved")
    
    trades = pm.load_trades()
    print(f"✅ Total trades: {pm.get_trade_count()}")
    
    print("")
    print("✅ Persistence working!")
