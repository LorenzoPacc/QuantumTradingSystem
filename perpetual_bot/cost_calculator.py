"""
Cost Calculator - Fee + Slippage Awareness
Implementa: Expected Edge > (Fee + Slippage) * 2.5

Supporta SPOT e FUTURES
"""

class CostCalculator:
    """Calcola costi totali trading"""
    
    def __init__(self, is_spot=True):
        self.is_spot = is_spot
        
        # Fee structure
        self.spot_fee = 0.001  # 0.1% per trade
        self.futures_fee = 0.0005  # 0.05% per trade
        
        # Slippage stimati (realistici)
        self.slippage_map = {
            'BTC/USDT': 0.0001,   # 0.01%
            'ETH/USDT': 0.00015,  # 0.015%
            'SOL/USDT': 0.0002,   # 0.02%
            # Futures symbols
            'BTC/USDT:USDT': 0.0001,
            'ETH/USDT:USDT': 0.00015
        }
    
    def calculate_total_cost(self, symbol, funding_rate=0):
        """
        Calcola costo totale per round-trip trade
        
        Args:
            symbol: asset symbol
            funding_rate: funding rate (solo futures, per 24h)
        
        Returns: 
            percentage (es. 0.0022 = 0.22%)
        """
        
        # Trading fee (entry + exit)
        if self.is_spot:
            fee = self.spot_fee * 2  # 0.2% totale
        else:
            fee = self.futures_fee * 2  # 0.1% totale
        
        # Slippage (entry + exit)
        slippage = self.slippage_map.get(symbol, 0.0003) * 2
        
        # Funding (solo futures)
        funding_cost = 0
        if not self.is_spot and funding_rate != 0:
            # Assume holding 24h = 3 funding periods
            funding_cost = abs(funding_rate) * 3
        
        total_cost = fee + slippage + funding_cost
        
        return total_cost
    
    def should_trade_based_on_edge(self, expected_edge, symbol, multiplier=2.5, funding_rate=0):
        """
        Regola: Expected Edge > Total Cost * multiplier
        
        Args:
            expected_edge: percentuale guadagno atteso (es. 0.05 = 5%)
            symbol: asset da tradare
            multiplier: moltiplicatore sicurezza (default 2.5)
            funding_rate: funding rate (solo futures)
        
        Returns:
            (bool, str): (should_trade, reason)
        """
        
        total_cost = self.calculate_total_cost(symbol, funding_rate)
        required_edge = total_cost * multiplier
        
        if expected_edge >= required_edge:
            return True, f"Edge OK: {expected_edge:.2%} > {required_edge:.2%} required"
        else:
            return False, f"Edge too low: {expected_edge:.2%} < {required_edge:.2%} required (cost: {total_cost:.2%})"
    
    def get_cost_breakdown(self, symbol, funding_rate=0):
        """Per debugging/analytics"""
        fee = (self.spot_fee if self.is_spot else self.futures_fee) * 2
        slippage = self.slippage_map.get(symbol, 0.0003) * 2
        funding = abs(funding_rate) * 3 if not self.is_spot else 0
        
        return {
            'type': 'SPOT' if self.is_spot else 'FUTURES',
            'fee': fee,
            'slippage': slippage,
            'funding': funding,
            'total': fee + slippage + funding
        }

if __name__ == "__main__":
    # Test
    print("════════════════════════════════════════════════════════════")
    print("📊 COST CALCULATOR TEST")
    print("════════════════════════════════════════════════════════════")
    print("")
    
    # Test SPOT
    print("🔵 SPOT MODE (V37):")
    calc_spot = CostCalculator(is_spot=True)
    
    for symbol in ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']:
        breakdown = calc_spot.get_cost_breakdown(symbol)
        print(f"  {symbol}:")
        print(f"    Fee: {breakdown['fee']:.4%}")
        print(f"    Slippage: {breakdown['slippage']:.4%}")
        print(f"    Total: {breakdown['total']:.4%}")
        print(f"    Min Edge (2.5x): {breakdown['total']*2.5:.2%}")
        print("")
    
    # Test FUTURES
    print("⚡ FUTURES MODE (Perpetual):")
    calc_futures = CostCalculator(is_spot=False)
    
    for symbol in ['BTC/USDT:USDT', 'ETH/USDT:USDT']:
        # Simula funding rate
        funding = 0.0001  # 0.01% per 8h
        breakdown = calc_futures.get_cost_breakdown(symbol, funding)
        print(f"  {symbol}:")
        print(f"    Fee: {breakdown['fee']:.4%}")
        print(f"    Slippage: {breakdown['slippage']:.4%}")
        print(f"    Funding (24h): {breakdown['funding']:.4%}")
        print(f"    Total: {breakdown['total']:.4%}")
        print(f"    Min Edge (2.5x): {breakdown['total']*2.5:.2%}")
        print("")
    
    print("════════════════════════════════════════════════════════════")
    print("✅ Cost Calculator ready!")
    print("════════════════════════════════════════════════════════════")
