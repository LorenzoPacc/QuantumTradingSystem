"""
Perpetual Bot V1 - Core Trading Engine
"""
import ccxt
import json
import pandas as pd
import time
from datetime import datetime, date
from datetime import datetime
from signal_generator import SignalGenerator
from risk_manager import RiskManager
from positions_manager import PositionsPersistence
from cost_calculator import CostCalculator
import logging

class PerpetualBot:
    """Main bot class"""
    
    def __init__(self, config_file='perpetual_config.json'):
        # Load config
        with open(config_file) as f:
            self.config = json.load(f)
        
        # Setup detailed logging
        self.logger = logging.getLogger('PerpetualBot')
        self.logger.setLevel(logging.INFO)
        
        # Format like V37
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        self.logger.addHandler(console)
        
        
        # Initialize components
        self.signal_generator = SignalGenerator(config_file)
        self.risk_manager = RiskManager(config_file)
        
        # Initialize exchange (paper trading mode)
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })
        
        # Persistence manager
        self.persistence = PositionsPersistence()
        self.cost_calculator = CostCalculator(is_spot=False)  # Perpetual is FUTURES
        
        # State
        self.positions = self.persistence.load_positions()  # Carica da file!
        self.trades_history = self.persistence.load_trades()
        self.cycle_count = 0
        
        # Recupera capitale dall'ultimo trade
        saved_capital = self.persistence.get_capital_from_trades()
        if saved_capital:
            self.risk_manager.update_capital(saved_capital)
            print(f"   💰 Capital recovered: ${saved_capital:.2f}")
        
        print(f"🤖 {self.config['bot_name']} Initialized")
        print(f"   Mode: {self.config['mode'].upper()}")
        self.logger.info(f"   Capital: ${self.risk_manager.current_capital}")
        print(f"   Assets: {', '.join(self.config['assets'])}")
        print(f"   Leverage: {self.config['leverage']['default']}x")
        
        # Mostra stato recuperato
        if self.positions:
            print(f"   📊 Recovered {len(self.positions)} open position(s)")
        if self.trades_history:
            print(f"   📋 Recovered {len(self.trades_history)} trade(s)")
        
        self.logger.info("")
    
    def fetch_market_data(self, symbol, timeframe='1h', limit=250):
        """Fetch OHLCV data from exchange"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            return df
        except Exception as e:
            print(f"❌ Error fetching data for {symbol}: {e}")
            return None
    
    def check_funding_rate(self, symbol):
        """Check funding rate and decide if it blocks trading"""
        try:
            funding = self.exchange.fetch_funding_rate(symbol)
            rate = funding['fundingRate']
            
            max_pos = self.config['blockers']['funding_rate']['max_positive']
            max_neg = self.config['blockers']['funding_rate']['max_negative']
            
            # Block LONG if funding too high (expensive)
            if rate > max_pos:
                return 'BLOCK_LONG', rate
            
            # Block SHORT if funding too negative (expensive)
            if rate < max_neg:
                return 'BLOCK_SHORT', rate
            
            # Favorable funding (we get paid)
            if rate < 0:
                return 'FAVOR_SHORT', rate
            elif rate > 0:
                return 'FAVOR_LONG', rate
            
            return 'NEUTRAL', rate
            
        except Exception as e:
            print(f"⚠️ Could not fetch funding rate: {e}")
            return 'NEUTRAL', 0
    
    def scan_for_opportunities(self):
        """Scan all assets for trading opportunities"""
        self.logger.info(f"🔍 Scanning {len(self.config['assets'])} assets...")
        
        for symbol in self.config['assets']:
            # Skip if already in position
            if symbol in self.positions:
                continue
            
            # Fetch data
            df = self.fetch_market_data(symbol, self.config['timeframes']['primary'])
            if df is None:
                continue
            
            # Check funding rate
            funding_status, funding_rate = self.check_funding_rate(symbol)
            
            # Generate signal
            can_trade, direction, signal, reason = self.signal_generator.evaluate(df, symbol)
            
            # Log decision
            self.logger.info(f"   {symbol}:")
            self.logger.info(f"      Signal: {direction if can_trade else 'NO_TRADE'}")
            self.logger.info(f"      Reason: {reason}")
            self.logger.info(f"      Funding: {funding_rate:.4%} ({funding_status})")
            

            # COST FILTER - Expected Edge > (Fee + Slippage + Funding) * 2.5
            if can_trade and direction:
                expected_edge = 0.045  # 4.5% target (più alto per coprire funding)
                cost_ok, cost_reason = self.cost_calculator.should_trade_based_on_edge(
                    expected_edge, symbol, funding_rate=funding_rate
                )
                if not cost_ok:
                    self.logger.info(f"      ❌ COST FILTER: {cost_reason}")
                    can_trade = False
                    reason = cost_reason

            # Check funding blocks
            if direction == 'LONG' and funding_status == 'BLOCK_LONG':
                self.logger.info(f"      ❌ BLOCKED: Funding rate too high for LONG")
                continue
            elif direction == 'SHORT' and funding_status == 'BLOCK_SHORT':
                self.logger.info(f"      ❌ BLOCKED: Funding rate too negative for SHORT")
                continue
            
            # Try to open position
            if can_trade:
                signal['symbol'] = symbol
                self.open_position(signal)
    
    def open_position(self, signal):
        """Open a new position (PAPER TRADING)"""
        symbol = signal['symbol']
        
        # Check if can open
        can_open, reason = self.risk_manager.can_open_position()
        if not can_open:
            self.logger.info(f"      ⚠️ Cannot open: {reason}")
            return
        
        # Calculate position size
        quantity, notional, leverage = self.risk_manager.calculate_position_size(signal)
        
        # Calculate stops
        entry_price = signal['entry_price']
        stop_loss, take_profit, trailing = self.risk_manager.calculate_stops(signal, entry_price)
        
        # Check R:R
        if signal['direction'] == 'LONG':
            risk = entry_price - stop_loss
            reward = take_profit - entry_price
        else:
            risk = stop_loss - entry_price
            reward = entry_price - take_profit
        
        rr_ratio = reward / risk if risk > 0 else 0
        min_rr = self.config['risk']['min_risk_reward']
        
        if rr_ratio < min_rr:
            self.logger.info(f"      ❌ R:R too low: {rr_ratio:.2f} < {min_rr}")
            return
        
        # Create position (PAPER)
        position = {
            'symbol': symbol,
            'direction': signal['direction'],
            'entry_price': entry_price,
            'entry_time': datetime.now(),
            'quantity': quantity,
            'notional': notional,
            'leverage': leverage,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'trailing_stop': trailing,
            'rr_ratio': rr_ratio,
            'signal_data': signal
        }
        
        self.positions[symbol] = position
        
        # SALVA SU FILE
        self.persistence.save_positions(self.positions)
        
        self.logger.info(f"      🟢 OPENED {signal['direction']} POSITION")
        self.logger.info(f"         Entry: ${entry_price:.2f}")
        self.logger.info(f"         Size: {quantity:.6f} (${notional:.2f})")
        self.logger.info(f"         Leverage: {leverage}x")
        self.logger.info(f"         SL: ${stop_loss:.2f} (-{self.config['risk']['stop_loss_pct']*100:.1f}%)")
        self.logger.info(f"         TP: ${take_profit:.2f} (+{self.config['risk']['take_profit_pct']*100:.1f}%)")
        self.logger.info(f"         R:R: {rr_ratio:.2f}:1")
    
    def manage_positions(self):
        """Check and manage open positions"""
        if not self.positions:
            return
        
        self.logger.info(f"📊 Managing {len(self.positions)} position(s)...")
        
        for symbol in list(self.positions.keys()):
            position = self.positions[symbol]
            
            # Get current price
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                current_price = ticker['last']
            except:
                continue
            
            # Calculate PnL
            direction = position['direction']
            entry = position['entry_price']
            
            if direction == 'LONG':
                pnl_pct = (current_price - entry) / entry
                pnl_usd = (current_price - entry) * position['quantity']
            else:
                pnl_pct = (entry - current_price) / entry
                pnl_usd = (entry - current_price) * position['quantity']
            
            self.logger.info(f"   {symbol} {direction}:")
            self.logger.info(f"      Entry: ${entry:.2f} → Current: ${current_price:.2f}")
            self.logger.info(f"      PnL: {pnl_pct*100:+.2f}% (${pnl_usd:+.2f})")
            
            # Check stop loss
            if direction == 'LONG':
                if current_price <= position['stop_loss']:
                    self.close_position(symbol, current_price, 'STOP_LOSS')
                    continue
            else:
                if current_price >= position['stop_loss']:
                    self.close_position(symbol, current_price, 'STOP_LOSS')
                    continue
            
            # Check take profit
            if direction == 'LONG':
                if current_price >= position['take_profit']:
                    self.close_position(symbol, current_price, 'TAKE_PROFIT')
                    continue
            else:
                if current_price <= position['take_profit']:
                    self.close_position(symbol, current_price, 'TAKE_PROFIT')
                    continue
            
            # Update trailing stop
            trailing = position['trailing_stop']
            if not trailing['active']:
                # Check activation
                if direction == 'LONG':
                    if current_price >= trailing['activation_price']:
                        trailing['active'] = True
                        trailing['current_stop'] = current_price * (1 - trailing['trail_distance_pct'])
                        self.logger.info(f"      ✅ Trailing stop ACTIVATED at ${trailing['current_stop']:.2f}")
                else:
                    if current_price <= trailing['activation_price']:
                        trailing['active'] = True
                        trailing['current_stop'] = current_price * (1 + trailing['trail_distance_pct'])
                        self.logger.info(f"      ✅ Trailing stop ACTIVATED at ${trailing['current_stop']:.2f}")
            else:
                # Update trailing stop
                if direction == 'LONG':
                    new_stop = current_price * (1 - trailing['trail_distance_pct'])
                    if new_stop > trailing['current_stop']:
                        trailing['current_stop'] = new_stop
                        self.logger.info(f"      📈 Trailing stop moved to ${new_stop:.2f}")
                    
                    # Check if hit
                    if current_price <= trailing['current_stop']:
                        self.close_position(symbol, current_price, 'TRAILING_STOP')
                        continue
                else:
                    new_stop = current_price * (1 + trailing['trail_distance_pct'])
                    if new_stop < trailing['current_stop']:
                        trailing['current_stop'] = new_stop
                        self.logger.info(f"      📉 Trailing stop moved to ${new_stop:.2f}")
                    
                    # Check if hit
                    if current_price >= trailing['current_stop']:
                        self.close_position(symbol, current_price, 'TRAILING_STOP')
                        continue
    
    def close_position(self, symbol, exit_price, reason):
        """Close position and record trade"""
        position = self.positions[symbol]
        
        direction = position['direction']
        entry = position['entry_price']
        
        if direction == 'LONG':
            pnl_pct = (exit_price - entry) / entry
            pnl_usd = (exit_price - entry) * position['quantity']
        else:
            pnl_pct = (entry - exit_price) / entry
            pnl_usd = (entry - exit_price) * position['quantity']
        
        # Update capital
        self.risk_manager.update_capital(self.risk_manager.current_capital + pnl_usd)
        
        # Record trade
        is_win = pnl_usd > 0
        self.risk_manager.record_trade(pnl_usd, is_win)
        
        trade = {
            'symbol': symbol,
            'direction': direction,
            'entry_price': entry,
            'exit_price': exit_price,
            'entry_time': position['entry_time'].isoformat(),
            'exit_time': datetime.now().isoformat(),
            'quantity': position['quantity'],
            'pnl_usd': pnl_usd,
            'pnl_pct': pnl_pct,
            'exit_reason': reason
        }
        
        # Aggiungi capitale finale al trade
        trade['final_capital'] = self.risk_manager.current_capital
        
        self.trades_history.append(trade)
        
        # SALVA TRADE SU FILE (con check duplicati)
        # Verifica che non sia già salvato
        existing_trades = self.persistence.load_trades()
        is_duplicate = any(
            t.get('entry_time') == trade['entry_time'] and 
            t.get('exit_time') == trade['exit_time']
            for t in existing_trades
        )
        
        if not is_duplicate:
            self.persistence.save_trade(trade)
        else:
            self.logger.info(f"      ⚠️ Duplicate trade detected, not saving")
        
        self.logger.info(f"      🔴 CLOSED {direction} ({reason})")
        self.logger.info(f"         Exit: ${exit_price:.2f}")
        print(f"         PnL: {pnl_pct*100:+.2f}% (${pnl_usd:+.2f})")
        self.logger.info(f"         New Capital: ${self.risk_manager.current_capital:.2f}")
        
        del self.positions[symbol]
        
        # AGGIORNA FILE POSITIONS (rimuovi posizione chiusa)
        self.persistence.save_positions(self.positions)
    
    def run_cycle(self):
        # Reset trades_today se è un nuovo giorno
        today = date.today()
        if not hasattr(self, 'last_reset_date'):
            self.last_reset_date = today
        elif self.last_reset_date != today:
            self.risk_manager.reset_daily_stats()
            self.last_reset_date = today
            self.logger.info("📅 Daily reset: trades_today=0, daily_pnl=0")
        
        """Run one trading cycle"""
        self.cycle_count += 1
        
        self.logger.info("=" * 80)
        self.logger.info(f"🔄 CYCLE {self.cycle_count} - {datetime.now()}")
        self.logger.info("=" * 80)
        
        # Manage existing positions first
        self.manage_positions()
        
        # Scan for new opportunities if no position
        if len(self.positions) < self.config['position']['max_concurrent']:
            self.scan_for_opportunities()
        
        # Portfolio status
        self.logger.info("")
        self.logger.info("💼 PORTFOLIO STATUS")
        self.logger.info(f"   Capital: ${self.risk_manager.current_capital:.2f}")
        self.logger.info(f"   Positions: {len(self.positions)}")
        self.logger.info(f"   Daily PnL: ${self.risk_manager.daily_pnl:+.2f}")
        self.logger.info(f"   Trades Today: {self.risk_manager.daily_trades}")
        self.logger.info(f"   Total Trades: {len(self.trades_history)}")
        self.logger.info("")

if __name__ == "__main__":
    # Quick test
    bot = PerpetualBot()
    bot.run_cycle()
