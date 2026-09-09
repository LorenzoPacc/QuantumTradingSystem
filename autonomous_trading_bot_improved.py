#!/usr/bin/env python3
"""
AUTONOMOUS TRADING BOT - V37 IMPROVED EDITION (FIXED)
Con infrastruttura produzione: snapshot, safe mode, tracking

CORREZIONI APPLICATE:
1. ✅ Logger duplicato rimosso
2. ✅ Trailing states nel snapshot
3. ✅ Idempotency negli ordini
4. ✅ Rate weights centralizzati
"""

import time
import logging
import os
import sys
import fcntl
import signal
import threading
from datetime import datetime
import ccxt

from market_state_engine import MarketStateEngine
from regime_controller import RegimeController
from cost_calculator import CostCalculator
from position_risk_manager import PositionRiskManager, StatePersistenceError
from telegram_notifier import TelegramNotifier


# ═══════════════════════════════════════════
# B17: PROCESS SINGLETON LOCK
# Impedisce più istanze V37 anche se il bot
# viene avviato manualmente senza bot_control.sh
# ═══════════════════════════════════════════
_SINGLETON_LOCK_HANDLE = None


def _acquire_singleton_lock(lock_path=None):
    global _SINGLETON_LOCK_HANDLE

    if _SINGLETON_LOCK_HANDLE is not None:
        return True, str(os.getpid())

    if lock_path is None:
        lock_path = f"/tmp/quantum_v37_{os.getuid()}.lock"

    lock_handle = open(lock_path, "a+")

    try:
        fcntl.flock(
            lock_handle.fileno(),
            fcntl.LOCK_EX | fcntl.LOCK_NB
        )
    except BlockingIOError:
        lock_handle.seek(0)
        owner = lock_handle.read().strip() or "unknown"
        lock_handle.close()
        return False, owner

    lock_handle.seek(0)
    lock_handle.truncate()
    lock_handle.write(str(os.getpid()))
    lock_handle.flush()

    # Il file descriptor deve rimanere aperto
    # per tutta la vita del processo.
    _SINGLETON_LOCK_HANDLE = lock_handle

    return True, str(os.getpid())


# ═══════════════════════════════════════════
# IMPROVEMENTS - IMPORT
# ═══════════════════════════════════════════
from snapshot_manager import init_snapshot_manager, save_bot_state, restore_bot_state
from log_manager import init_log_manager
from safe_mode_manager import init_safe_mode_manager, TradingMetrics
from api_protection import init_api_protection
from tracking_systems import init_tracking_systems
# ═══════════════════════════════════════════

# Logger regime (esistente)
regime_logger = logging.getLogger('regime_decisions')
regime_logger.setLevel(logging.INFO)
regime_handler = logging.FileHandler('paper_trading_30d/regime_decisions.log')
regime_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
regime_logger.addHandler(regime_handler)

# ═══════════════════════════════════════════
# FIX #4: RATE WEIGHTS CENTRALIZZATI
# ═══════════════════════════════════════════
RATE_WEIGHTS = {
    'fetch_ticker': 1,
    'fetch_ohlcv': 2,
    'fetch_order_book': 2,
    'create_order': 1,
    'cancel_order': 1,
    'fetch_balance': 1,
    'market_scan': 2,
}
# ═══════════════════════════════════════════


