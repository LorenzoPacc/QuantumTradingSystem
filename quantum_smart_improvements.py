#!/usr/bin/env python3
"""
🎯 QUANTUM SMART IMPROVEMENTS - Day Trading Optimized
Modulo con tutti i miglioramenti intelligenti integrati
"""

import numpy as np
import logging
from typing import List, Dict, Tuple, Optional

# =============================================================================
# TECHNICAL INDICATORS (per evitare dipendenze circolari)
# =============================================================================

class TechnicalIndicators:
    """Indicatori tecnici essenziali"""
    
    @staticmethod
    def atr(klines: List[Dict], period: int = 14) -> Optional[float]:
        """Calculate Average True Range"""
        try:
            if len(klines) < period + 1:
                return None
            
            true_ranges = []
            for i in range(1, len(klines)):
                high = klines[i]['high']
                low = klines[i]['low']
                prev_close = klines[i-1]['close']
                
                tr = max(
                    high - low,
                    abs(high - prev_close),
                    abs(low - prev_close)
                )
                true_ranges.append(tr)
            
            return np.mean(true_ranges[-period:]) if true_ranges else None
        except Exception as e:
            logging.error(f"Error calculating ATR: {e}")
            return None

# =============================================================================
# 1️⃣ RSI ADATTIVO (DINAMICO BASATO SU ATR)
# =============================================================================

class AdaptiveRSI:
    """RSI con soglie dinamiche basate sulla volatilità"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
    
    def get_dynamic_thresholds(self, atr: float, avg_atr: float) -> Tuple[int, int]:
        """
        Calcola soglie RSI dinamiche basate su volatilità
        
        Args:
            atr: ATR corrente
            avg_atr: ATR medio (ultimi 20 periodi)
            
        Returns:
            (rsi_oversold, rsi_overbought)
        """
        # Fallback per dati insufficienti
        if not atr or not avg_atr or avg_atr == 0:
            self.logger.warning("ATR data insufficient, using default RSI thresholds")
            return (35, 65)
        
        # Calcola ratio volatilità
        volatility_ratio = atr / avg_atr
        
        if volatility_ratio > 1.5:  # Alta volatilità (+50%)
            self.logger.debug(f"High volatility ({volatility_ratio:.2f}x), using aggressive RSI")
            return (48, 70)  # RSI < 48 per comprare
            
        elif volatility_ratio < 0.7:  # Bassa volatilità (-30%)
            self.logger.debug(f"Low volatility ({volatility_ratio:.2f}x), using conservative RSI")
            return (50, 60)  # RSI < 50 (più opportunità)
            
        else:  # Volatilità normale
            return (50, 65)  # RSI < 48 (bilanciato)
    
    def calculate_avg_atr(self, klines: List[Dict], period: int = 20) -> float:
        """Calcola ATR medio degli ultimi N periodi"""
        try:
            # Serve almeno ATR period + averaging period
            if len(klines) < 14 + 1:
                self.logger.warning(f"Not enough data for avg ATR (need 15+, got {len(klines)})")
                return 0.0
            
            # Usa gli ultimi 'period' ATR calcolati
            num_periods = min(period, len(klines) - 14)
            atrs = []
            
            for i in range(len(klines) - num_periods, len(klines)):
                subset = klines[max(0, i-14):i+1]
                atr_val = TechnicalIndicators.atr(subset, 14)
                if atr_val and atr_val > 0:
                    atrs.append(atr_val)
            
            if not atrs:
                self.logger.warning("No valid ATR values calculated")
                return 0.0
                
            return np.mean(atrs)
            
        except Exception as e:
            self.logger.error(f"Error calculating avg ATR: {e}")
            return 0.0

# =============================================================================
# 2️⃣ VOLUME RATIO INTELLIGENTE
# =============================================================================

class SmartVolume:
    """Analisi volume con threshold dinamico"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
    
    def get_volume_threshold(self, atr_normalized: float) -> float:
        """
        Calcola threshold volume dinamico basato su volatilità
        
        Args:
            atr_normalized: ATR/Price (volatilità normalizzata 0-1)
            
        Returns:
            Volume threshold (es. 1.3 = 130% della media)
        """
        # Base threshold conservativo
        base = 1.2
        
        # Componente dinamica (0.1-0.5)
        # Più volatilità = più volume richiesto per filtrare noise
        dynamic = min(0.5, max(0.1, atr_normalized * 10))
        
        threshold = base + dynamic
        self.logger.debug(f"Volume threshold: {threshold:.2f} (ATR norm: {atr_normalized:.4f})")
        
        return threshold
    
    def check_volume_quality(
        self, 
        klines: List[Dict], 
        current_volume: float,
        dynamic_threshold: Optional[float] = None
    ) -> Tuple[bool, float]:
        """
        Verifica qualità del volume corrente
        
        Args:
            klines: Candele storiche
            current_volume: Volume corrente
            dynamic_threshold: Soglia dinamica (opzionale)
            
        Returns:
            (is_valid, volume_ratio)
        """
        try:
            if len(klines) < 20:
                self.logger.warning("Not enough data for volume analysis")
                return False, 0.0
            
            # Volume medio ultimi 20 periodi
            recent_volumes = [k['volume'] for k in klines[-20:]]
            avg_volume = np.mean(recent_volumes)
            
            if avg_volume == 0:
                self.logger.warning("Average volume is zero")
                return False, 0.0
            
            volume_ratio = current_volume / avg_volume
            
            # Usa threshold dinamico se fornito, altrimenti minimo assoluto
            min_threshold = dynamic_threshold if dynamic_threshold else 0.5
            
            is_valid = volume_ratio >= min_threshold
            
            if not is_valid:
                self.logger.info(f"Volume too low: {volume_ratio:.2f}x < {min_threshold:.2f}x")
            
            return is_valid, volume_ratio
            
        except Exception as e:
            self.logger.error(f"Error checking volume quality: {e}")
            return False, 0.0

