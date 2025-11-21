"""
QUANTUM GATING SYSTEM V3 - Advanced Entry Validation
"""
import numpy as np
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger("QuantumGating")

@dataclass
class GatingResult:
    approved: bool
    adjusted_size: float
    confidence: float
    gates_passed: List[str]
    gates_failed: List[str]
    recommendation: str
    details: Dict[str, Any]
    timestamp: str

class AdvancedGatingSystem:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logger
        self.min_volume_ratio = self.config.get('min_volume_ratio', 0.75)
        self.max_correlation = self.config.get('max_correlation', 0.7)
        self.min_mtf_score = self.config.get('min_mtf_score', 0.65)
        self.min_liquidity = self.config.get('min_liquidity_depth', 8000)
        self.max_daily_dd = self.config.get('max_daily_drawdown', -0.03)
        self.fear_greed_threshold = self.config.get('fear_greed_threshold', 20)
        self.max_volatility = self.config.get('max_daily_volatility', 0.08)
        self.logger.info("🚀 Advanced Gating System Initialized")

    def evaluate_entry_signal(self, symbol: str, signal_data: Dict, position_size: float, market_context: Dict) -> GatingResult:
        gates_passed = []
        gates_failed = []
        details = {}
        
        # Gate 1: Volume Validation
        volume_ok, volume_details = self._check_volume_advanced(symbol, market_context)
        if volume_ok: gates_passed.append('volume') 
        else: gates_failed.append('volume')
        details['volume'] = volume_details
        
        # Gate 2: Liquidity & Slippage
        liquidity_ok, liquidity_details = self._check_liquidity_advanced(symbol, position_size, market_context)
        if liquidity_ok: gates_passed.append('liquidity')
        else: gates_failed.append('liquidity')
        details['liquidity'] = liquidity_details
        
        # Gate 3: Portfolio Risk Management
        risk_ok, risk_details = self._check_portfolio_risk_advanced(market_context)
        if risk_ok: gates_passed.append('portfolio_risk')
        else: gates_failed.append('portfolio_risk')
        details['portfolio_risk'] = risk_details
        
        # Gate 4: Market Regime Analysis
        regime_ok, regime_details = self._check_market_regime_advanced(market_context)
        if regime_ok: gates_passed.append('market_regime')
        else: gates_failed.append('market_regime')
        details['market_regime'] = regime_details
        
        # Gate 5: Signal Quality & Strength
        signal_ok, signal_details = self._check_signal_quality_advanced(signal_data, market_context)
        if signal_ok: gates_passed.append('signal_quality')
        else: gates_failed.append('signal_quality')
        details['signal_quality'] = signal_details
        
        # Gate 6: Volatility Assessment
        volatility_ok, volatility_details = self._check_volatility_advanced(symbol, market_context)
        if volatility_ok: gates_passed.append('volatility')
        else: gates_failed.append('volatility')
        details['volatility'] = volatility_details
        
        total_gates = 6
        passed_count = len(gates_passed)
        confidence = passed_count / total_gates
        
        critical_gates = ['volume', 'liquidity', 'portfolio_risk']
        critical_passed = all(gate in gates_passed for gate in critical_gates)
        
        approved = critical_passed and confidence >= self.min_mtf_score
        
        if approved:
            vol_multiplier = 1.0 - (volatility_details.get('volatility', 0) * 2)
            vol_multiplier = max(0.5, min(1.2, vol_multiplier))
            strength_multiplier = signal_details.get('strength_score', 0.5) * 1.5
            adjusted_size = position_size * confidence * vol_multiplier * strength_multiplier
            recommendation = f"✅ APPROVED ({passed_count}/{total_gates} gates)"
        else:
            adjusted_size = 0.0
            recommendation = f"⛔ REJECTED ({passed_count}/{total_gates} gates)"
        
        return GatingResult(
            approved=approved,
            adjusted_size=adjusted_size,
            confidence=confidence,
            gates_passed=gates_passed,
            gates_failed=gates_failed,
            recommendation=recommendation,
            details=details,
            timestamp=datetime.now().isoformat()
        )

    def _check_volume_advanced(self, symbol: str, context: Dict) -> Tuple[bool, Dict]:
        try:
            klines_1h = context.get('klines_1h', [])
            if not klines_1h or len(klines_1h) < 24:
                return False, {"reason": "insufficient_data", "score": 0.0}
            
            recent_volume = sum(k.get('volume', 0) for k in klines_1h[-6:]) / 6
            avg_volume_24h = sum(k.get('volume', 0) for k in klines_1h[-24:]) / 24
            
            if avg_volume_24h == 0:
                return False, {"reason": "zero_volume", "score": 0.0}
            
            volume_ratio = recent_volume / avg_volume_24h
            passed = volume_ratio >= self.min_volume_ratio
            volume_score = min(1.0, volume_ratio / 2.0)
            
            return passed, {
                "volume_ratio": volume_ratio,
                "recent_volume": recent_volume,
                "avg_volume_24h": avg_volume_24h,
                "threshold": self.min_volume_ratio,
                "score": volume_score,
                "reason": "sufficient_volume" if passed else "low_volume"
            }
        except Exception as e:
            self.logger.error(f"Volume check error: {e}")
            return False, {"reason": "error", "error": str(e), "score": 0.0}

    def _check_liquidity_advanced(self, symbol: str, position_size: float, context: Dict) -> Tuple[bool, Dict]:
        try:
            orderbook = context.get('orderbook', {})
            bids = orderbook.get('bids', [])
            asks = orderbook.get('asks', [])
            
            if not bids or not asks:
                return True, {"reason": "no_data", "score": 0.5}
            
            depth_levels = [5, 10, 20]
            liquidity_at_depth = {}
            
            for depth in depth_levels:
                bid_liquidity = sum(float(b[1]) * float(b[0]) for b in bids[:depth])
                ask_liquidity = sum(float(a[1]) * float(a[0]) for a in asks[:depth])
                liquidity_at_depth[depth] = (bid_liquidity + ask_liquidity) / 2
            
            estimated_slippage = self._estimate_slippage(position_size, orderbook)
            required_liquidity = position_size * 3
            top_liquidity = liquidity_at_depth.get(5, 0)
            
            passed = top_liquidity >= required_liquidity and estimated_slippage < 0.002
            liquidity_score = min(1.0, top_liquidity / (required_liquidity * 2))
            
            return passed, {
                "liquidity_at_5_levels": top_liquidity,
                "required_liquidity": required_liquidity,
                "estimated_slippage": estimated_slippage,
                "liquidity_at_depths": liquidity_at_depth,
                "score": liquidity_score,
                "reason": "sufficient_liquidity" if passed else "low_liquidity"
            }
        except Exception as e:
            self.logger.error(f"Liquidity check error: {e}")
            return True, {"reason": "check_failed", "score": 0.5}

    def _estimate_slippage(self, position_size: float, orderbook: Dict) -> float:
        try:
            asks = orderbook.get('asks', [])
            if not asks:
                return 0.001
            
            cumulative_volume = 0
            cumulative_value = 0
            target_volume = position_size / float(asks[0][0]) if asks else 0
            
            for price, volume in asks:
                price_float = float(price)
                volume_float = float(volume)
                
                if cumulative_volume >= target_volume:
                    break
                    
                fill_volume = min(volume_float, target_volume - cumulative_volume)
                cumulative_value += fill_volume * price_float
                cumulative_volume += fill_volume
            
            if cumulative_volume == 0:
                return 0.001
                
            avg_price = cumulative_value / cumulative_volume
            first_price = float(asks[0][0])
            slippage = (avg_price - first_price) / first_price
            
            return max(0.0, slippage)
        except:
            return 0.001

    def _check_portfolio_risk_advanced(self, context: Dict) -> Tuple[bool, Dict]:
        try:
            positions = context.get('portfolio_positions', [])
            max_positions = self.config.get('max_portfolio_positions', 6)
            
            if len(positions) >= max_positions:
                return False, {
                    "reason": "max_positions",
                    "current": len(positions),
                    "max": max_positions,
                    "score": 0.0
                }
            
            daily_pnl = context.get('daily_pnl', 0.0)
            if daily_pnl < self.max_daily_dd:
                return False, {
                    "reason": "daily_drawdown",
                    "daily_pnl": daily_pnl,
                    "max_drawdown": self.max_daily_dd,
                    "score": 0.0
                }
            
            correlation_risk = context.get('portfolio_correlation', 0.0)
            if correlation_risk > self.max_correlation:
                return False, {
                    "reason": "high_correlation",
                    "correlation": correlation_risk,
                    "max_correlation": self.max_correlation,
                    "score": 0.0
                }
            
            position_score = 1.0 - (len(positions) / max_positions)
            pnl_score = 1.0 if daily_pnl >= 0 else max(0.0, 1.0 + (daily_pnl / self.max_daily_dd))
            correlation_score = 1.0 - (correlation_risk / self.max_correlation)
            overall_score = (position_score + pnl_score + correlation_score) / 3
            
            return True, {
                "reason": "acceptable_risk",
                "position_count": len(positions),
                "daily_pnl": daily_pnl,
                "correlation": correlation_risk,
                "score": overall_score
            }
            
        except Exception as e:
            self.logger.error(f"Portfolio risk check error: {e}")
            return True, {"reason": "check_failed", "score": 0.5}

    def _check_market_regime_advanced(self, context: Dict) -> Tuple[bool, Dict]:
        try:
            fear_greed = context.get('fear_greed', 50)
            volatility = context.get('market_volatility', 0.05)
            
            if fear_greed < 25:
                regime = "EXTREME_FEAR"
                sentiment_score = 0.8
            elif fear_greed < 45:
                regime = "FEAR"
                sentiment_score = 0.6
            elif fear_greed < 55:
                regime = "NEUTRAL"
                sentiment_score = 0.5
            elif fear_greed < 75:
                regime = "GREED"
                sentiment_score = 0.4
            else:
                regime = "EXTREME_GREED"
                sentiment_score = 0.2
            
            if volatility > self.max_volatility:
                regime += "_HIGH_VOL"
                sentiment_score *= 0.7
            
            if fear_greed < self.fear_greed_threshold:
                passed = True
                reason = "favorable_sentiment"
            elif fear_greed > 80 and volatility > 0.06:
                passed = False
                reason = "dangerous_regime"
            else:
                passed = True
                reason = "neutral_regime"
            
            return passed, {
                "regime": regime,
                "fear_greed": fear_greed,
                "volatility": volatility,
                "sentiment_score": sentiment_score,
                "reason": reason
            }
            
        except Exception as e:
            self.logger.error(f"Market regime check error: {e}")
            return True, {"reason": "check_failed", "score": 0.5}

    def _check_signal_quality_advanced(self, signal_data: Dict, context: Dict) -> Tuple[bool, Dict]:
        try:
            strength = signal_data.get('strength', 0.5)
            reason = signal_data.get('reason', '')
            
            min_strength = 0.4
            strength_passed = strength >= min_strength
            
            reason_score = 0.5
            if 'fear' in reason.lower() and context.get('fear_greed', 50) < 30:
                reason_score = 0.8
            elif 'momentum' in reason.lower():
                reason_score = 0.7
            elif 'breakout' in reason.lower():
                reason_score = 0.6
            
            mtf_score = context.get('multi_timeframe_score', 0.5)
            signal_score = (strength + reason_score + mtf_score) / 3
            passed = strength_passed and signal_score >= 0.5
            
            return passed, {
                "strength": strength,
                "reason_score": reason_score,
                "mtf_score": mtf_score,
                "signal_score": signal_score,
                "threshold": min_strength,
                "reason": "strong_signal" if passed else "weak_signal"
            }
            
        except Exception as e:
            self.logger.error(f"Signal quality check error: {e}")
            return True, {"reason": "check_failed", "score": 0.5}

    def _check_volatility_advanced(self, symbol: str, context: Dict) -> Tuple[bool, Dict]:
        try:
            klines_1h = context.get('klines_1h', [])
            
            if not klines_1h or len(klines_1h) < 24:
                return True, {"volatility": 0.05, "score": 0.5, "reason": "insufficient_data"}
            
            closes = [k.get('close', 0) for k in klines_1h if k.get('close', 0) > 0]
            
            if len(closes) < 10:
                return True, {"volatility": 0.05, "score": 0.5, "reason": "insufficient_data"}
            
            returns = []
            for i in range(1, len(closes)):
                ret = (closes[i] - closes[i-1]) / closes[i-1]
                returns.append(ret)
            
            volatility = np.std(returns) if returns else 0.05
            annualized_vol = volatility * np.sqrt(365 * 24)
            
            passed = volatility <= self.max_volatility
            vol_score = max(0.1, 1.0 - (volatility / (self.max_volatility * 2)))
            
            return passed, {
                "volatility": volatility,
                "annualized_vol": annualized_vol,
                "threshold": self.max_volatility,
                "score": vol_score,
                "reason": "acceptable_volatility" if passed else "high_volatility"
            }
            
        except Exception as e:
            self.logger.error(f"Volatility check error: {e}")
            return True, {"volatility": 0.05, "score": 0.5, "reason": "check_failed"}

