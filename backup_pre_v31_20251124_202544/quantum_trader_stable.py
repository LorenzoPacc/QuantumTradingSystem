#!/usr/bin/env python3
"""
QUANTUM TRADER - VERSIONE STABILE DEFINITIVA
✅ Balance sempre verificato
✅ Gestione ordini sicura
✅ Recovery automatico
"""

import requests
import hmac
import hashlib
import time
import json
from datetime import datetime, timedelta
import logging
import numpy as np
from typing import Dict, List, Tuple, Optional

# Import database
from quantum_database import db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("QuantumStable")

class StableTrader:
    def __init__(self):
        # API Config - TESTNET
        self.api_key = "EXyS3Fvmsrb9pCKjQMuJSlLiUIWYih5JiglIsiRzvLDR2tzJS60r3DXzknca0FC1"
        self.api_secret = "yvPlsaFwUg8XaBejUmptovSRH3XjQ6lOeGTRwbDprV2tAXs5naD6y1dsWbcmb2aI"
        self.base_url = "https://testnet.binance.vision"
        
        # Trading Config CONSERVATIVO
        self.symbols = ["BTCUSDT", "ETHUSDT"]
        self.min_confluence = 2.5  # Più conservativo
        self.min_confidence = 0.70  # 70% confidence
        self.max_risk_per_trade = 0.10  # Solo 10% del balance
        self.trade_cooldown = 300  # 5 minuti tra trade
        
        # Stato sistema
        self.last_trade_time = 0
        self.current_balance = 0.0
        self.available_balance = 0.0
        
        # Inizializza balance
        self._initialize_balance()
    
    def _initialize_balance(self):
        """Inizializza balance all'avvio"""
        self.current_balance = self.get_balance_verified()
        self.available_balance = self.current_balance
        logger.info(f"💰 BALANCE INIZIALE: ${self.current_balance:.2f}")
    
    def _sign_request(self, params: str) -> str:
        """Crea signature per API"""
        return hmac.new(
            self.api_secret.encode('utf-8'),
            params.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def get_balance_verified(self) -> float:
        """
        Ottieni balance CON VERIFICA A DOPPIO STRATO
        """
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                timestamp = int(time.time() * 1000)
                query_string = f"timestamp={timestamp}"
                signature = self._sign_request(query_string)
                
                url = f"{self.base_url}/api/v3/account?{query_string}&signature={signature}"
                headers = {"X-MBX-APIKEY": self.api_key}
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Cerca USDT
                    usdt_balance = 0.0
                    available_usdt = 0.0
                    
                    for balance in data['balances']:
                        if balance['asset'] == 'USDT':
                            usdt_balance = float(balance['free']) + float(balance['locked'])
                            available_usdt = float(balance['free'])
                            break
                    
                    # Verifica consistenza
                    if usdt_balance >= 0 and available_usdt >= 0:
                        # Salva nel database
                        db.log_balance(usdt_balance, available_usdt)
                        
                        logger.info(f"✅ BALANCE VERIFICATO: ${usdt_balance:.2f} (Disponibile: ${available_usdt:.2f})")
                        self.current_balance = usdt_balance
                        self.available_balance = available_usdt
                        
                        return usdt_balance
                    else:
                        logger.warning(f"⚠️  Balance negativo, riprovo...")
                
                else:
                    logger.warning(f"⚠️  API Balance fallita (attempt {attempt+1}): {response.status_code}")
            
            except Exception as e:
                logger.warning(f"⚠️  Errore balance (attempt {attempt+1}): {e}")
            
            time.sleep(1)
        
        # Se tutti i tentativi falliscono, usa ultimo balance dal DB
        last_balance, last_available = db.get_last_balance()
        if last_balance > 0:
            logger.warning(f"🔄 USING CACHED BALANCE: ${last_balance:.2f}")
            self.current_balance = last_balance
            self.available_balance = last_available
            return last_balance
        
        logger.error("💥 IMPOSSIBILE OTTENERE BALANCE!")
        return 0.0
    
    def get_klines(self, symbol: str, interval: str = "1h", limit: int = 100) -> List:
        """Ottieni candele con ritry"""
        try:
            url = f"{self.base_url}/api/v3/klines"
            params = {'symbol': symbol, 'interval': interval, 'limit': limit}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return []
        except:
            return []
    
    def analyze_macro(self) -> Tuple[float, str]:
        """Analisi macro semplificata ma robusta"""
        try:
            btc_price = self.get_price("BTCUSDT")
            
            if btc_price > 110000:
                return 0.8, f"BTC ${btc_price:,.0f} > $110k (bullish)"
            elif btc_price > 100000:
                return 0.6, f"BTC ${btc_price:,.0f} > $100k (neutro)"
            else:
                return 0.4, f"BTC ${btc_price:,.0f} (cautela)"
        except:
            return 0.5, "Analisi macro non disponibile"
    
    def analyze_price_action(self, symbol: str) -> Tuple[float, str]:
        """Analisi price action robusta"""
        try:
            klines = self.get_klines(symbol, "1h", 50)
            if not klines or len(klines) < 20:
                return 0.5, "Dati insufficienti"
            
            closes = np.array([float(k[4]) for k in klines])
            volumes = np.array([float(k[5]) for k in klines])
            
            vwap = np.sum(closes * volumes) / np.sum(volumes)
            current_price = closes[-1]
            
            if current_price > vwap * 1.02:
                return 0.8, f"Price ${current_price:.2f} > VWAP ${vwap:.2f} (bullish)"
            elif current_price > vwap:
                return 0.6, f"Price ${current_price:.2f} > VWAP ${vwap:.2f} (leggero bullish)"
            else:
                return 0.4, f"Price ${current_price:.2f} < VWAP ${vwap:.2f} (cautela)"
        except:
            return 0.5, "Errore analisi price action"
    
    def analyze_onchain(self, symbol: str) -> Tuple[float, str]:
        """Analisi on-chain semplificata"""
        try:
            klines = self.get_klines(symbol, "1d", 20)
            if not klines:
                return 0.5, "Dati insufficienti"
            
            volumes = np.array([float(k[5]) for k in klines])
            avg_volume = np.mean(volumes[-5:])  # Ultimi 5 giorni
            
            if avg_volume > np.mean(volumes) * 1.2:
                return 0.7, "Volume sopra media (bullish)"
            else:
                return 0.5, "Volume nella norma"
        except:
            return 0.5, "Dati on-chain non disponibili"
    
    def analyze_cycles(self) -> Tuple[float, str]:
        """Analisi cicli halving"""
        try:
            last_halving = datetime(2024, 4, 20)
            days_since_halving = (datetime.now() - last_halving).days
            
            if days_since_halving < 180:
                return 0.8, f"{days_since_halving} giorni post-halving (fase forte)"
            elif days_since_halving < 365:
                return 0.7, f"{days_since_halving} giorni post-halving (bull market)"
            else:
                return 0.5, f"{days_since_halving} giorni post-halving (maturo)"
        except:
            return 0.5, "Analisi cicli non disponibile"
    
    def calculate_confluence(self, symbol: str) -> Dict:
        """Calcola confluence score"""
        logger.info(f"\n🎯 ANALISI CONFLUENCE: {symbol}")
        
        # Esegui analisi
        macro_score, macro_reason = self.analyze_macro()
        price_score, price_reason = self.analyze_price_action(symbol)
        onchain_score, onchain_reason = self.analyze_onchain(symbol)
        cycles_score, cycles_reason = self.analyze_cycles()
        
        # Calcola weighted confluence
        weights = [0.3, 0.3, 0.25, 0.15]
        scores = [macro_score, price_score, onchain_score, cycles_score]
        
        confluence = sum(s * w for s, w in zip(scores, weights))
        confluence_scaled = confluence * 4
        
        # Determina signal
        if confluence_scaled >= self.min_confluence and confluence >= self.min_confidence:
            signal = "BUY" if confluence >= 0.6 else "SELL"
        else:
            signal = "HOLD"
        
        result = {
            'symbol': symbol,
            'confluence': confluence_scaled,
            'confidence': confluence,
            'signal': signal,
            'factors': {
                'macro': macro_score,
                'price_action': price_score,
                'onchain': onchain_score,
                'cycles': cycles_score
            }
        }
        
        logger.info(f"📊 RISULTATO: Confluence {confluence_scaled:.2f}/4.0 - Confidence {confluence:.2%} - Signal: {signal}")
        
        return result
    
    def get_price(self, symbol: str) -> float:
        """Ottieni prezzo corrente"""
        try:
            url = f"{self.base_url}/api/v3/ticker/price?symbol={symbol}"
            response = requests.get(url, timeout=5)
            return float(response.json()['price'])
        except:
            return 0.0
    
    def calculate_position_size(self, symbol: str, price: float) -> float:
        """Calcola position size sicuro"""
        # Usa available_balance per sicurezza
        position_usd = self.available_balance * self.max_risk_per_trade
        
        # Minimo $10, massimo 90% disponibile
        min_notional = 10.0
        max_notional = self.available_balance * 0.9
        
        position_usd = max(min_notional, min(position_usd, max_notional))
        
        quantity = position_usd / price
        
        # Arrotondamento sicuro
        if "BTC" in symbol:
            quantity = round(quantity, 5)
        elif "ETH" in symbol:
            quantity = round(quantity, 4)
        else:
            quantity = round(quantity, 3)
        
        logger.info(f"📏 POSITION SIZE: ${position_usd:.2f} = {quantity} {symbol}")
        
        return quantity
    
    def verify_order_safe(self, symbol: str, side: str, quantity: float, price: float) -> bool:
        """Verifica se l'ordine è sicuro prima di eseguire"""
        try:
            # 1. Verifica cooldown
            current_time = time.time()
            if current_time - self.last_trade_time < self.trade_cooldown:
                logger.warning(f"⏳ Cooldown attivo, aspetta {(self.trade_cooldown - (current_time - self.last_trade_time))//60} minuti")
                return False
            
            # 2. Verifica balance
            required_usd = quantity * price
            if required_usd > self.available_balance * 0.95:
                logger.warning(f"⚠️  Ordine troppo grande: ${required_usd:.2f} > ${self.available_balance * 0.95:.2f}")
                return False
            
            # 3. Verifica prezzo realistico
            current_price = self.get_price(symbol)
            if abs(price - current_price) / current_price > 0.05:  # 5% tolerance
                logger.warning(f"⚠️  Prezzo non realistico: ${price:.2f} vs ${current_price:.2f}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Verifica ordine fallita: {e}")
            return False
    
    def place_order(self, symbol: str, side: str, quantity: float, price: float) -> Tuple[bool, str]:
        """Piazza ordine CON CONTROLLI MULTIPLI"""
        try:
            # Verifica sicurezza ordine
            if not self.verify_order_safe(symbol, side, quantity, price):
                return False, "Ordine non sicuro"
            
            timestamp = int(time.time() * 1000)
            query_string = f"symbol={symbol}&side={side}&type=LIMIT&timeInForce=GTC&quantity={quantity}&price={price:.2f}&timestamp={timestamp}"
            
            signature = self._sign_request(query_string)
            
            url = f"{self.base_url}/api/v3/order?{query_string}&signature={signature}"
            headers = {"X-MBX-APIKEY": self.api_key}
            
            logger.info(f"🚀 TENTATIVO ORDINE: {symbol} {side} {quantity} @ ${price:.2f}")
            
            response = requests.post(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                order_data = response.json()
                order_id = str(order_data['orderId'])
                
                # Salva trade come OPEN
                db.log_trade(symbol, side, quantity, price, 'OPEN', order_id)
                
                # Aggiorna last trade time
                self.last_trade_time = time.time()
                
                logger.info(f"✅ ORDINE ESEGUITO! ID: {order_id}")
                return True, order_id
            else:
                error_msg = f"API Error: {response.status_code} - {response.text}"
                logger.error(f"❌ ORDINE FALLITO: {error_msg}")
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            logger.error(f"💥 ECCEZIONE ORDINE: {error_msg}")
            return False, error_msg
    
    def run_trading_cycle(self):
        """Ciclo di trading principale"""
        logger.info(f"\n{'='*50}")
        logger.info(f"🔄 CICLO TRADING - {datetime.now().strftime('%H:%M:%S')}")
        logger.info(f"{'='*50}")
        
        # 1. AGGIORNA BALANCE (CRITICO)
        balance = self.get_balance_verified()
        
        if balance < 5:
            logger.warning(f"🚫 BALANCE INSUFFICIENTE: ${balance:.2f} < $15")
            return False
        
        # 2. ANALIZZA OGNI SYMBOL
        for symbol in self.symbols:
            try:
                analysis = self.calculate_confluence(symbol)
                
                if analysis['signal'] in ['BUY', 'SELL']:
                    price = self.get_price(symbol)
                    quantity = self.calculate_position_size(symbol, price)
                    
                    logger.info(f"🎯 SEGNALE {analysis['signal']} PER {symbol}")
                    logger.info(f"   Prezzo: ${price:.2f}")
                    logger.info(f"   Quantità: {quantity}")
                    logger.info(f"   Investimento: ${quantity * price:.2f}")
                    
                    # Piazza ordine
                    success, order_id = self.place_order(symbol, analysis['signal'], quantity, price)
                    
                    if success:
                        logger.info(f"🎉 TRADE ESEGUITO CON SUCCESSO!")
                        
                        # Aggiorna balance dopo trade
                        time.sleep(2)
                        self.get_balance_verified()
                        
                        return True  # Un trade per ciclo
            
            except Exception as e:
                logger.error(f"❌ Errore con {symbol}: {e}")
                continue
        
        logger.info("⏭️  Nessun trade questo ciclo")
        return False
    
    def run(self):
        """Loop principale con gestione errori robusta"""
        logger.info(f"\n{'#'*60}")
        logger.info(f"🚀 QUANTUM STABLE TRADER AVVIATO")
        logger.info(f"💰 Balance iniziale: ${self.current_balance:.2f}")
        logger.info(f"⚙️  Config: Risk {self.max_risk_per_trade:.0%}, Min Confluence {self.min_confluence}")
        logger.info(f"{'#'*60}")
        
        cycle_count = 0
        error_count = 0
        
        while error_count < 5:  # Massimo 5 errori consecutivi
            try:
                cycle_count += 1
                logger.info(f"\n📈 CICLO #{cycle_count}")
                
                success = self.run_trading_cycle()
                
                if success:
                    error_count = 0  # Reset error counter
                else:
                    error_count += 1
                
                # Wait per prossimo ciclo
                wait_time = 300  # 5 minuti
                logger.info(f"⏳ Prossimo ciclo tra {wait_time//60} minuti...")
                time.sleep(wait_time)
                
            except KeyboardInterrupt:
                logger.info("\n🛑 FERMATO DALL'UTENTE")
                break
            except Exception as e:
                error_count += 1
                logger.error(f"💥 ERRORE CICLO: {e}")
                logger.info("😴 Attendo 60s prima di riprovare...")
                time.sleep(60)
        
        if error_count >= 5:
            logger.error("🚨 TROPPI ERRORI, SISTEMA FERMATO")

if __name__ == "__main__":
    trader = StableTrader()
    trader.run()
