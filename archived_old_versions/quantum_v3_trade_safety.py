#!/usr/bin/env python3
"""
QUANTUM V3 - TRADE SAFETY CHECK
Verifica che i trade siano di dimensioni ragionevoli
"""

def safe_trade_size_calculation(portfolio_value, cash_balance, symbol, price):
    """Calcola dimensioni trade in modo SICURO"""
    
    # LIMITI DI SICUREZZA
    MAX_TRADE_SIZE = 50  # Massimo $50 per trade
    MAX_PORTFOLIO_PERCENT = 0.05  # Massimo 5% del portafoglio
    
    # Calcola dimensione massima
    max_by_portfolio = portfolio_value * MAX_PORTFOLIO_PERCENT
    max_by_cash = cash_balance * 0.8  # Massimo 80% del cash
    
    # Usa il minimo tra tutti i limiti
    max_trade_size = min(MAX_TRADE_SIZE, max_by_portfolio, max_by_cash)
    
    # Calcola quantità
    quantity = max_trade_size / price
    
    print(f"🔒 CALCOLO SICURO:")
    print(f"   💰 Portafoglio: ${portfolio_value:.2f}")
    print(f"   💵 Cash: ${cash_balance:.2f}")
    print(f"   📈 Prezzo {symbol}: ${price:.3f}")
    print(f"   🎯 Max trade size: ${max_trade_size:.2f}")
    print(f"   📦 Quantità: {quantity:.4f}")
    
    return quantity, max_trade_size

# Test con i tuoi parametri
portfolio = 194.76
cash = 161.75
price = 2.729

quantity, size = safe_trade_size_calculation(portfolio, cash, "DOTUSDT", price)
print(f"✅ Trade sicuro: {quantity:.2f} unità per ${size:.2f}")
