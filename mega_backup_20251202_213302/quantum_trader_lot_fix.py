#!/usr/bin/env python3
"""
QUANTUM TRADER LOT FIX - Risolve problemi LOT_SIZE
"""

class LotSizeFix:
    @staticmethod
    def adjust_quantity(symbol, quantity):
        """Aggiusta quantity per LOT_SIZE rules"""
        # Minimi e step sizes per TestNet
        lot_rules = {
            "BTCUSDT": {"min_qty": 0.00001, "step_size": 0.000001},
            "ETHUSDT": {"min_qty": 0.0001, "step_size": 0.00001},
            "SOLUSDT": {"min_qty": 0.01, "step_size": 0.001}
        }
        
        rules = lot_rules.get(symbol, {"min_qty": 0.001, "step_size": 0.001})
        
        # Applica step size
        steps = quantity / rules["step_size"]
        adjusted_steps = int(steps)
        if steps > adjusted_steps:
            adjusted_steps += 1
        
        adjusted_quantity = adjusted_steps * rules["step_size"]
        
        # Verifica minimo
        if adjusted_quantity < rules["min_qty"]:
            adjusted_quantity = rules["min_qty"]
        
        # Arrotondamento finale
        if symbol == "BTCUSDT":
            return round(adjusted_quantity, 6)
        elif symbol == "ETHUSDT":
            return round(adjusted_quantity, 5)
        else:
            return round(adjusted_quantity, 3)

# Test
if __name__ == "__main__":
    test_cases = [
        ("BTCUSDT", 0.00011),
        ("ETHUSDT", 0.00277), 
        ("SOLUSDT", 0.06)
    ]
    
    print("🔧 TEST LOT SIZE FIX:")
    for symbol, qty in test_cases:
        fixed = LotSizeFix.adjust_quantity(symbol, qty)
        print(f"   {symbol}: {qty} → {fixed}")