class QuantumIntegrationManager:
    def __init__(self, bot):
        self.bot = bot
        self.dry_run_mode = True
        self.gating_system = AdvancedGatingSystem(getattr(bot, 'gating_config', {}))
        self.logger = logger
        self.logger.info("🚀 Quantum Integration Manager Initialized")

    async def evaluate_and_execute(self, symbol: str, original_signal: Dict) -> bool:
        try:
            market_context = await self._gather_comprehensive_context(symbol)
            position_size = self._calculate_intelligent_size(symbol, original_signal)
            
            result = self.gating_system.evaluate_entry_signal(
                symbol=symbol,
                signal_data=original_signal,
                position_size=position_size,
                market_context=market_context
            )
            
            self._log_comprehensive_result(symbol, result)
            
            if result.approved:
                return await self._handle_approved_trade(symbol, result)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Evaluation pipeline error for {symbol}: {e}")
            return False

    async def _gather_comprehensive_context(self, symbol: str) -> Dict:
        context = {
            'portfolio_positions': list(getattr(self.bot, 'positions', {}).keys()),
            'daily_pnl': getattr(self.bot, 'daily_pnl', 0.0),
            'fear_greed': getattr(self.bot, 'fear_greed_index', 50),
            'portfolio_correlation': 0.0,
            'market_volatility': 0.05,
            'multi_timeframe_score': 0.6,
        }
        
        for timeframe in ['1h', '4h']:
            try:
                if hasattr(self.bot, 'get_klines'):
                    klines = await self.bot.get_klines(symbol, timeframe, 100)
                    context[f'klines_{timeframe}'] = klines
            except Exception as e:
                self.logger.warning(f"Could not get {timeframe} klines for {symbol}: {e}")
                context[f'klines_{timeframe}'] = []
        
        try:
            if hasattr(self.bot, 'get_orderbook'):
                orderbook = await self.bot.get_orderbook(symbol, 20)
                context['orderbook'] = orderbook
        except Exception as e:
            self.logger.warning(f"Could not get orderbook for {symbol}: {e}")
            context['orderbook'] = {}
        
        return context

    def _calculate_intelligent_size(self, symbol: str, signal: Dict) -> float:
        base_size = getattr(self.bot, 'position_size_base', 0.10)
        capital = getattr(self.bot, 'capital', 200.0)
        min_size = getattr(self.bot, 'min_position_size', 15.0)
        max_size = getattr(self.bot, 'max_position_size', 35.0)
        
        size = capital * base_size
        strength = signal.get('strength', 0.5)
        size *= (0.5 + strength)
        size = max(min_size, min(size, max_size))
        
        return size

    async def _handle_approved_trade(self, symbol: str, result: GatingResult) -> bool:
        if self.dry_run_mode:
            self.logger.info(
                f"🧪 [DRY-RUN] Approved: {symbol} | "
                f"Size: ${result.adjusted_size:.2f} | "
                f"Confidence: {result.confidence:.1%} | "
                f"Gates: {len(result.gates_passed)}/6"
            )
            return True
        else:
            self.logger.info(
                f"🚀 [LIVE] Executing: {symbol} | "
                f"Size: ${result.adjusted_size:.2f}"
            )
            
            if hasattr(self.bot, 'execute_buy'):
                success = await self.bot.execute_buy(symbol, result.adjusted_size)
                if success:
                    self.logger.info(f"✅ Live execution successful: {symbol}")
                return success
            else:
                self.logger.error("❌ Bot missing execute_buy method!")
                return False

    def _log_comprehensive_result(self, symbol: str, result: GatingResult):
        if result.approved:
            self.logger.info(
                f"🎯 {symbol} {result.recommendation} | "
                f"Confidence: {result.confidence:.1%} | "
                f"Size: ${result.adjusted_size:.2f} | "
                f"Gates: {len(result.gates_passed)}/6 passed"
            )
            
            if result.gates_passed:
                self.logger.debug(f"   ✅ Passed: {', '.join(result.gates_passed)}")
        else:
            self.logger.info(
                f"⛔ {symbol} {result.recommendation} | "
                f"Confidence: {result.confidence:.1%}"
            )
            
            if result.gates_failed:
                self.logger.debug(f"   ❌ Failed: {', '.join(result.gates_failed)}")

__all__ = ['AdvancedGatingSystem', 'QuantumIntegrationManager', 'GatingResult']
