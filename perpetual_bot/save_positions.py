"""Add position persistence"""
import json

def save_positions(positions, filename='positions_state.json'):
    """Save positions to file"""
    with open(filename, 'w') as f:
        # Convert datetime to string
        data = {}
        for symbol, pos in positions.items():
            pos_copy = pos.copy()
            pos_copy['entry_time'] = pos_copy['entry_time'].isoformat()
            data[symbol] = pos_copy
        json.dump(data, f, indent=2)

def load_positions(filename='positions_state.json'):
    """Load positions from file"""
    try:
        with open(filename) as f:
            data = json.load(f)
        # Convert string back to datetime
        from datetime import datetime
        for symbol in data:
            data[symbol]['entry_time'] = datetime.fromisoformat(data[symbol]['entry_time'])
        return data
    except FileNotFoundError:
        return {}
