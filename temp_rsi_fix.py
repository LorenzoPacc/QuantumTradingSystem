def calculate_rsi_fixed(prices, period=14):
    if len(prices) < period + 1:
        return 50.0
    
    try:
        import numpy as np
        
        deltas = np.diff(prices)
        up = deltas[deltas >= 0]
        down = -deltas[deltas < 0]
        
        if len(up) == 0 or len(down) == 0:
            return 50.0
        
        avg_gain = np.mean(up[:period]) if len(up) >= period else np.mean(up)
        avg_loss = np.mean(down[:period]) if len(down) >= period else np.mean(down)
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))
        
        return max(0.0, min(100.0, rsi))
    except:
        return 50.0
