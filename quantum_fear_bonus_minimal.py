import time
import logging
import random

class QuantumTrader:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.log = logging.getLogger(__name__)
        
    def get_fear_greed_index(self):
        """Simula Fear & Greed Index"""
        # Per test, restituisce Extreme Fear (25)
        return 25
    
    def get_price(self, symbol):
        """Simula prezzo"""
        return 45000.0
    
    def check_buy(self, symbol):
        """Versione MINIMALE con FEAR BONUS funzionante"""
        # Simula dati
        base_confidence = 33.0  # Confidence base (come nei log)
        fear_index = self.get_fear_greed_index()
        
        # 🚀 FEAR BONUS
        if fear_index < 30:  # EXTREME FEAR
            confidence = base_confidence * 1.25
            self.log.info(f"🚀 FEAR BONUS APPLIED: +25% (F&G: {fear_index}) | Confidence: {base_confidence:.1f}% → {confidence:.1f}%")
        elif fear_index < 45:  # FEAR
            confidence = base_confidence * 1.15
            self.log.info(f"📈 Fear bonus: +15% (F&G: {fear_index}) | Confidence: {base_confidence:.1f}% → {confidence:.1f}%")
        else:
            confidence = base_confidence
        
        # Auto-buy logic
        if confidence >= 40.0:
            self.log.info(f"✅ BUY SIGNAL: {symbol} - Confidence: {confidence:.1f}% (F&G: {fear_index})")
            return True, {"confidence": confidence, "fear_index": fear_index}
        else:
            self.log.info(f"📊 {symbol}: Confidence: {confidence:.1f}% (F&G: {fear_index}) - Too low for buy")
            return False, f"Low confidence ({confidence:.1f}% < 40%)"
    
    def run(self):
        self.log.info("🚀 QuantumTrader MINIMAL con FEAR BONUS avviato!")
        self.log.info("📊 Fear & Greed: 25 (EXTREME FEAR)")
        self.log.info("🎯 Auto-buy threshold: 40%")
        self.log.info("="*60)
        
        cycle = 0
        while True:
            cycle += 1
            self.log.info(f"\n🔁 CICLO {cycle}")
            
            # Test su vari simboli
            symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
            for symbol in symbols:
                result, info = self.check_buy(symbol)
                if result:
                    self.log.info(f"🎯 ACQUISTO APPROVATO per {symbol}!")
            
            time.sleep(60)  # 1 minuto tra i cicli

if __name__ == "__main__":
    trader = QuantumTrader()
    trader.run()
