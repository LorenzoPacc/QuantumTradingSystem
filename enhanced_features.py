"""Enhanced Features - MINIMAL VERSION (3 features only)"""
import numpy as np
import pandas as pd

class EnhancedFeatures:
    """Solo 3 features essenziali - zero rischio"""
    
    def compute_all(self, ohlcv_df):
        """Calcola 3 features core"""
        return {
            'volatility_regime': self._volatility_clustering(ohlcv_df),
            'volume_strength': self._volume_analysis(ohlcv_df),
            'market_efficiency': self._hurst_exponent(ohlcv_df)
        }
    
    def _volatility_clustering(self, df):
        """Volatilità alta = rischio"""
        returns = df['close'].pct_change()
        vol_short = returns.rolling(10).std()
        vol_long = returns.rolling(50).std()
        
        vol_ratio = vol_short.iloc[-1] / vol_long.iloc[-1]
        
        return {
            'vol_ratio': vol_ratio,
            'regime': 'HIGH_VOL' if vol_ratio > 1.5 else 'NORMAL'
        }
    
    def _volume_analysis(self, df):
        """Volume conferma movimento"""
        volume_ma = df['volume'].rolling(20).mean()
        volume_current = df['volume'].iloc[-1]
        volume_ratio = volume_current / volume_ma.iloc[-1]
        
        return {
            'volume_confirmation': volume_ratio > 1.2,
            'strength': volume_ratio
        }
    
    def _hurst_exponent(self, df, lags=100):
        """Trending vs Mean-Reverting"""
        try:
            prices = df['close'].values[-min(lags, len(df)):]
            
            lags_range = range(2, min(20, len(prices)//2))
            tau = [np.std(np.subtract(prices[lag:], prices[:-lag])) for lag in lags_range]
            
            poly = np.polyfit(np.log(lags_range), np.log(tau), 1)
            hurst = poly[0]
            
            if hurst > 0.55:
                regime = 'TRENDING'
            elif hurst < 0.45:
                regime = 'MEAN_REVERTING'
            else:
                regime = 'RANDOM'
            
            return {'hurst': hurst, 'regime': regime}
        except:
            return {'hurst': 0.5, 'regime': 'UNKNOWN'}

# Quick test
if __name__ == "__main__":
    import ccxt
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1h', limit=200)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    enhancer = EnhancedFeatures()
    features = enhancer.compute_all(df)
    
    print("📊 ENHANCED FEATURES TEST:")
    for name, value in features.items():
        print(f"  {name}: {value}")