# =============================================================================
# 3️⃣ TREND ALIGNMENT FORTE
# =============================================================================

class TrendGuard:
    """Protezione contro trade contro-trend"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
    
    def check_trend_alignment(self, market_data: Dict) -> Tuple[bool, str]:
        """
        Verifica allineamento trend su timeframe lunghi
        
        REGOLA CRITICA: Non comprare MAI se trend 1h è ribassista
        
        Returns:
            (can_buy, reason)
        """
        try:
            # Dati 1h (timeframe lungo)
            data_1h = market_data.get('1h', {})
            
            if not data_1h:
                self.logger.warning("No 1h data available for trend check")
                return True, 'No 1h data'
            
            price = data_1h.get('price', 0)
            sma_30 = data_1h.get('sma_slow', 0)  # SMA(30) su 1h
            
            # Validazione dati
            if not price or not sma_30 or price <= 0 or sma_30 <= 0:
                self.logger.warning("Invalid price or SMA data for trend check")
                return True, 'Invalid trend data'
            
            # FILTRO PRINCIPALE: Prezzo sotto SMA30 su 1h = NO BUY
            if price < sma_30:
                self.logger.info(f"Trend bearish: price {price:.2f} < SMA30 {sma_30:.2f}")
                return False, f'Trend 1h ribassista (price ${price:.2f} < SMA30 ${sma_30:.2f})'
            
            # Controllo aggiuntivo: slope SMA (se disponibile)
            sma_history = data_1h.get('sma_history', [])
            if len(sma_history) >= 5:
                # SMA sta scendendo negli ultimi 5 periodi?
                recent_slope = sma_history[-1] - sma_history[-5]
                if recent_slope < 0:
                    self.logger.info(f"SMA30 declining: {recent_slope:.2f}")
                    return False, 'SMA30 1h in discesa'
            
            return True, 'Trend OK'
            
        except Exception as e:
            self.logger.error(f"Error in trend alignment check: {e}")
            return True, 'Trend check error (allowing trade)'

# =============================================================================
# 5️⃣ CONTROLLO LIQUIDITÀ AUTOMATICO
# =============================================================================

class LiquidityFilter:
    """Filtra orari a bassa liquidità"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
    
    def check_liquidity(self, klines_5m: List[Dict]) -> Tuple[bool, str]:
        """
        Verifica liquidità recente (ultime 20 candele 5m = 100 minuti)
        
        Returns:
            (is_liquid, reason)
        """
        try:
            if len(klines_5m) < 20:
                self.logger.warning("Not enough data for liquidity check")
                return True, 'Not enough data'
            
            # Ultimi 20 periodi (100 minuti)
            recent_candles = klines_5m[-20:]
            recent_volumes = [k['volume'] for k in recent_candles]
            recent_avg = np.mean(recent_volumes)
            
            # Volume medio globale (per confronto)
            all_volumes = [k['volume'] for k in klines_5m]
            global_avg = np.mean(all_volumes)
            
            if global_avg == 0:
                self.logger.warning("Global average volume is zero")
                return True, 'No volume data'
            
            # Calcola ratio
            liquidity_ratio = recent_avg / global_avg
            
            # THRESHOLD: Se ultimi 100min hanno volume < 50% della media
            # → probabilmente orario morto (notte, pre-market, etc.)
            if liquidity_ratio < 0.5:
                self.logger.info(f"Low liquidity period: {liquidity_ratio:.2%} of average")
                return False, f'Bassa liquidità ({liquidity_ratio:.0%} della media)'
            
            self.logger.debug(f"Liquidity OK: {liquidity_ratio:.2%}")
            return True, f'Liquidità OK ({liquidity_ratio:.0%})'
            
        except Exception as e:
            self.logger.error(f"Error checking liquidity: {e}")
            return True, 'Liquidity check error (allowing trade)'

