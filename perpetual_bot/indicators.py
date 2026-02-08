"""
Technical Indicators for Perpetual Bot
"""
import pandas as pd
import numpy as np

class TechnicalIndicators:
    """Calculate all technical indicators"""
    
    @staticmethod
    def calculate_ema(prices, period):
        """Exponential Moving Average"""
        return prices.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        """Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_atr(high, low, close, period=14):
        """Average True Range"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr
    
    @staticmethod
    def calculate_all(df, config):
        """Calculate all indicators at once"""
        indicators = {}
        
        # EMAs
        indicators['ema_200'] = TechnicalIndicators.calculate_ema(
            df['close'], config['indicators']['ema_long']
        )
        indicators['ema_50'] = TechnicalIndicators.calculate_ema(
            df['close'], config['indicators']['ema_med']
        )
        indicators['ema_20'] = TechnicalIndicators.calculate_ema(
            df['close'], config['indicators']['ema_short']
        )
        
        # RSI
        indicators['rsi'] = TechnicalIndicators.calculate_rsi(
            df['close'], config['indicators']['rsi_period']
        )
        
        # ATR
        indicators['atr'] = TechnicalIndicators.calculate_atr(
            df['high'], df['low'], df['close'],
            config['indicators']['atr_period']
        )
        
        # ATR Percentage
        indicators['atr_pct'] = (indicators['atr'] / df['close']) * 100
        
        # Volume MA
        indicators['volume_ma'] = df['volume'].rolling(
            window=config['indicators']['volume_ma']
        ).mean()
        
        return indicators

if __name__ == "__main__":
    # Test indicators
    import ccxt
    
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1h', limit=250)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    config = {
        'indicators': {
            'ema_long': 200,
            'ema_med': 50,
            'ema_short': 20,
            'rsi_period': 14,
            'atr_period': 14,
            'volume_ma': 20
        }
    }
    
    indicators = TechnicalIndicators.calculate_all(df, config)
    
    print("📊 INDICATORS TEST:")
    print(f"  EMA 200: {indicators['ema_200'].iloc[-1]:.2f}")
    print(f"  EMA 50: {indicators['ema_50'].iloc[-1]:.2f}")
    print(f"  EMA 20: {indicators['ema_20'].iloc[-1]:.2f}")
    print(f"  RSI: {indicators['rsi'].iloc[-1]:.2f}")
    print(f"  ATR %: {indicators['atr_pct'].iloc[-1]:.4f}%")
    print("✅ All indicators working!")
