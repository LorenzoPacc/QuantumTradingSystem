"""
STATE MANAGER per Quantum Trader - Persistenza dati
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

class StateManager:
    """
    Gestisce il salvataggio e caricamento dello stato del bot
    """
    
    def __init__(self, state_file: str = 'quantum_state.json'):
        self.state_file = state_file
        self.backup_dir = 'state_backups'
        
    def save_state(self, bot_instance) -> bool:
        """
        Salva lo stato completo del bot
        """
        try:
            state = {
                'metadata': {
                    'version': '2.5',
                    'timestamp': datetime.now().isoformat(),
                    'capital': getattr(bot_instance, 'capital', 0),
                    'total_trades': getattr(bot_instance, 'total_trades', 0),
                    'win_rate': getattr(bot_instance, 'win_rate', 0)
                },
                'positions': self._serialize_positions(getattr(bot_instance, 'positions', {})),
                'trade_history': getattr(bot_instance, 'trade_history', [])[-100:],
                'performance': {
                    'daily_pnl': getattr(bot_instance, 'daily_pnl', 0),
                    'weekly_pnl': getattr(bot_instance, 'weekly_pnl', 0),
                    'total_pnl': getattr(bot_instance, 'total_pnl', 0)
                },
                'settings': {
                    'watch_symbols': getattr(bot_instance, 'watch_symbols', []),
                    'max_positions': getattr(bot_instance, 'max_positions', 6),
                    'risk_per_trade': getattr(bot_instance, 'risk_per_trade', 0.1)
                }
            }
            
            # Crea backup
            self._create_backup()
            
            # Salva stato
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2, default=str)
            
            print(f"✅ Stato salvato: {len(state['positions'])} posizioni")
            return True
            
        except Exception as e:
            print(f"❌ Errore salvataggio stato: {e}")
            return False
    
    def load_state(self) -> Dict[str, Any]:
        """
        Carica lo stato precedente
        """
        try:
            if not os.path.exists(self.state_file):
                print("⚠️ Nessuno stato precedente trovato")
                return {}
            
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            
            print(f"✅ Stato caricato: {len(state.get('positions', []))} posizioni")
            return state
            
        except Exception as e:
            print(f"❌ Errore caricamento stato: {e}")
            return {}
    
    def _serialize_positions(self, positions: Dict) -> List[Dict]:
        """Serializza le posizioni per il salvataggio"""
        serialized = []
        for symbol, position in positions.items():
            serialized.append({
                'symbol': symbol,
                'entry_price': getattr(position, 'entry_price', 0),
                'quantity': getattr(position, 'quantity', 0),
                'current_price': getattr(position, 'current_price', 0),
                'pnl': getattr(position, 'pnl', 0),
                'pnl_percent': getattr(position, 'pnl_percent', 0),
                'entry_time': getattr(position, 'entry_time', datetime.now().isoformat()),
                'stop_loss': getattr(position, 'stop_loss', 0),
                'take_profit': getattr(position, 'take_profit', 0)
            })
        return serialized
    
    def _create_backup(self):
        """Crea backup dello stato"""
        try:
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir)
            
            if os.path.exists(self.state_file):
                backup_file = f"{self.backup_dir}/state_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                import shutil
                shutil.copy2(self.state_file, backup_file)
                
                # Mantieni solo ultimi 5 backup
                backups = sorted([f for f in os.listdir(self.backup_dir) if f.startswith('state_backup_')])
                if len(backups) > 5:
                    for old_backup in backups[:-5]:
                        os.remove(os.path.join(self.backup_dir, old_backup))
                        
        except Exception as e:
            print(f"⚠️ Backup fallito: {e}")

    def emergency_save(self, bot_instance):
        """
        Salvataggio di emergenza (minimo essenziale)
        """
        try:
            emergency_state = {
                'capital': getattr(bot_instance, 'capital', 0),
                'positions': self._serialize_positions(getattr(bot_instance, 'positions', {})),
                'timestamp': datetime.now().isoformat()
            }
            
            with open('emergency_state.json', 'w') as f:
                json.dump(emergency_state, f)
            
            print("🚨 Stato di emergenza salvato")
            
        except Exception as e:
            print(f"💥 Salvataggio emergenza fallito: {e}")