class AutonomousTradingBot:
    """
    Bot completamente autonomo con improvements
    - Snapshot automatici (con trailing states)
    - Safe mode protection
    - Rate limiting (pesi centralizzati)
    - Idempotency (prevenzione duplicati)
    - Timeline tracking
    """

    def __init__(self, initial_capital=202.62, symbols=None):
        self.exchange = ccxt.binance()

        # Core modules
        self.market_engine = MarketStateEngine()
        self.regime_controller = RegimeController()
        self.cost_calculator = CostCalculator(is_spot=True)  # V37 is SPOT
        self.risk_manager = PositionRiskManager(initial_capital)

        # ═══════════════════════════════════════════
        # IMPROVEMENTS INITIALIZATION
        # ═══════════════════════════════════════════
        print("🛠️  Inizializzazione improvements...")
        
        # 1. Log Manager (PRIMO!) - FIX #1: Gestisce già il file
        self.log_mgr = init_log_manager("autonomous_bot.log")
        
        # 2. Snapshot Manager
        self.snapshot_mgr = init_snapshot_manager()
        
        # 3. Safe Mode Manager
        self.safe_mgr = init_safe_mode_manager()
        
        # 4. API Protection
        protection = init_api_protection()
        self.rate_limiter = protection['rate_limiter']
        self.idempotency = protection['idempotency']
        self.degradation = protection['degradation']
        
        # 5. Tracking Systems
        tracking = init_tracking_systems(window_size=20)
        self.timeline = tracking['timeline']
        self.metrics = tracking['metrics']
        
        # 6. B18: snapshot precedente SOLO diagnostico.
        # Lo stato operativo ufficiale viene caricato dal
        # PositionRiskManager con B14/B19.
        snapshot_state = restore_bot_state(self.snapshot_mgr)

        if snapshot_state:
            logging.info(
                "ℹ️ Snapshot precedente disponibile come checkpoint "
                "diagnostico; stato live NON sovrascritto"
            )

        print("✅ Improvements attivi")
        # ═══════════════════════════════════════════

        # Telegram notifier
        try:
            self.notifier = TelegramNotifier()
            self.TELEGRAM_ENABLED = self.notifier.enabled
            if self.TELEGRAM_ENABLED:
                self.notifier.send_message(
                    "🤖 <b>Trading Bot V37 Avviato</b>\n"
                    f"💰 Capitale: ${initial_capital}\n"
                    f"📊 Simboli: {len(symbols or ['BTC/USDT', 'ETH/USDT', 'SOL/USDT'])}\n"
                    "✅ Improvements attivi\n"
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
        self.daily_pnl = 0.0

        # Logging (FIX #1: Solo console, file gestito da log_manager)
        self.logger = self._setup_logger()

        print("🤖 Autonomous Trading Bot V37 Initialized (FIXED)")
        print(f"   Capital: ${initial_capital}")
        print(f"   Universe: {', '.join(self.symbols)}")
        print(f"   Telegram: {'✅ Enabled' if self.TELEGRAM_ENABLED else '❌ Disabled'}")
        print(f"   Improvements: ✅ Active (all fixes applied)")

    def _setup_logger(self):
        """
        FIX #1: LOGGER SENZA DUPLICATI
        FileHandler rimosso - gestito da log_manager
        """
        logger = logging.getLogger('AutonomousBot')
        logger.setLevel(logging.INFO)

        # ❌ RIMOSSO: FileHandler duplicato
        # fh = logging.FileHandler('autonomous_bot.log')
        # fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        # logger.addHandler(fh)

        # ✅ SOLO Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(ch)

        return logger

    def run_cycle(self):
        """
        Single trading cycle - con improvements e fix
        """
        self.cycle_count += 1
        self._send_health_check()
        self._reset_daily_pnl_if_needed()
        cycle_start = time.time()

        self.logger.info("\n" + "="*80)
        self.logger.info(f"🔄 CYCLE {self.cycle_count} - {datetime.now()}")
        self.logger.info("="*80)

        # ═══════════════════════════════════════════
        # Graceful Degradation Check
        # ═══════════════════════════════════════════
        if self.degradation.should_skip_cycle():
            self.logger.warning("⏭️ Ciclo saltato per instabilità API")
            time.sleep(120)
            return
        # ═══════════════════════════════════════════

        # ═══════════════════════════════════════════
        # Safe Mode Check
        # ═══════════════════════════════════════════
        current_capital = self.risk_manager.current_capital
        
        metrics = TradingMetrics(
            daily_pnl_percent=(self.daily_pnl / current_capital * 100) if current_capital > 0 else 0,
            api_errors_count=self.degradation.consecutive_errors
        )
        
        safe_status = self.safe_mgr.check_and_update(metrics)
        
        # KILL SWITCH
        if safe_status['kill_switch']:
            self.logger.critical("🚨 KILL SWITCH ATTIVATO - BOT FERMATO")
            self.logger.critical(f"🚨 Motivo: {safe_status['reason']}")
            
            if self.TELEGRAM_ENABLED and self.notifier:
                self.notifier.send_message(
                    "🚨 <b>KILL SWITCH ATTIVATO</b>\n"
                    f"Motivo: {safe_status['reason']}\n"
                    "⚠️ Bot fermato - intervento richiesto"
                )
            
            self.is_running = False
            return
        
        # SAFE MODE
        allow_new_entries = safe_status['allow_new_entries']
        if not allow_new_entries:
            self.logger.warning(f"🛡️ SAFE MODE ATTIVO: {safe_status['reason']}")
            self.logger.info("   → Gestisco solo posizioni esistenti")
        # ═══════════════════════════════════════════

        # Step 1: Check existing positions (SEMPRE)
        self._check_existing_positions()

        # Step 2: Look for new opportunities (SOLO SE NO SAFE MODE)
        if allow_new_entries:
            self._scan_for_opportunities()
        else:
            self.logger.info("⏸️ Ricerca nuove opportunità disabilitata (safe mode)")

        # Step 3: Portfolio status
        self._log_portfolio_status()

        # ═══════════════════════════════════════════
        # Snapshot periodico - FIX #2: CON TRAILING STATES
        # ═══════════════════════════════════════════
        if self.snapshot_mgr.should_save(self.cycle_count):
            # Recupera trailing states (se esiste nel risk_manager)
            trailing_states = {}
            if hasattr(self.risk_manager, 'trailing_states'):
                trailing_states = self.risk_manager.trailing_states
            elif hasattr(self.risk_manager, 'get_trailing_states'):
                trailing_states = self.risk_manager.get_trailing_states()
            
            save_bot_state(
                self.snapshot_mgr,
                cycle=self.cycle_count,
                capital=current_capital,
                positions=self.risk_manager.positions,
                trailing_states=trailing_states,  # ✅ FIX #2
                daily_pnl=self.daily_pnl
            )
        # ═══════════════════════════════════════════

        # ═══════════════════════════════════════════
        # Statistiche periodiche
        # ═══════════════════════════════════════════
        if self.cycle_count % 10 == 0:
            self.risk_manager._save_capital()  # 💾 persist capital
            # Rate limiter stats
            rl_stats = self.rate_limiter.get_stats()
            self.logger.info(
                f"📊 API Usage: {rl_stats['calls_last_minute']}/{rl_stats['limit']} "
                f"({rl_stats['usage_percent']:.1f}%)"
            )
            
            # Metriche rolling
            if len(self.metrics.recent_trades) >= 5:
                m = self.metrics.calculate_metrics()
                self.logger.info(
                    f"📈 Performance (ultimi {m['trades_in_window']} trade): "
                    f"WR={m['win_rate']}% | Exp=${m['expectancy']:.2f}"
                )
        # ═══════════════════════════════════════════

        cycle_duration = time.time() - cycle_start
        try:
            with open('last_cycle.txt', 'w') as _lc:
                _lc.write(str(time.time()))
        except Exception:
            pass
        self.logger.info(f"⏱️ Ciclo durato {cycle_duration:.1f}s")
        self.logger.info("="*80)
        self.logger.info("⏰ Next cycle in 2 hours (7200 seconds)...")
        self.logger.info("="*80 + "\n")

    def _check_existing_positions(self):
        """
        Manage existing positions - con improvements
        """
        if not self.risk_manager.positions:
            self.logger.info("📊 No active positions")
            return

        self.logger.info(f"📊 Checking {len(self.risk_manager.positions)} active positions")

        for symbol in list(self.risk_manager.positions.keys()):
            try:
                # ═══════════════════════════════════════════
                # Rate limiting - FIX #4: Peso centralizzato
                # ═══════════════════════════════════════════
                self.rate_limiter.wait_if_needed(weight=RATE_WEIGHTS['fetch_ticker'])
                # ═══════════════════════════════════════════
                
                # ═══════════════════════════════════════════
                # Graceful degradation
                # ═══════════════════════════════════════════
                ticker = self.degradation.execute_with_retry(
                    self.exchange.fetch_ticker,
                    symbol
                )
                
                if ticker is None:
                    self.logger.error(f"❌ Impossibile ottenere prezzo per {symbol}")
                    self.safe_mgr.record_api_error("fetch_ticker_failed")
                    continue
                # ═══════════════════════════════════════════
                
                current_price = ticker.get('last')
                if not current_price or current_price <= 0:
                    self.logger.error(f'🚨 Prezzo invalido {symbol}: {current_price} - skip')
                    continue  # price_invalid

                action, reason = self.risk_manager.check_position_exits(symbol, current_price)

                if action == 'EXIT':
                    self.logger.info(f"   🔴 CLOSING {symbol}: {reason}")

                    # Get position data before closing
                    pos = self.risk_manager.positions[symbol]
                    entry_price = pos['entry']
                    success, msg = self.risk_manager.close_position(symbol, current_price, reason)
                    self.logger.info(f"      {msg}")
                    last_trade = self.risk_manager.trades[-1] if success and self.risk_manager.trades else None
                    pnl = last_trade['pnl_pct'] if last_trade else 0
                    pnl_dollars = last_trade['pnl'] if last_trade else 0
                    
                    # ═══════════════════════════════════════════
                    # Tracking
                    # ═══════════════════════════════════════════
                    if success:
                        # Aggiorna PnL giornaliero
                        self.daily_pnl += pnl_dollars
                        
                        # Metriche rolling
                        self.metrics.add_trade(
                            symbol=symbol,
                            side=pos.get('side', 'LONG'),
                            pnl=pnl_dollars,
                            pnl_percent=pnl,
                            duration=time.time() - pos.get('entry_time', time.time()),
                            exit_reason=reason
                        )
                    # ═══════════════════════════════════════════

                    # Telegram notification
                    if success and self.TELEGRAM_ENABLED and self.notifier:
                        emoji = "🎉" if pnl > 0 else "😢"
                        self.notifier.send_message(
                            f"🔴 <b>POSIZIONE CHIUSA</b> {emoji}\n"
                            f"📊 Asset: {symbol}\n"
                            f"💵 PnL: {pnl:+.2f}% (${pnl_dollars:+.2f})\n"
                            f"📝 Motivo: {reason}"
                        )

            except StatePersistenceError as e:
                self.logger.critical(
                    f"🚨 ERRORE FATALE PERSISTENZA {symbol}: {e}"
                )

                if self.TELEGRAM_ENABLED and self.notifier:
                    try:
                        self.notifier.send_message(
                            f"🚨 <b>ERRORE FATALE PERSISTENZA</b>\n"
                            f"Symbol: <b>{symbol}</b>\n"
                            f"Errore: <code>{str(e)[:300]}</code>\n"
                            "⛔ V37 in arresto per proteggere lo stato"
                        )
                    except Exception as notify_error:
                        self.logger.error(
                            f"Errore notifica persistence failure: "
                            f"{notify_error}"
                        )

                raise

            except Exception as e:
                self.logger.error(f"❌ Error checking {symbol}: {e}")
                if self.TELEGRAM_ENABLED and self.notifier:
                    self.notifier.send_message(
                        f"🚨 <b>ERRORE POSIZIONE</b>\n"
                        f"Symbol: <b>{symbol}</b>\n"
                        f"Errore: <code>{str(e)[:300]}</code>\n"
                        f"Ciclo: {self.cycle_count}"
                    )
                self.safe_mgr.record_api_error(str(e))

    def _scan_for_opportunities(self):
        """
        Scan for new trade opportunities - TUA LOGICA ORIGINALE
        """
        self.logger.info("🔍 Scanning for opportunities...")
        
        for symbol in self.symbols:
            try:
                # ═══════════════════════════════════════════
                # Rate limiting (improvements)
                # ═══════════════════════════════════════════
                self.rate_limiter.wait_if_needed(weight=RATE_WEIGHTS['market_scan'])
                # ═══════════════════════════════════════════
                
                # Skip if already have position
                if symbol in self.risk_manager.positions:
                    continue
                
                # Evaluate through regime controller (TUA LOGICA)
                can_trade, signal, reason = self.regime_controller.evaluate_trading_decision(symbol)
                
                # DEBUG: Log decisione
                self.logger.info(f"   {symbol}: can_trade={can_trade}, signal={signal.get('signal') if signal else None}, reason={reason}")
                

                # COST FILTER - Expected Edge > (Fee + Slippage) * 2.5
                if can_trade and signal:
                    expected_edge = 0.04  # 4% medio target
                    cost_ok, cost_reason = self.cost_calculator.should_trade_based_on_edge(
                        expected_edge, symbol
                    )
                    if not cost_ok:
                        self.logger.info(f"      ❌ COST FILTER: {cost_reason}")
                        can_trade = False
                        reason = cost_reason

                if can_trade and signal and signal['signal'] in ['BUY', 'SELL']:
                    # ═══════════════════════════════════════════
                    # Idempotency check (improvements)
                    # ═══════════════════════════════════════════
                    trade_key = self.idempotency.generate_key(
                        symbol=symbol,
                        side=signal['signal'],
                        timestamp=time.time(),
                        price=signal['entry']
                    )
                    
                    if not self.idempotency.check_and_set(trade_key):
                        self.logger.warning(f"⚠️ Trade duplicato evitato: {symbol}")
                        continue
                    # ═══════════════════════════════════════════
                    
                    # Pre-trade risk check
                    can_open, risk_reason = self.risk_manager.can_open_position(symbol)
                    
                    if can_open:
                        # Calculate position size
                        size = self.risk_manager.calculate_position_size(signal, symbol)
                        
                        # ═══════════════════════════════════════════
                        # Rate limiting for order (improvements)
                        # ═══════════════════════════════════════════
                        self.rate_limiter.wait_if_needed(weight=RATE_WEIGHTS.get('create_order', 1))
                        # ═══════════════════════════════════════════
                        
                        # Open position
                        success, msg = self.risk_manager.open_position(symbol, signal, size)
                        
                        if success:
                            self.logger.info(f"   🟢 OPENED {symbol} {signal['signal']}")
                            self.logger.info(f"      Entry: {signal['entry']:.2f}")
                            self.logger.info(f"      TP: {signal.get('take_profit', 'N/A')}")
                            self.logger.info(f"      SL: {signal.get('stop_loss', 'N/A')}")
                            self.logger.info(f"      Size: {size:.4f}")
                            
                            # ═══════════════════════════════════════════
                            # Timeline tracking (improvements)
                            # ═══════════════════════════════════════════
                            trade_id = f"trade_{self.cycle_count}_{symbol}"
                            self.timeline.record_event(
                                trade_id=trade_id,
                                event_type="entry",
                                price=signal['entry'],
                                signal=signal['signal'],
                                size=size
                            )
                            # ═══════════════════════════════════════════
                            
                            # Telegram notification
                            if self.TELEGRAM_ENABLED and self.notifier:
                                tp = signal.get('take_profit', 0)
                                sl = signal.get('stop_loss', 0)
                                tp_pct = ((tp - signal['entry']) / signal['entry'] * 100) if tp else 0
                                sl_pct = ((sl - signal['entry']) / signal['entry'] * 100) if sl else 0
                                
                                self.notifier.send_message(
                                    "🟢 <b>POSIZIONE APERTA</b>\n"
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
                        self.logger.info(f"   ⏸️ Cannot open {symbol}: {risk_reason}")
                else:
                    if reason:
                        self.logger.debug(f"   ⏸️ {symbol}: {reason}")
            
            except StatePersistenceError as e:
                self.logger.critical(
                    f"🚨 ERRORE FATALE PERSISTENZA {symbol}: {e}"
                )

                if self.TELEGRAM_ENABLED and self.notifier:
                    try:
                        self.notifier.send_message(
                            f"🚨 <b>ERRORE FATALE PERSISTENZA</b>\n"
                            f"Symbol: <b>{symbol}</b>\n"
                            f"Errore: <code>{str(e)[:300]}</code>\n"
                            "⛔ V37 in arresto per proteggere lo stato"
                        )
                    except Exception as notify_error:
                        self.logger.error(
                            f"Errore notifica persistence failure: "
                            f"{notify_error}"
                        )

                raise

            except Exception as e:
                self.logger.error(f"❌ Error scanning {symbol}: {e}")
                if self.TELEGRAM_ENABLED and self.notifier:
                    self.notifier.send_message(
                        f"⚠️ <b>ERRORE SCANSIONE</b>\n"
                        f"Symbol: <b>{symbol}</b>\n"
                        f"Errore: <code>{str(e)[:300]}</code>\n"
                        f"Ciclo: {self.cycle_count}"
                    )
                # ═══════════════════════════════════════════
                # Track API errors (improvements)
                # ═══════════════════════════════════════════
                self.safe_mgr.record_api_error(str(e))
                # ═══════════════════════════════════════════
    def _should_open_position(self, market_state, regime):
        """
        Determina se aprire posizione
        (ADATTA ALLA TUA LOGICA)
        """
        # Placeholder - implementa la tua logica
        return False

    def _log_portfolio_status(self):
        """
        Log portfolio status
        """
        total_value = self.risk_manager.current_capital
        
        self.logger.info("💼 PORTFOLIO STATUS")
        self.logger.info(f"   Total Value: ${total_value:.2f}")
        self.logger.info(f"   Available: ${self.risk_manager.current_capital:.2f}")
        self.logger.info(f"   Positions: {len(self.risk_manager.positions)}")
        self.logger.info(f"   Daily PnL: ${self.daily_pnl:+.2f}")


    def _reset_daily_pnl_if_needed(self):
        """Reset giornaliero e ripristino PnL dopo restart"""
        today = datetime.now().date()
        last = getattr(self, "_last_reset_date", None)

        # Primo ciclo del processo: non azzerare alla cieca.
        # Ricostruisce il PnL dei trade già chiusi oggi.
        if last is None:
            today_key = today.isoformat()
            reconstructed_pnl = 0.0

            for trade in self.risk_manager.trades:
                closed_at = trade.get("closed_at")

                if isinstance(closed_at, str) and closed_at[:10] == today_key:
                    try:
                        reconstructed_pnl += float(trade.get("pnl", 0) or 0)
                    except (TypeError, ValueError):
                        self.logger.warning(
                            f"⚠️ PnL non numerico ignorato nel daily restore: {trade}"
                        )

            self.daily_pnl = reconstructed_pnl
            self.risk_manager.daily_pnl = reconstructed_pnl
            self._last_reset_date = today

            self.logger.info(
                f"🔄 Daily PnL restored: {today} "
                f"${reconstructed_pnl:+.2f}"
            )
            return

        # Vero cambio di giornata durante lo stesso processo.
        if last != today:
            self._last_reset_date = today
            self.daily_pnl = 0.0
            self.risk_manager.daily_pnl = 0
            self.logger.info(f"🔄 Daily PnL reset: {today}")

    def _send_health_check(self):
        """Health check Telegram ogni 24h (12 cicli x 2h)"""
        if not (self.TELEGRAM_ENABLED and self.notifier):
            return
        if self.cycle_count == 0 or self.cycle_count % 12 != 0:
            return
        metrics = self.risk_manager.get_portfolio_metrics()
        total = metrics.get('total_trades', 0)
        wr = metrics.get('win_rate', 0)
        pos_list = ''.join(
            f"  • {sym} @ ${pos['entry']:.2f}\n"
            for sym, pos in self.risk_manager.positions.items()
        ) or '  Nessuna'
        self.notifier.send_message(
            f"📊 <b>HEALTH CHECK 24H</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💰 Capital: <b>${metrics['capital']:.2f}</b>\n"
            f"📈 PnL: <b>{metrics['total_pnl_pct']:+.2f}%</b>\n"
            f"🔄 Cicli: {self.cycle_count}\n"
            f"💼 Trade: {total} | WR: {wr:.0f}%\n"
            f"📌 Posizioni:\n{pos_list}\n"
            f"✅ Sistema operativo"
        )
        self.logger.info('📊 Health check 24h inviato')

    def start(self):
        """
        Start autonomous trading - con improvements
        """
        self.is_running = True
        shutdown_event = threading.Event()

        previous_sigterm_handler = signal.getsignal(signal.SIGTERM)

        def _handle_sigterm(signum, frame):
            self.logger.info(
                "🛑 SIGTERM ricevuto - shutdown controllato richiesto"
            )
            self.is_running = False
            shutdown_event.set()

        signal.signal(signal.SIGTERM, _handle_sigterm)

        self.logger.info("🚀 Starting autonomous trading loop...")

        try:
            while self.is_running:
                self.run_cycle()

                if self.is_running:
                    # B18f: attesa interrompibile da SIGTERM,
                    # senza eccezioni asincrone dentro run_cycle().
                    shutdown_event.wait(7200)

            self.logger.info(
                "🛑 Shutdown controllato richiesto dal sistema"
            )

        except KeyboardInterrupt:
            self.logger.info("⌨️ Shutdown richiesto dall'utente")
        except Exception as e:
            self.logger.error(f"❌ Errore critico: {e}", exc_info=True)
            if self.TELEGRAM_ENABLED and self.notifier:
                import traceback
                tb = traceback.format_exc()[-400:]
                self.notifier.send_message(
                    f"🚨🚨 <b>CRASH CRITICO BOT</b>\n"
                    f"Errore: <code>{str(e)[:300]}</code>\n"
                    f"Ciclo: {self.cycle_count}\n"
                    f"Traceback:\n<code>{tb}</code>\n"
                    f"⛔ Riavvia: ~/bot_control.sh start"
                )
        finally:
            # Ripristina l'handler precedente prima della chiusura.
            try:
                signal.signal(
                    signal.SIGTERM,
                    previous_sigterm_handler
                )
            except Exception:
                pass

            # ═══════════════════════════════════════════
            # Snapshot finale - FIX #2: CON TRAILING STATES
            # ═══════════════════════════════════════════
            self.logger.info("💾 Salvataggio stato finale...")
            current_capital = self.risk_manager.current_capital
            
            trailing_states = {}
            if hasattr(self.risk_manager, 'trailing_states'):
                trailing_states = self.risk_manager.trailing_states
            elif hasattr(self.risk_manager, 'get_trailing_states'):
                trailing_states = self.risk_manager.get_trailing_states()
            
            save_bot_state(
                self.snapshot_mgr,
                cycle=self.cycle_count,
                capital=current_capital,
                positions=self.risk_manager.positions,
                trailing_states=trailing_states,  # ✅ FIX #2
                daily_pnl=self.daily_pnl,
                force=True
            )
            # ═══════════════════════════════════════════
            
            self.logger.info("✅ Bot stopped gracefully")
            
            if self.TELEGRAM_ENABLED and self.notifier:
                self.notifier.send_message(
                    "🛑 <b>Bot Fermato</b>\n"
                    f"💰 Capitale finale: ${current_capital:.2f}\n"
                    f"📊 Cicli completati: {self.cycle_count}\n"
                    "✅ Stato salvato"
                )


if __name__ == "__main__":
    lock_ok, lock_owner = _acquire_singleton_lock()

    if not lock_ok:
        print(
            f"❌ V37 già attivo: singleton lock occupato "
            f"(PID proprietario: {lock_owner})",
            file=sys.stderr
        )
        raise SystemExit(1)

    bot = AutonomousTradingBot(
        initial_capital=202.62,
        symbols=['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
    )
    bot.start()
