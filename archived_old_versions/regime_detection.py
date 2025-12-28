#!/usr/bin/env python3
"""
Regime Detection Module - Quantum Trading System
Identifica il regime di mercato corrente per adattare la strategia
"""

import pandas as pd
import numpy as np


def calculate_atr(df, period=14):
    """Calcola Average True Range"""
    high = df['high']
    low = df['low']
    close = df['close']
    
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    
    return atr.iloc[-1] if len(atr) > 0 else 0


def calculate_adx(df, period=14):
    """Calcola Average Directional Index"""
    high = df['high']
    low = df['low']
    close = df['close']
    
    # +DM e -DM
    up_move = high.diff()
    down_move = -low.diff()
    
    plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0))
    minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0))
    
    # ATR
    atr = calculate_atr(df, period)
    
    # Smoothed DI
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr) if atr > 0 else 0
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr) if atr > 0 else 0
    
    # ADX
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di) if (plus_di + minus_di) > 0 else 0
    adx = dx if isinstance(dx, (int, float)) else dx.rolling(window=period).mean().iloc[-1]
    
    return adx if not pd.isna(adx) else 0


def calculate_rsi(series, period=14):
    """Calcola RSI"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.iloc[-1] if len(rsi) > 0 and not pd.isna(rsi.iloc[-1]) else 50


def calculate_ema(series, period):
    """Calcola EMA"""
    return series.ewm(span=period, adjust=False).mean()


def detect_market_regime(df, fear_greed):
    """
    Identifica il regime di mercato corrente
    
    Returns:
        str: Uno tra:
            - PANIC_CAPITULATION: Extreme fear, oversold, alta volatilità
            - TREND_UP: Trend rialzista confermato
            - TREND_DOWN: Trend ribassista confermato
            - RANGE_CONSOLIDATION: Mercato laterale
            - HIGH_VOLATILITY: Alta volatilità senza direzione chiara
            - UNDEFINED: Regime non chiaro
    """
    
    # Calcola indicatori necessari
    atr = calculate_atr(df, 14)
    atr_mean = df['close'].rolling(20).std().mean() if len(df) > 20 else atr
    adx = calculate_adx(df, 14)
    rsi = calculate_rsi(df['close'], 14)
    
    # Calcola EMA per trend
    df_copy = df.copy()
    df_copy['ema_20'] = calculate_ema(df_copy['close'], 20)
    df_copy['ema_50'] = calculate_ema(df_copy['close'], 50)
    
    current_price = df['close'].iloc[-1]
    ema_20 = df_copy['ema_20'].iloc[-1]
    ema_50 = df_copy['ema_50'].iloc[-1]
    
    # Volume spike detection
    volume_mean = df['volume'].rolling(20).mean().iloc[-1]
    volume_current = df['volume'].iloc[-1]
    volume_spike = volume_current > volume_mean * 1.5 if volume_mean > 0 else False
    
    # REGIME 1: PANIC CAPITULATION (priorità massima)
    if fear_greed < 25 and float(rsi) < 35 and volume_spike:
        return "PANIC_CAPITULATION"
    
    # REGIME 2: STRONG DOWNTREND
    if float(adx) > 25 and current_price < ema_20 < ema_50:
        return "TREND_DOWN"
    
    # REGIME 3: STRONG UPTREND
    if float(adx) > 25 and current_price > ema_20 > ema_50:
        return "TREND_UP"
    
    # REGIME 4: RANGE / CONSOLIDATION
    if adx < 20 and atr < atr_mean:
        return "RANGE_CONSOLIDATION"
    
    # REGIME 5: HIGH VOLATILITY
    if float(atr) > float(atr_mean) * 1.5:
        return "HIGH_VOLATILITY"
    
    # Default
    return "UNDEFINED"


def get_position_size_based_on_regime(regime, base_size, portfolio_value):
    """
    Adatta la size della posizione in base al regime
    
    Args:
        regime: Regime corrente
        base_size: Size base calcolata (es. dal risk 2%)
        portfolio_value: Valore totale portfolio
    
    Returns:
        float: Size adattata
    """
    
    multipliers = {
        "PANIC_CAPITULATION": 0.5,    # Size ridotta per accumulo graduale
        "TREND_UP": 1.5,               # Size aumentata in uptrend
        "TREND_DOWN": 0.3,             # Size molto ridotta in downtrend
        "RANGE_CONSOLIDATION": 0.8,    # Size leggermente ridotta
        "HIGH_VOLATILITY": 0.6,        # Size ridotta per alta volatilità
        "UNDEFINED": 0.5               # Conservativo
    }
    
    multiplier = multipliers.get(regime, 1.0)
    adjusted_size = base_size * multiplier
    
    # Cap massimo: 25% del portfolio
    max_size = portfolio_value * 0.25
    
    return min(adjusted_size, max_size)


if __name__ == "__main__":
    # Test rapido
    print("🧪 Testing Regime Detection Module...")
    
    # Crea dati di test
    test_data = pd.DataFrame({
        'open': [100, 99, 98, 97, 95],
        'high': [101, 100, 99, 98, 96],
        'low': [99, 98, 97, 95, 94],
        'close': [100, 99, 98, 96, 95],
        'volume': [1000, 1200, 1500, 2000, 3000]
    })
    
    regime = detect_market_regime(test_data, fear_greed=23)
    print(f"✅ Detected Regime: {regime}")
    
    size = get_position_size_based_on_regime(regime, base_size=50, portfolio_value=200)
    print(f"✅ Adjusted Size: ${size:.2f}")