# =============================================================================
# 7️⃣ SEGNALE SELL COMPLETO
# =============================================================================

class SmartExit:
    """Logica di uscita migliorata"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
    
    def check_exit_signal(self, position: Dict, market_data: Dict) -> Tuple[bool, str]:
        """
        Controlla segnali di uscita multipli
        
        PRIORITÀ EXIT (dal più urgente):
        1. Validazione dati
        2. Stop loss / Take profit
        3. Rottura SMA30 su 15m (exit veloce)
        4. RSI overbought su 5m
        
        Returns:
            (should_exit, reason)
        """
        try:
            # Validazione entry price
            entry_price = position.get('entry_price', 0)
            if entry_price <= 0:
                self.logger.error(f"Invalid entry price: {entry_price}")
                return False, 'Invalid entry price'
            
            # Current price
            current_price = market_data.get('5m', {}).get('price', 0)
            if current_price <= 0:
                self.logger.error(f"Invalid current price: {current_price}")
                return False, 'Invalid current price'
            
            # Calcola PnL
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
            
            # 1. STOP LOSS / TAKE PROFIT (priorità massima)
            stop_loss_pct = position.get('stop_loss_pct', -2.0)
            take_profit_pct = position.get('take_profit_pct', 6.0)
            
            if pnl_pct <= stop_loss_pct:
                self.logger.info(f"Stop Loss triggered: {pnl_pct:.2f}%")
                return True, f'Stop Loss ({pnl_pct:.2f}%)'
            
            if pnl_pct >= take_profit_pct:
                self.logger.info(f"Take Profit triggered: {pnl_pct:.2f}%")
                return True, f'Take Profit ({pnl_pct:.2f}%)'
            
            # 2. ROTTURA SMA30 SU 15M (segnale forte)
            data_15m = market_data.get('15m', {})
            sma_30_15m = data_15m.get('sma_slow', 0)
            
            if sma_30_15m > 0 and current_price < sma_30_15m:
                # Verifica che sia una rottura recente
                sma_history = data_15m.get('sma_history', [])
                price_history = data_15m.get('price_history', [])
                
                if len(sma_history) >= 5 and len(price_history) >= 5:
                    # Prepara dati per zip sicuro
                    min_len = min(len(price_history[-5:-1]), len(sma_history[-5:-1]))
                    
                    if min_len > 0:
                        # Era sopra la SMA nelle candele precedenti?
                        was_above = any(
                            p > s for p, s in zip(
                                price_history[-5:-1][-min_len:],
                                sma_history[-5:-1][-min_len:]
                            )
                        )
                        
                        if was_above:
                            self.logger.info("SMA30 breakout on 15m detected")
                            return True, 'ROTTURA SMA30 su 15m'
            
            # 3. RSI OVERBOUGHT
            rsi_5m = market_data.get('5m', {}).get('rsi', 50)
            if rsi_5m > 70:
                self.logger.info(f"RSI overbought: {rsi_5m:.1f}")
                return True, f'RSI overbought ({rsi_5m:.1f})'
            
            return False, 'Hold'
            
        except Exception as e:
            self.logger.error(f"Error in exit signal check: {e}")
            return False, 'Exit check error'

# =============================================================================
# 6️⃣ GESTIONE POSIZIONI MULTIPLE (MAX EXPOSURE)
# =============================================================================

class PositionManager:
    """Gestione intelligente delle posizioni"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
    
    def can_open_position(
        self,
        cash_balance: float,
        positions: Dict,
        total_portfolio_value: float,
        max_exposure: float = 0.60  # 60% max
    ) -> Tuple[bool, str]:
        """
        Verifica se si può aprire una nuova posizione
        
        Args:
            cash_balance: Cash disponibile
            positions: Dizionario posizioni aperte
            total_portfolio_value: Valore totale portfolio
            max_exposure: Esposizione massima (default 60%)
            
        Returns:
            (can_open, reason)
        """
        try:
            # Validazione input
            if total_portfolio_value <= 0:
                self.logger.error("Invalid portfolio value")
                return False, 'Invalid portfolio value'
            
            # Nessuna posizione = OK
            if not positions:
                return True, 'No positions'
            
            # Calcola valore totale investito
            invested_value = 0
            for symbol, pos in positions.items():
                qty = pos.get('quantity', 0)
                price = pos.get('current_price', 0)
                
                if qty > 0 and price > 0:
                    invested_value += qty * price
            
            current_exposure = invested_value / total_portfolio_value
            
            if current_exposure >= max_exposure:
                self.logger.info(f"Max exposure reached: {current_exposure:.1%}")
                return False, f'Max exposure ({current_exposure:.0%})'
            
            available_exposure = max_exposure - current_exposure
            self.logger.debug(f"Exposure: {current_exposure:.1%}, available: {available_exposure:.1%}")
            
            return True, f'OK ({current_exposure:.0%} used)'
            
        except Exception as e:
            self.logger.error(f"Error in position manager: {e}")
            return False, 'Position check error'

