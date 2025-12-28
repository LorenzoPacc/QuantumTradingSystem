#!/bin/bash
set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   QUANTUM V34 - AUTOMATIC INTEGRATION                       ║"
echo "║   Integrating Adaptive Regime Engine into your bot          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

cd ~/trading_project/QuantumTradingSystem

# ═══════════════════════════════════════════════════════════════
# STEP 1: BACKUP
# ═══════════════════════════════════════════════════════════════
echo "📦 Step 1/5: Creating backup..."
BACKUP_FILE="quantum_v33_BACKUP_$(date +%Y%m%d_%H%M%S).py"
cp quantum_v33_ultimate_final.py "$BACKUP_FILE"
echo "✅ Backup created: $BACKUP_FILE"
echo ""

# ═══════════════════════════════════════════════════════════════
# STEP 2: CREATE V34 BASE
# ═══════════════════════════════════════════════════════════════
echo "📄 Step 2/5: Creating V34 integrated version..."
cp quantum_v33_ultimate_final.py quantum_v34_integrated.py
echo "✅ Base file created: quantum_v34_integrated.py"
echo ""

# ═══════════════════════════════════════════════════════════════
# STEP 3: ADD IMPORT
# ═══════════════════════════════════════════════════════════════
echo "🔧 Step 3/5: Adding regime engine import..."

# Add import after other imports (after requests line)
sed -i '/^import requests$/a from adaptive_regime import AdaptiveRiskRegimeEngine' quantum_v34_integrated.py

echo "✅ Import added"
echo ""

# ═══════════════════════════════════════════════════════════════
# STEP 4: RENAME CLASS
# ═══════════════════════════════════════════════════════════════
echo "🔧 Step 4/5: Renaming class to V34..."

sed -i 's/class QuantumTradingV33/class QuantumTradingV34/g' quantum_v34_integrated.py
sed -i 's/Quantum Trading V33/Quantum Trading V34/g' quantum_v34_integrated.py
sed -i 's/quantum_v33/quantum_v34/g' quantum_v34_integrated.py

echo "✅ Class renamed"
echo ""

# ═══════════════════════════════════════════════════════════════
# STEP 5: ADD REGIME ENGINE CODE
# ═══════════════════════════════════════════════════════════════
echo "🔧 Step 5/5: Integrating Adaptive Regime Engine..."

# Create Python script to do the integration
python3 << 'PYINTEGRATE'
import re

# Read the file
with open('quantum_v34_integrated.py', 'r') as f:
    content = f.read()

# ─────────────────────────────────────────────────────────────
# MODIFICATION 1: Add regime engine in __init__
# ─────────────────────────────────────────────────────────────
init_addition = """
        # Adaptive Regime Engine
        self.regime_engine = AdaptiveRiskRegimeEngine()
        self.adaptive_tp_mult = 1.0
        self.adaptive_sl_mult = 1.0
        logger.info("✅ Adaptive Regime Engine initialized")
"""

# Find __init__ and add after self.max_positions
pattern = r"(self\.max_positions\s*=\s*\d+)"
if re.search(pattern, content):
    content = re.sub(pattern, r"\1" + init_addition, content, count=1)
    print("✅ Added regime engine initialization")
else:
    print("⚠️  Could not find max_positions in __init__")

# ─────────────────────────────────────────────────────────────
# MODIFICATION 2: Add helper methods before the run() method
# ─────────────────────────────────────────────────────────────
helper_methods = '''
    def _calculate_win_rate_hours(self, hours):
        """Calculate win rate for specified hours"""
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [t for t in self.trades_history if t.get('timestamp', datetime.now()) > cutoff]
        if not recent:
            return 0
        wins = sum(1 for t in recent if t.get('pnl', 0) > 0)
        return (wins / len(recent)) * 100
    
    def _calculate_rr_ratio(self):
        """Calculate risk/reward ratio from recent trades"""
        recent = self.trades_history[-50:] if len(self.trades_history) > 50 else self.trades_history
        if not recent:
            return 1.0
        wins = [t['pnl'] for t in recent if t.get('pnl', 0) > 0]
        losses = [abs(t['pnl']) for t in recent if t.get('pnl', 0) < 0]
        avg_win = sum(wins) / len(wins) if wins else 0
        avg_loss = sum(losses) / len(losses) if losses else 1
        return avg_win / max(avg_loss, 0.01)
    
    def _close_all_positions_regime(self, reason):
        """Close all positions (for regime hibernation)"""
        logger.warning(f"🐻 Closing all positions: {reason}")
        for symbol in list(self.positions.keys()):
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                self._exit_position(symbol, current_price, reason)
            except Exception as e:
                logger.error(f"Error closing {symbol}: {e}")
'''

