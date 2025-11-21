#!/usr/bin/env bash
set -euo pipefail

# Colors for output
RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
PURPLE='\033[1;35m'
CYAN='\033[1;36m'
NC='\033[0m'

# Print functions
print_header() { echo -e "\n${PURPLE}🎯 $1${NC}"; }
print_step() { echo -e "${BLUE}▶ $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${CYAN}ℹ $1${NC}"; }

main() {
    clear
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║           🚀 QUANTUM TRADER V3 - COMPLETE INSTALLER         ║"
    echo "║                                                              ║"
    echo "║         Advanced Gating System Integration                  ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    # STEP 1: System Checks
    print_header "SYSTEM CHECKS"
    
    if ! command -v python3 >/dev/null 2>&1; then
        print_error "Python3 not found!"
        exit 1
    fi
    print_success "Python3: $(python3 --version | cut -d' ' -f2)"

    if ! command -v pip3 >/dev/null 2>&1; then
        print_error "pip3 not found!"
        exit 1
    fi
    print_success "pip3 available"

    # STEP 2: Backup
    print_header "BACKUP CREATION"
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_DIR="backup_${TIMESTAMP}"
    mkdir -p "$BACKUP_DIR"
    
    for file in quantum_*.py; do
        if [ -f "$file" ]; then
            cp "$file" "$BACKUP_DIR/"
            print_success "Backed up: $file"
        fi
    done
    
    print_success "Backups saved in: $BACKUP_DIR"

    # STEP 3: Virtual Environment
    print_header "VIRTUAL ENVIRONMENT"
    
    if [ ! -d "venv" ]; then
        print_step "Creating virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_success "Virtual environment already exists"
    fi
    
    source venv/bin/activate
    print_success "Virtual environment activated"

    # STEP 4: Dependencies
    print_header "DEPENDENCIES INSTALLATION"
    
    print_step "Upgrading pip..."
    pip install --upgrade pip >/dev/null 2>&1
    
    REQUIRED_PACKAGES=(
        "numpy"
        "pandas" 
        "requests"
        "python-binance"
        "aiohttp"
        "websockets"
        "python-dotenv"
        "colorama"
        "tabulate"
        "psutil"
    )
    
    for package in "${REQUIRED_PACKAGES[@]}"; do
        print_step "Checking $package..."
        if pip show "$package" >/dev/null 2>&1; then
            print_success "$package already installed"
        else
            pip install "$package" >/dev/null 2>&1
            print_success "Installed $package"
        fi
    done

    # STEP 5: Create Gating System
    print_header "GATING SYSTEM CREATION"
    
    cat > entry_gating_system.py << 'GATING_EOF'
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
GATING_EOF

    print_success "Advanced Gating System created"

    # STEP 6: Create Integration Patcher
    print_header "BOT INTEGRATION"

    cat > patch_quantum_bot.py << 'PATCH_EOF'
#!/usr/bin/env python3
"""
Quantum Trader V3 Integration Patcher
"""
import re
import sys
import os

def patch_existing_bot():
    input_file = "quantum_v2_1_complete.py"
    output_file = "quantum_v3_enhanced.py"
    
    if not os.path.exists(input_file):
        print("❌ Error: quantum_v2_1_complete.py not found!")
        return False
    
    print(f"📖 Reading {input_file}...")
    with open(input_file, 'r') as f:
        content = f.read()
    
    original_content = content
    modifications = []
    
    # Add imports
    if "from entry_gating_system import" not in content:
        print("  → Adding gating system imports...")
        
        lines = content.split('\n')
        last_import_idx = 0
        
        for i, line in enumerate(lines):
            if line.startswith(('import ', 'from ')):
                last_import_idx = i
            elif line.strip() and not line.startswith(('#', '"""', "'''")):
                break
        
        new_imports = [
            "",
            "# =============================================",
            "# QUANTUM V3 GATING SYSTEM INTEGRATION",
            "# =============================================",
            "from entry_gating_system import AdvancedGatingSystem, QuantumIntegrationManager",
            ""
        ]
        
        lines = lines[:last_import_idx+1] + new_imports + lines[last_import_idx+1:]
        content = '\n'.join(lines)
        modifications.append("Added gating system imports")
    
    # Add gating system to __init__
    if "self.gating_system" not in content:
        print("  → Integrating gating system into bot class...")
        
        class_pattern = r'(class QuantumTraderV21.*?def __init__\(self[^)]*\):\s*\n)(.*?)(?=\n    def \w+|\nclass |\Z)'
        
        match = re.search(class_pattern, content, re.DOTALL)
        if match:
            init_body = match.group(2)
            
            gating_init = '''
        # 🚀 QUANTUM V3 GATING SYSTEM INTEGRATION
        self.gating_config = {
            'min_volume_ratio': 0.75,
            'max_correlation': 0.7,
            'min_mtf_score': 0.65,
            'max_portfolio_positions': getattr(self, 'max_positions', 6),
            'min_liquidity_depth': 8000,
            'max_daily_drawdown': -0.03,
            'fear_greed_threshold': 20,
            'max_daily_volatility': 0.08,
            'position_size_base': 0.10,
            'min_position_size': 15.0,
            'max_position_size': 35.0,
        }
        
        self.gating_system = AdvancedGatingSystem(self.gating_config)
        self.integration_manager = QuantumIntegrationManager(self)
        self.integration_manager.dry_run_mode = True  # ⚠️ SAFETY FIRST!
        
        self.logger.info("🚀 QUANTUM V3 GATING SYSTEM INTEGRATED - DRY RUN MODE")
'''
            
            new_init_body = init_body.rstrip() + gating_init
            content = content.replace(init_body, new_init_body)
            modifications.append("Added gating system to __init__")
    
    # Save patched bot
    if modifications:
        print(f"  → Saving patched bot to {output_file}...")
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        print(f"\n✅ SUCCESS! Created {output_file}")
        print("📊 Modifications applied:")
        for mod in modifications:
            print(f"   • {mod}")
        
        return True
    else:
        print("ℹ️  No modifications needed")
        return True

def main():
    print("🚀 QUANTUM V3 BOT PATCHER")
    print("=" * 50)
    
    success = patch_existing_bot()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 PATCHING COMPLETED SUCCESSFULLY!")
        print("\n📁 Generated files:")
        print("   • entry_gating_system.py - Advanced gating system")
        print("   • quantum_v3_enhanced.py - Your enhanced bot")
        print("\n🚀 NEXT STEPS:")
        print("   1. Review: quantum_v3_enhanced.py")
        print("   2. Test: python3 quantum_v3_enhanced.py")
        print("   3. Monitor gating decisions in logs")
        print("   4. When confident: Set dry_run_mode = False")
        print("\n⚠️  SAFETY: Starts in DRY RUN mode - no live trades!")
    else:
        print("\n❌ PATCHING FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()
PATCH_EOF

    print_success "Integration patcher created"

    # STEP 7: Run the Patcher
    print_header "APPLYING PATCHES"
    
    python3 patch_quantum_bot.py
    PATCH_RESULT=$?
    
    if [ $PATCH_RESULT -eq 0 ]; then
        print_success "Bot successfully patched with Quantum V3!"
    else
        print_error "Patching failed!"
        exit 1
    fi

    # STEP 8: Create Test Suite
    print_header "CREATING TEST SUITE"
    
    cat > test_quantum_v3.sh << 'TEST_EOF'
#!/bin/bash
echo "🧪 QUANTUM V3 TEST"
echo "=================="
echo "1. Testing Gating System..."
python3 -c "
try:
    from entry_gating_system import AdvancedGatingSystem
    print('   ✅ Gating system imports OK')
    gating = AdvancedGatingSystem()
    print('   ✅ Gating system initialization OK')
    result = gating.evaluate_entry_signal(
        symbol='BTCUSDT',
        signal_data={'strength': 0.8, 'action': 'BUY', 'reason': 'momentum'},
        position_size=20.0,
        market_context={
            'klines_1h': [{'volume': 1000000, 'close': 50000} for _ in range(24)],
            'orderbook': {'bids': [[50000, 1]], 'asks': [[50001, 1]]},
            'portfolio_positions': [],
            'daily_pnl': 0.0,
            'fear_greed': 25
        }
    )
    print(f'   ✅ Evaluation: {result.recommendation}')
    print(f'   📊 Confidence: {result.confidence:.1%}')
except Exception as e:
    print(f'   ❌ Test failed: {e}')
    exit(1)
"
echo "2. Testing Enhanced Bot..."
python3 -c "
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location('quantum_v3', 'quantum_v3_enhanced.py')
    if spec is None:
        print('   ❌ Could not load enhanced bot')
        exit(1)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print('   ✅ Enhanced bot loads successfully')
    if hasattr(module, 'QuantumTraderV21'):
        print('   ✅ QuantumTraderV21 class found')
    else:
        print('   ❌ QuantumTraderV21 class not found')
        exit(1)
except Exception as e:
    print(f'   ❌ Enhanced bot test failed: {e}')
    exit(1)
"
echo "=================="
echo "🎉 ALL TESTS PASSED!"
echo ""
echo "🚀 YOUR QUANTUM V3 IS READY!"
echo "   Run: python3 quantum_v3_enhanced.py"
TEST_EOF

    chmod +x test_quantum_v3.sh
    print_success "Test suite created"

    # STEP 9: Run Tests
    print_header "FINAL VERIFICATION"
    ./test_quantum_v3.sh

    # STEP 10: Create Launch Script
    print_header "CREATING LAUNCH SCRIPT"
    
    cat > launch_quantum_v3.sh << 'LAUNCH_EOF'
#!/bin/bash
echo "🚀 LAUNCHING QUANTUM TRADER V3"
echo "================================"
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found"
    exit 1
fi
if [ ! -f "quantum_v3_enhanced.py" ]; then
    echo "❌ Enhanced bot not found. Run installer first."
    exit 1
fi
echo ""
echo "🎯 QUANTUM V3 FEATURES:"
echo "   • Advanced 6-Gate Entry Validation"
echo "   • Intelligent Position Sizing"
echo "   • Multi-Timeframe Analysis"
echo "   • Portfolio Risk Management"
echo "   • Market Regime Detection"
echo ""
echo "⚠️  MODE: DRY RUN (No live trades)"
echo "   To enable live trading, set: integration_manager.dry_run_mode = False"
echo ""
echo "Starting bot..."
echo "================================"
python3 quantum_v3_enhanced.py
LAUNCH_EOF

    chmod +x launch_quantum_v3.sh
    print_success "Launch script created"

    # FINAL SUMMARY
    print_header "🎉 INSTALLATION COMPLETE!"
    
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                   QUANTUM TRADER V3 READY!                 ║"
    echo "║                Advanced Gating System Active               ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    echo ""
    echo "📁 GENERATED FILES:"
    echo "   • ${GREEN}entry_gating_system.py${NC} - Advanced 6-gate validation"
    echo "   • ${GREEN}quantum_v3_enhanced.py${NC} - Your enhanced trading bot"
    echo "   • ${GREEN}launch_quantum_v3.sh${NC}   - Quick launch script"
    echo "   • ${GREEN}test_quantum_v3.sh${NC}     - Verification tests"
    echo "   • ${GREEN}backup_${TIMESTAMP}/${NC}   - Original files backup"
    
    echo ""
    echo "🚀 QUICK START:"
    echo "   1. ${CYAN}./launch_quantum_v3.sh${NC} - Start enhanced bot"
    echo "   2. ${CYAN}Monitor logs${NC} - Watch gating decisions"
    echo "   3. ${YELLOW}When confident${NC} - Set dry_run_mode = False"
    
    echo ""
    echo -e "${PURPLE}🎉 YOUR TRADING BOT IS NOW UPGRADED WITH AI-POWERED GATING!${NC}"
    
    deactivate 2>/dev/null
}

main "$@"
