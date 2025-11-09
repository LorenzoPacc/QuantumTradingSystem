#!/bin/python3
import requests
import json
import os
from datetime import datetime

print("🔄 DIVERSIFICAZIONE XRP - STRATEGIA REALE")
print("=========================================")

# Configurazione
XRP_TICKER = "XRPUSDT"
REDUCTION_TARGET = 0.30  # Riduci del 30%
MAX_XRP_WEIGHT = 0.10   # Massimo 10% del portfolio

def get_current_price(symbol):
    """Ottieni prezzo corrente da Binance"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/price"
        response = requests.get(url, params={'symbol': symbol}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return float(data['price'])
        return None
    except Exception as e:
        print(f"❌ Errore prezzo {symbol}: {e}")
        return None

def calculate_portfolio():
    """Calcola portafoglio attuale"""
    # Simulazione - nella realtà leggeresti dal tuo sistema
    xrp_price = get_current_price(XRP_TICKER)
    if not xrp_price:
        return None
    
    # Dati dal performance report
    xrp_quantity = 762.06
    portfolio_value = 11153.10
    xrp_value = xrp_quantity * xrp_price
    
    xrp_weight = xrp_value / portfolio_value
    
    return {
        'xrp_quantity': xrp_quantity,
        'xrp_price': xrp_price,
        'xrp_value': xrp_value,
        'portfolio_value': portfolio_value,
        'xrp_weight': xrp_weight
    }

def main():
    # Analisi situazione attuale
    portfolio = calculate_portfolio()
    if not portfolio:
        print("❌ Impossibile analizzare portafoglio")
        return
    
    print(f"📊 ANALISI PORTAFOGLIO:")
    print(f"   XRP quantità: {portfolio['xrp_quantity']:.2f}")
    print(f"   Prezzo XRP: ${portfolio['xrp_price']:.4f}")
    print(f"   Valore XRP: ${portfolio['xrp_value']:.2f}")
    print(f"   Portafoglio totale: ${portfolio['portfolio_value']:.2f}")
    print(f"   Peso XRP: {portfolio['xrp_weight']:.1%}")
    
    # Decisione di diversificazione
    if portfolio['xrp_weight'] > MAX_XRP_WEIGHT:
        print(f"⚠️  XRP OVERCONCENTRATION: {portfolio['xrp_weight']:.1%} > {MAX_XRP_WEIGHT:.1%}")
        
        # Calcola quanto vendere
        target_reduction = portfolio['xrp_quantity'] * REDUCTION_TARGET
        new_xrp_quantity = portfolio['xrp_quantity'] - target_reduction
        new_xrp_value = new_xrp_quantity * portfolio['xrp_price']
        new_weight = new_xrp_value / portfolio['portfolio_value']
        
        print(f"🎯 STRATEGIA DIVERSIFICAZIONE:")
        print(f"   Vendere: {target_reduction:.2f} XRP")
        print(f"   Nuova quantità: {new_xrp_quantity:.2f} XRP")
        print(f"   Nuovo peso: {new_weight:.1%}")
        print(f"   Riduzione rischio: {(portfolio['xrp_weight'] - new_weight):.1%}")
        
        # Conferma azione
        print(f"✅ RACCOMANDAZIONE: VENDI {target_reduction:.0f} XRP")
        
    else:
        print(f"✅ XRP peso OK: {portfolio['xrp_weight']:.1%}")

if __name__ == "__main__":
    main()
