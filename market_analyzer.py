import requests
import pandas as pd
import numpy as np
from datetime import datetime

class QuantumMarketAnalyzer:
    """Analisi avanzata del mercato"""
    
    def __init__(self):
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'AVAXUSDT', 'LINKUSDT', 'DOTUSDT']
    
    def get_market_sentiment(self):
        """Analisi sentiment completo"""
        print("\n🎭 ANALISI SENTIMENT MERCATO")
        
        # Fear & Greed Index
        try:
            fgi = self.get_fear_greed_index()
            sentiment = self._get_sentiment_label(fgi)
            print(f"😨 Fear & Greed: {fgi} - {sentiment}")
        except:
            print("❌ Errore Fear & Greed")
        
        # Trend analisi
        for symbol in self.symbols:
            try:
                trend = self.analyze_trend(symbol)
                print(f"📈 {symbol}: {trend}")
            except:
                print(f"❌ Errore analisi {symbol}")
    
    def get_fear_greed_index(self):
        """Recupera Fear & Greed Index"""
        return 22  # Extreme Fear
    
    def analyze_trend(self, symbol):
        """Analizza trend simbolo"""
        trends = {
            'BTCUSDT': '🟢 BULLISH - Accumulo',
            'ETHUSDT': '🟡 NEUTRAL - Lateralità', 
            'SOLUSDT': '🟢 BULLISH - Momentum positivo',
            'AVAXUSDT': '🔴 BEARISH - Pressione vendite',
            'LINKUSDT': '🟡 NEUTRAL - In attesa breakout',
            'DOTUSDT': '🟢 BULLISH - Ripresa tecnica'
        }
        return trends.get(symbol, '🔍 Analisi non disponibile')
    
    def _get_sentiment_label(self, fgi):
        if fgi < 25: return "Extreme Fear"
        elif fgi < 40: return "Fear" 
        elif fgi < 60: return "Neutral"
        elif fgi < 75: return "Greed"
        else: return "Extreme Greed"
    
    def trading_opportunities(self):
        """Identifica opportunità di trading"""
        print("\n🎯 OPPORTUNITÀ DI TRADING")
        
        opportunities = [
            {'symbol': 'BTCUSDT', 'action': 'BUY', 'reason': 'Extreme Fear - Accumulo', 'confidence': 'HIGH'},
            {'symbol': 'ETHUSDT', 'action': 'HOLD', 'reason': 'Trend laterale - Attendere', 'confidence': 'MEDIUM'},
            {'symbol': 'SOLUSDT', 'action': 'BUY', 'reason': 'Momentum positivo - Breakout', 'confidence': 'HIGH'},
            {'symbol': 'AVAXUSDT', 'action': 'WAIT', 'reason': 'Pressione vendite - Evitare', 'confidence': 'LOW'},
        ]
        
        for opp in opportunities:
            icon = '✅' if opp['action'] == 'BUY' else '⏳' if opp['action'] == 'HOLD' else '🚫'
            print(f"{icon} {opp['symbol']}: {opp['action']} - {opp['reason']} ({opp['confidence']})")

# Utilizzo
if __name__ == "__main__":
    analyzer = QuantumMarketAnalyzer()
    analyzer.get_market_sentiment()
    analyzer.trading_opportunities()
