#!/usr/bin/env python3
"""
AUTONOMOUS TRADING BOT - V36 TELEGRAM EDITION
Integrazione completa con notifiche Telegram
"""

import time
import logging
from datetime import datetime
import ccxt

from market_state_engine import MarketStateEngine
from regime_controller import RegimeController
from position_risk_manager import PositionRiskManager
from telegram_notifier import TelegramNotifier


# ═══════════════════════════════════════════
# CONFIGURAZIONE LOGGER DETTAGLIATO
# ═══════════════════════════════════════════
regime_logger = logging.getLogger('regime_decisions')
regime_logger.setLevel(logging.INFO)
regime_handler = logging.FileHandler('paper_trading_30d/regime_decisions.log')
regime_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
regime_logger.addHandler(regime_handler)
# ═══════════════════════════════════════════

class AutonomousTradingBot:
    """
    Bot completamente autonomo con notifiche Telegram
    - Valuta market state
    - Decide regime
    - Gestisce risk
    - Logga tutto
    - Notifica su Telegram
    """
    
    def __init__(self, initial_capital=1000, symbols=None):
        self.exchange = ccxt.binance()
        
        # Core modules
        self.market_engine = MarketStateEngine()
        self.regime_controller = RegimeController()
        self.risk_manager = PositionRiskManager(initial_capital)
        
        # Telegram notifier
        try:
            self.notifier = TelegramNotifier()
            self.TELEGRAM_ENABLED = self.notifier.enabled
            if self.TELEGRAM_ENABLED:
                self.notifier.send_message(
                    "🤖 <b>Trading Bot Avviato</b>\n"
                    f"💰 Capitale: ${initial_capital}\n"
                    f"📊 Simboli: {len(symbols or ['BTC/USDT', 'ETH/USDT', 'SOL/USDT'])}\n"
                    "✅ Monitoring attivo..."
                )
        except Exception as e:
            print(f"⚠️ Telegram non disponibile: {e}")
            self.TELEGRAM_ENABLED = False
            self.notifier = None
        
        # Trading universe
        self.symbols = symbols or ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        
        # State
        self.is_running = False
        self.cycle_count = 0
        
        # Logging
        self.logger = self._setup_logger()
        
        print("🤖 Autonomous Trading Bot V36 Initialized")
        print(f"   Capital: ${initial_capital}")
        print(f"   Universe: {', '.join(self.symbols)}")
        print(f"   Telegram: {'✅ Enabled' if self.TELEGRAM_ENABLED else '❌ Disabled'}")
    
    def _setup_logger(self):
        logger = logging.getLogger('AutonomousBot')
        logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler('autonomous_bot.log')
        fh.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(fh)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(ch)
        
        return logger
    
    def run_cycle(self):
        """
        Single trading cycle
        """
        self.cycle_count += 1
        
        self.logger.info("\n" + "="*80)
        self.logger.info(f"🔄 CYCLE {self.cycle_count} - {datetime.now()}")
        self.logger.info("="*80)
        
        # Step 1: Check existing positions
        self._check_existing_positions()
        
        # Step 2: Look for new opportunities
        self._scan_for_opportunities()
        
        # Step 3: Portfolio status
        self._log_portfolio_status()
        
        self.logger.info("="*80 + "\n")
    
    def _check_existing_positions(self):
        """
        Manage existing positions
        """
        if not self.risk_manager.positions:
            self.logger.info("📊 No active positions")
            return
        
        self.logger.info(f"📊 Checking {len(self.risk_manager.positions)} active positions")
        
        for symbol in list(self.risk_manager.positions.keys()):
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                
                action, reason = self.risk_manager.check_position_exits(symbol, current_price)
                
                if action == 'EXIT':
                    self.logger.info(f"   🔴 CLOSING {symbol}: {reason}")
                    
                    # Get position data before closing
                    pos = self.risk_manager.positions[symbol]
                    entry_price = pos['entry']
                    pnl = ((current_price - entry_price) / entry_price) * 100
                    
                    success, msg = self.risk_manager.close_position(symbol, current_price, reason)
                    self.logger.info(f"      {msg}")
                    
                    # Telegram notification
                    if success and self.TELEGRAM_ENABLED and self.notifier:
                        emoji = "🎉" if pnl > 0 else "😢"
                        self.notifier.send_message(
                            f"🔴 <b>POSIZIONE CHIUSA</b> {emoji}\n"
                            f"📊 Asset: {symbol}\n"
                            f"💵 Entry: ${entry_price:.2f}\n"
                            f"💰 Exit: ${current_price:.2f}\n"
                            f"📈 PnL: <b>{pnl:+.2f}%</b>\n"
                            f"ℹ️ Motivo: {reason}"
                        )
                else:
                    pos = self.risk_manager.positions[symbol]
                    pnl = ((current_price - pos['entry']) / pos['entry']) * 100
                    self.logger.info(f"   ✅ HOLDING {symbol}: PnL {pnl:+.2f}%")
            
            except Exception as e:
                self.logger.error(f"   ❌ Error checking {symbol}: {e}")
    
    def _scan_for_opportunities(self):
        """
        Scan for new trade opportunities
        """
        self.logger.info("\n🔍 Scanning for opportunities...")
        
        for symbol in self.symbols:
            try:
                # Skip if already have position
                if symbol in self.risk_manager.positions:
                    continue
                
                # Evaluate through regime controller
                can_trade, signal, reason = self.regime_controller.evaluate_trading_decision(symbol)
                
                if can_trade and signal and signal['signal'] in ['BUY', 'SELL']:
                    # Pre-trade risk check
                    can_open, risk_reason = self.risk_manager.can_open_position(symbol)
                    
                    if can_open:
                        # Calculate position size
                        size = self.risk_manager.calculate_position_size(signal, symbol)
                        
                        # Open position
                        success, msg = self.risk_manager.open_position(symbol, signal, size)
                        
                        if success:
                            self.logger.info(f"   🟢 OPENED {symbol} {signal['signal']}")
                            self.logger.info(f"      Entry: {signal['entry']:.2f}")
                            self.logger.info(f"      TP: {signal.get('take_profit', 'N/A')}")
                            self.logger.info(f"      SL: {signal.get('stop_loss', 'N/A')}")
                            self.logger.info(f"      Size: {size:.4f}")
                            
                            # Telegram notification
                            if self.TELEGRAM_ENABLED and self.notifier:
                                tp = signal.get('take_profit', 0)
                                sl = signal.get('stop_loss', 0)
                                tp_pct = ((tp - signal['entry']) / signal['entry'] * 100) if tp else 0
                                sl_pct = ((sl - signal['entry']) / signal['entry'] * 100) if sl else 0
                                
                                self.notifier.send_message(
                                    f"🟢 <b>POSIZIONE APERTA</b>\n"
                                    f"📊 Asset: {symbol}\n"
                                    f"🎯 Direzione: <b>{signal['signal']}</b>\n"
                                    f"💵 Entry: ${signal['entry']:.2f}\n"
                                    f"🎯 Target: ${tp:.2f} (+{tp_pct:.1f}%)\n"
                                    f"🛑 Stop: ${sl:.2f} ({sl_pct:.1f}%)\n"
                                    f"📦 Size: {size:.4f}"
                                )
                        else:
                            self.logger.warning(f"   ⚠️  Failed to open {symbol}: {msg}")
                    else:
                        self.logger.info(f"   ⛔ {symbol}: Risk check failed - {risk_reason}")
                
                else:
                    # Log why NO TRADE in compact form
                    self.logger.info(f"   ⚪ {symbol}: NO TRADE - {reason.split(chr(10))[0]}")
            
            except Exception as e:
                self.logger.error(f"   ❌ Error scanning {symbol}: {e}")
    
    def _log_portfolio_status(self):
        """
        Log current portfolio status
        """
        metrics = self.risk_manager.get_portfolio_metrics()
        
        self.logger.info("\n💼 PORTFOLIO STATUS:")
        self.logger.info(f"   Capital: ${metrics['capital']:.2f}")
        self.logger.info(f"   Total PnL: ${metrics['total_pnl']:.2f} ({metrics['total_pnl_pct']:+.2f}%)")
        self.logger.info(f"   Daily PnL: ${metrics['daily_pnl']:.2f}")
        self.logger.info(f"   Win Rate: {metrics['win_rate']:.1f}%")
        self.logger.info(f"   Max DD: {metrics['max_drawdown']:.2f}%")
        self.logger.info(f"   Positions: {metrics['active_positions']}/{self.risk_manager.MAX_POSITIONS}")
    
    def run(self, cycle_interval_minutes=120):
        """
        Main loop - runs indefinitely
        """
        self.is_running = True
        
        self.logger.info("\n" + "="*80)
        self.logger.info("🚀 AUTONOMOUS BOT STARTED")
        self.logger.info("="*80)
        self.logger.info(f"   Cycle Interval: {cycle_interval_minutes} minutes")
        self.logger.info(f"   Symbols: {', '.join(self.symbols)}")
        self.logger.info("="*80 + "\n")
        
        try:
            while self.is_running:
                self.run_cycle()
                
                # Sleep until next cycle
                self.logger.info(f"⏸️  Next cycle in {cycle_interval_minutes} minutes...\n")
                time.sleep(cycle_interval_minutes * 60)
        
        except KeyboardInterrupt:
            self.logger.info("\n🛑 Bot stopped by user")
            self.is_running = False
            
            if self.TELEGRAM_ENABLED and self.notifier:
                self.notifier.send_message("🛑 <b>Bot Fermato</b>\nArresto manuale")
        
        except Exception as e:
            self.logger.error(f"\n❌ Bot crashed: {e}")
            self.is_running = False
            
            if self.TELEGRAM_ENABLED and self.notifier:
                self.notifier.send_message(f"❌ <b>Bot Crashato</b>\n{str(e)[:200]}")
        
        finally:
            # Final report
            self.logger.info("\n" + "="*80)
            self.logger.info("📊 FINAL REPORT")
            self.logger.info("="*80)
            
            metrics = self.risk_manager.get_portfolio_metrics()
            self.logger.info(f"Total Cycles: {self.cycle_count}")
            self.logger.info(f"Total Trades: {metrics['total_trades']}")
            self.logger.info(f"Final Capital: ${metrics['capital']:.2f}")
            self.logger.info(f"Total Return: {metrics['total_pnl_pct']:+.2f}%")
            self.logger.info("="*80)
            
            if self.TELEGRAM_ENABLED and self.notifier:
                self.notifier.send_message(
                    f"📊 <b>Report Finale</b>\n"
                    f"🔄 Cicli: {self.cycle_count}\n"
                    f"💼 Trades: {metrics['total_trades']}\n"
                    f"💰 Capitale: ${metrics['capital']:.2f}\n"
                    f"📈 Return: <b>{metrics['total_pnl_pct']:+.2f}%</b>"
                )

# Run bot
if __name__ == "__main__":
    bot = AutonomousTradingBot(
        initial_capital=202.64,
        symbols=['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
    )
    
    # Run with 2-hour cycles
    bot.run(cycle_interval_minutes=120)