#!/usr/bin/env python3
"""
Dip Buy Module - Quantum Trading System
Modulo dedicato alla strategia "Buy the Dip" durante panic selling
"""

import pandas as pd
import numpy as np


def calculate_rsi(series, period=14):
    """Calcola RSI"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.iloc[-1] if len(rsi) > 0 and not pd.isna(rsi.iloc[-1]) else 50


def calculate_bollinger_bands(series, period=20, std_dev=2):
    """Calcola Bollinger Bands"""
    sma = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    
    return {
        'upper': upper.iloc[-1] if len(upper) > 0 else series.iloc[-1] * 1.02,
        'middle': sma.iloc[-1] if len(sma) > 0 else series.iloc[-1],
        'lower': lower.iloc[-1] if len(lower) > 0 else series.iloc[-1] * 0.98
    }


def calculate_macd(series, fast=12, slow=26, signal=9):
    """Calcola MACD"""
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    
    return {
        'macd': macd_line.iloc[-1] if len(macd_line) > 0 else 0,
        'signal': signal_line.iloc[-1] if len(signal_line) > 0 else 0,
        'histogram': histogram.iloc[-1] if len(histogram) > 0 else 0
    }


def check_dip_buy_signal(df, fear_greed, portfolio_cash):
    """
    Genera segnale di acquisto durante i dip
    
    Condizioni per BUY THE DIP:
    1. Fear & Greed < 25 (extreme fear)
    2. RSI < 30 (oversold)
    3. Prezzo vicino alla Bollinger Band inferiore
    4. Volume spike (>150% della media)
    5. MACD in fase di inversione
    
    Returns:
        dict o None: {
            'signal': 'BUY_DIP',
            'size': float,
            'confidence': float (0-1),
            'reason': str
        }
    """
    
    # Calcola indicatori
    rsi = calculate_rsi(df['close'], 14)
    bb = calculate_bollinger_bands(df['close'], 20)
    macd = calculate_macd(df['close'])
    
    current_price = df['close'].iloc[-1]
    volume_mean = df['volume'].rolling(20).mean().iloc[-1]
    volume_current = df['volume'].iloc[-1]
    
    # Condizioni per dip buy
    conditions = {
        'extreme_fear': fear_greed < 25,
        'rsi_oversold': rsi < 30,
        'at_bb_lower': current_price <= bb['lower'] * 1.01,  # 1% di tolleranza
        'volume_spike': volume_current > volume_mean * 1.5 if volume_mean > 0 else False,
        'macd_reversal': macd['histogram'] > macd['histogram'] * 0.9  # In fase di inversione
    }
    
    # Conta quante condizioni sono soddisfatte
    score = sum(conditions.values())
    total_conditions = len(conditions)
    confidence = score / total_conditions
    
    # Genera segnale se almeno 3/5 condizioni soddisfatte
    if score >= 3:
        # Calcola size (10-20% del cash disponibile)
        size_pct = 0.10 + (confidence * 0.10)  # 10-20% based on confidence
        size = portfolio_cash * size_pct
        
        # Crea reason string
        reasons = [k for k, v in conditions.items() if v]
        reason = ", ".join(reasons)
        
        return {
            'signal': 'BUY_DIP',
            'size': size,
            'confidence': confidence,
            'reason': reason,
            'rsi': rsi,
            'fear_greed': fear_greed
        }
    
    return None


def calculate_dip_scaling(current_price, entry_price, atr):
    """
    Calcola scaling per accumulo graduale durante i dip
    
    Strategy: Se il prezzo scende ulteriormente dopo il primo acquisto,
    compra di nuovo con size incrementale (averaging down controllato)
    
    Returns:
        dict o None: {
            'should_scale': bool,
            'scale_multiplier': float
        }
    """
    
    price_drop_pct = (entry_price - current_price) / entry_price
    
    # Se il prezzo è sceso di più di 1x ATR, considera scaling
    if price_drop_pct > (atr / entry_price):
        # Scala fino a max 2x la size originale
        scale_multiplier = min(1.5, 1 + price_drop_pct * 5)
        
        return {
            'should_scale': True,
            'scale_multiplier': scale_multiplier
        }
    
    return {'should_scale': False, 'scale_multiplier': 1.0}


def is_capitulation_pattern(df):
    """
    Rileva pattern di capitulation (panic selling estremo)
    
    Pattern:
    - Candle con body lungo (>5% drop)
    - Long lower wick (>2x del body)
    - Volume spike estremo (>200%)
    
    Returns:
        bool: True se pattern di capitulation rilevato
    """
    
    last_candle = df.iloc[-1]
    body = abs(last_candle['close'] - last_candle['open'])
    lower_wick = min(last_candle['open'], last_candle['close']) - last_candle['low']
    
    # Volume spike
    volume_mean = df['volume'].rolling(20).mean().iloc[-2]
    volume_spike = last_candle['volume'] > volume_mean * 2 if volume_mean > 0 else False
    
    # Drop percentage
    drop_pct = abs(last_candle['close'] - last_candle['open']) / last_candle['open']
    
    # Condizioni capitulation
    is_big_drop = drop_pct > 0.05  # >5% drop
    has_long_wick = lower_wick > body * 2
    has_volume = volume_spike
    
    return is_big_drop and has_long_wick and has_volume


if __name__ == "__main__":
    # Test rapido
    print("🧪 Testing Dip Buy Module...")
    
    # Crea dati di test (panic selling scenario)
    test_data = pd.DataFrame({
        'open': [100, 98, 95, 92, 88],
        'high': [101, 99, 96, 93, 89],
        'low': [99, 97, 94, 90, 85],  # Long wick on last candle
        'close': [99, 97, 94, 91, 87],
        'volume': [1000, 1200, 1500, 2000, 3500]  # Volume spike
    })
    
    signal = check_dip_buy_signal(test_data, fear_greed=23, portfolio_cash=200)
    
    if signal:
        print(f"✅ Signal: {signal['signal']}")
        print(f"   Confidence: {signal['confidence']:.2%}")
        print(f"   Size: ${signal['size']:.2f}")
        print(f"   Reason: {signal['reason']}")
    else:
        print("⚠️  No signal (normal if conditions not met)")
    
    capitulation = is_capitulation_pattern(test_data)
    print(f"✅ Capitulation Pattern: {capitulation}")