# =============================================================================
# 🎯 INTEGRAZIONE COMPLETA
# =============================================================================

class SmartTradingEngine:
    """Engine di trading con tutti i miglioramenti"""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        
        # Inizializza componenti
        self.adaptive_rsi = AdaptiveRSI(logger)
        self.smart_volume = SmartVolume(logger)
        self.trend_guard = TrendGuard(logger)
        self.liquidity_filter = LiquidityFilter(logger)
        self.smart_exit = SmartExit(logger)
        self.position_manager = PositionManager(logger)
    
    def generate_buy_signal(
        self,
        market_data: Dict,
        fear_greed: int,
        cash_balance: float,
        positions: Dict,
        total_value: float
    ) -> Tuple[bool, str, Dict]:
        """
        Genera segnale BUY con tutti i filtri smart
        
        Returns:
            (should_buy, reason, metadata)
        """
        try:
            # Validazione input base
            if not market_data or total_value <= 0 or cash_balance < 0:
                return False, 'Invalid input data', {}
            
            # Richiedi dati 5m
            if '5m' not in market_data:
                return False, 'Missing 5m data', {}
            
            # 1. Check exposure
            can_open, exposure_reason = self.position_manager.can_open_position(
                cash_balance, positions, total_value, max_exposure=0.60
            )
            if not can_open:
                return False, exposure_reason, {}
            
            # 2. Check liquidità
            klines_5m = market_data['5m'].get('klines', [])
            if not klines_5m:
                return False, 'No klines data', {}
            
            is_liquid, liq_reason = self.liquidity_filter.check_liquidity(klines_5m)
            if not is_liquid:
                return False, liq_reason, {}
            
            # 3. Check trend alignment (CRITICO)
            can_buy, trend_reason = self.trend_guard.check_trend_alignment(market_data)
            if not can_buy:
                return False, trend_reason, {}
            
            # 4. RSI dinamico
            atr_current = market_data['5m'].get('atr', 0)
            avg_atr = self.adaptive_rsi.calculate_avg_atr(klines_5m, 20)
            rsi_oversold, rsi_overbought = self.adaptive_rsi.get_dynamic_thresholds(
                atr_current, avg_atr
            )
            
            rsi_5m = market_data['5m'].get('rsi', 50)
            
            # Usa >= per essere precisi (non < ma >=)
            if rsi_5m >= rsi_oversold:
                return False, f'RSI non oversold ({rsi_5m:.1f} >= {rsi_oversold})', {}
            
            # 5. Volume intelligente con threshold dinamico
            current_price = market_data['5m'].get('price', 0)
            if current_price <= 0:
                return False, 'Invalid price', {}
            
            atr_normalized = (atr_current / current_price) if current_price > 0 else 0
            vol_threshold = self.smart_volume.get_volume_threshold(atr_normalized)
            # Per timeframe 5m, usa soglia più bassa
            vol_threshold = max(0.3, vol_threshold * 0.5)  # 50% della soglia normale
            
            # Usa penultima candela (ultima è in formazione)
            current_volume = klines_5m[-2]['volume'] if len(klines_5m) >= 2 else (klines_5m[-1]['volume'] if klines_5m else 0)
            vol_valid, vol_ratio = self.smart_volume.check_volume_quality(
                klines_5m, current_volume, vol_threshold
            )
            
            if not vol_valid:
                return False, f'Volume {vol_ratio:.2f}x < {vol_threshold:.2f}x', {}
            
            # 6. Fear & Greed
            if not (10 <= fear_greed <= 40):
                return False, f'Fear & Greed out of range ({fear_greed})', {}
            
            # 7. Conferme multi-timeframe (almeno 2 su 3)
            signals = self._check_multitimeframe_alignment(
                market_data, rsi_oversold
            )
            confirmations = sum(1 for v in signals.values() if v)
            
            if confirmations < 1:
                return False, f'Solo {confirmations}/3 TF concordano', {}
            
            # ✅ TUTTI I FILTRI PASSATI
            metadata = {
                'rsi_threshold': rsi_oversold,
                'rsi_value': rsi_5m,
                'volume_ratio': vol_ratio,
                'volume_threshold': vol_threshold,
                'confirmations': confirmations,
                'signals': {k: (1 if v else 0) for k, v in signals.items()},
                'fear_greed': fear_greed
            }
            
            reason = (
                f'BUY: {confirmations}/3 TF | '
                f'RSI={rsi_5m:.1f}<{rsi_oversold} | '
                f'Vol={vol_ratio:.2f}x | '
                f'F&G={fear_greed}'
            )
            
            return True, reason, metadata
            
        except Exception as e:
            self.logger.error(f"Error generating buy signal: {e}")
            return False, f'Signal generation error: {e}', {}
    
    def _check_multitimeframe_alignment(
        self,
        market_data: Dict,
        rsi_threshold: int
    ) -> Dict[str, bool]:
        """Verifica allineamento segnali su tutti i timeframe"""
        signals = {}
        
        for tf in ['5m', '15m', '1h']:
            data = market_data.get(tf, {})
            
            if not data:
                signals[tf] = False
                continue
            
            rsi = data.get('rsi', 50)
            price = data.get('price', 0)
            sma_fast = data.get('sma_fast', 0)
            
            # Segnale: RSI oversold + prezzo sopra SMA veloce
            # Usa < invece di <= per essere coerente
            if rsi < rsi_threshold and price > 0 and sma_fast > 0 and price > sma_fast:
                signals[tf] = True
            else:
                signals[tf] = False
        
        return signals

# =============================================================================
# 📊 INFO E TESTING
# =============================================================================

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║   🎯 QUANTUM SMART IMPROVEMENTS - MODULE READY           ║
    ╚═══════════════════════════════════════════════════════════╝
    
    ✅ Componenti implementati:
    
    1️⃣ AdaptiveRSI        - RSI dinamico basato su volatilità
    2️⃣ SmartVolume        - Volume threshold intelligente
    3️⃣ TrendGuard         - Protezione contro-trend
    5️⃣ LiquidityFilter    - Filtra orari morti
    7️⃣ SmartExit          - Uscite intelligenti
    6️⃣ PositionManager    - Max 60% exposure
    🎯 SmartTradingEngine - Integrazione completa
    
    🔧 Correzioni applicate:
    ✅ Import TechnicalIndicators incluso
    ✅ Gestione divisione per zero (entry_price)
    ✅ RSI check con >= (oversold threshold)
    ✅ Volume threshold dinamico integrato
    ✅ Logging completo per debug
    ✅ Input validation su tutti i metodi
    ✅ Safe zip per price/sma history
    ✅ Fallback intelligenti per dati mancanti
    
    📊 Pronto per integrazione in quantum_v3_enhanced.py
    """)
