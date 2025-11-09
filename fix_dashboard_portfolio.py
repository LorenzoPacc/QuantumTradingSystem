import streamlit as st
import json
from paper_trading_engine import PaperTradingEngine

def debug_portfolio():
    """Debug del portfolio"""
    engine = PaperTradingEngine(150)
    success = engine.load_from_json('paper_trading_state.json')
    
    print("🔍 DEBUG PORTFOLIO:")
    print(f"Caricamento: {success}")
    print(f"Tipo portfolio: {type(engine.portfolio)}")
    print(f"Portfolio: {engine.portfolio}")
    print(f"Lunghezza portfolio: {len(engine.portfolio)}")
    
    if hasattr(engine.portfolio, 'items'):
        print("✅ Portfolio ha metodo items()")
        for symbol, qty in engine.portfolio.items():
            print(f"  {symbol}: {qty} (tipo: {type(qty)})")
    else:
        print("❌ Portfolio non ha metodo items()")

if __name__ == "__main__":
    debug_portfolio()