# Find the run() method and insert helpers before it
pattern = r"(\n    def run\(self\):)"
if re.search(pattern, content):
    content = re.sub(pattern, helper_methods + r"\1", content, count=1)
    print("✅ Added helper methods")
else:
    print("⚠️  Could not find run() method")

# ─────────────────────────────────────────────────────────────
# MODIFICATION 3: Add regime calculation in main cycle
# ─────────────────────────────────────────────────────────────
regime_block = '''
        # ═══════════════════════════════════════════════════════════
        # ADAPTIVE REGIME ENGINE
        # ═══════════════════════════════════════════════════════════
        try:
            # Calculate metrics for regime engine
            win_rate_24h = self._calculate_win_rate_hours(24)
            win_rate_72h = self._calculate_win_rate_hours(72)
            rr_ratio = self._calculate_rr_ratio()
            current_drawdown = self._calculate_max_drawdown()
            mtf_pass_rate = (self.mtf_passed / max(self.mtf_checks, 1)) * 100
            
            # Get risk profile
            risk_profile = self.regime_engine.calculate_risk_profile(
                fear_greed=fg_value,
                mtf_pass_rate=mtf_pass_rate,
                volatility=0.03,  # Simplified for now
                win_rate_24h=win_rate_24h,
                win_rate_72h=win_rate_72h,
                drawdown=current_drawdown,
                rr_ratio=rr_ratio
            )
            
            # Apply risk profile dynamically
            self.max_positions = risk_profile['max_positions']
            old_tp_mult = self.adaptive_tp_mult
            old_sl_mult = self.adaptive_sl_mult
            self.adaptive_tp_mult = risk_profile['tp_multiplier']
            self.adaptive_sl_mult = risk_profile['sl_multiplier']
            
            # Log regime status
            logger.info(f"💼 RISK PROFILE: {risk_profile['profile_name']}")
            logger.info(f"   Market: {risk_profile['market_regime']} | Health: {risk_profile['strategy_health']}")
            logger.info(f"   Max Positions: {self.max_positions} | TP Mult: {self.adaptive_tp_mult:.2f} | SL Mult: {self.adaptive_sl_mult:.2f}")
            
            # Hibernation mode check
            if risk_profile.get('close_existing', False):
                logger.warning("🐻 HIBERNATION MODE ACTIVATED")
                self._close_all_positions_regime("HIBERNATION")
                logger.info("⏸️  Skipping trade scan - waiting for better conditions")
                time.sleep(120)
                continue  # Skip this cycle
                
        except Exception as e:
            logger.error(f"Regime engine error: {e}")
            # Continue with default settings on error
        
'''

# Find after Fear & Greed calculation and add regime block
# Look for the Fear & Greed logging line
pattern = r'(logger\.info\(f"Fear & Greed: \{fg_value\}.*?\))\n'
if re.search(pattern, content):
    content = re.sub(pattern, r"\1\n" + regime_block, content, count=1)
    print("✅ Added regime calculation in main cycle")
else:
    print("⚠️  Could not find Fear & Greed log line")

# ─────────────────────────────────────────────────────────────
# MODIFICATION 4: Update TP/SL calculations to use multipliers
# ─────────────────────────────────────────────────────────────
# Find TP calculation and add multiplier
content = re.sub(
    r'tp_pct = self\.base_tp_pct',
    r'tp_pct = self.base_tp_pct * self.adaptive_tp_mult',
    content
)

# Find SL calculation and add multiplier
content = re.sub(
    r'sl_pct = self\.base_sl_pct',
    r'sl_pct = self.base_sl_pct * self.adaptive_sl_mult',
    content
)

print("✅ Updated TP/SL calculations with multipliers")

# Write the modified content
with open('quantum_v34_integrated.py', 'w') as f:
    f.write(content)

print("\n✅ Integration complete!")
PYINTEGRATE

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ INTEGRATION COMPLETE!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📋 Files:"
echo "   ✅ $BACKUP_FILE (backup)"
echo "   ✅ adaptive_regime.py (regime engine module)"
echo "   ✅ quantum_v34_integrated.py (integrated bot)"
echo ""
echo "🧪 Quick test:"
echo "   python3 -c \"from quantum_v34_integrated import QuantumTradingV34; print('✅ Import OK')\""
echo ""
echo "🚀 To start the bot:"
echo "   pkill -9 -f quantum_v33  # Stop old version"
echo "   nohup python3 quantum_v34_integrated.py > v34.log 2>&1 &"
echo ""
echo "📊 Monitor:"
echo "   tail -f quantum_v34_adaptive.log"
echo ""
echo "════════════════════════════════════════════════════════════════"
