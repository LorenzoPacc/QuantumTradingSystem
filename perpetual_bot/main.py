#!/usr/bin/env python3
"""
Perpetual Bot V1 - Main Runner
"""
import signal
import threading

from perpetual_bot import PerpetualBot


stop_event = threading.Event()


def request_shutdown(signum, frame):
    print("")
    print(f"🛑 Shutdown requested (signal {signum})")
    stop_event.set()


def print_final_stats(bot):
    print("")
    print("📊 FINAL STATS:")
    print(f"   Total Trades: {len(bot.trades_history)}")
    print(f"   Final Capital: ${bot.risk_manager.current_capital:.2f}")

    if bot.trades_history:
        wins = len([t for t in bot.trades_history if t["pnl_usd"] > 0])
        wr = wins / len(bot.trades_history) * 100
        total_pnl = sum(t["pnl_usd"] for t in bot.trades_history)
        print(f"   Win Rate: {wr:.1f}%")
        print(f"   Total PnL: ${total_pnl:+.2f}")

    print("")
    print("✅ Shutdown complete")


def main():
    signal.signal(signal.SIGTERM, request_shutdown)
    signal.signal(signal.SIGINT, request_shutdown)

    print("╔════════════════════════════════════════════════════════════╗")
    print("║          🚀 PERPETUAL BOT V1 - STARTING                   ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print("")

    bot = PerpetualBot()
    cycle_interval = 7200

    print(f"⏱️  Cycle interval: {cycle_interval // 3600} hours")
    print("")
    print("🚀 Starting trading loop...")
    print("")

    try:
        while not stop_event.is_set():
            bot.run_cycle()

            if stop_event.is_set():
                break

            print("=" * 80)
            print(
                f"⏰ Next cycle in "
                f"{cycle_interval // 3600} hours "
                f"({cycle_interval} seconds)..."
            )
            print("=" * 80)
            print("")

            # Interrompibile immediatamente da SIGTERM/SIGINT.
            stop_event.wait(cycle_interval)

    except BaseException:
        print("❌ Uscita per errore: nessun salvataggio finale dalla RAM")
        raise
    else:
        # Salvataggio finale delle posizioni con la persistenza atomica B26a.
        try:
            bot.persistence.save_positions(bot.positions)
            print("💾 Final positions saved")
        except Exception as e:
            print(f"⚠️ Final positions save failed: {e}")
            raise

        print_final_stats(bot)


if __name__ == "__main__":
    main()
