#!/bin/python3
print("🛡️ SISTEMA DI PREVENZIONE OVERCONCENTRATION")
print("==========================================")

# Aggiungi questa logica a quantum_trader_production.py

MAX_SINGLE_ASSET_WEIGHT = 0.12  # Massimo 12% per asset

def check_portfolio_concentration(self, portfolio, symbol):
    """Controlla e previeni overconcentration"""
    asset_value = portfolio.get(symbol, 0) * self.get_current_price(symbol)
    portfolio_value = self.calculate_portfolio_value(portfolio)
    
    weight = asset_value / portfolio_value if portfolio_value > 0 else 0
    
    if weight > MAX_SINGLE_ASSET_WEIGHT:
        print(f"⚠️  OVERCONCENTRATION: {symbol} al {weight:.1%}")
        # Auto-diversifica vendendo il 25%
        excess = weight - MAX_SINGLE_ASSET_WEIGHT
        sell_percentage = min(excess / weight, 0.25)  # Max 25% vendita
        return True, sell_percentage
    return False, 0

print("✅ Aggiungi questa funzione al trader per prevenire futuro overconcentration")
