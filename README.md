# 🤖 Quantum Trading System V36

Sistema di trading autonomo con gestione rischio professionale e notifiche Telegram.

## 🚀 Quick Start
```bash
git clone https://github.com/LorenzoPacc/QuantumTradingSystem.git
cd QuantumTradingSystem
python3 -m venv venv
source venv/bin/activate
pip install ccxt python-dotenv requests
cp .env.example .env
nano .env  # Aggiungi credenziali
nohup python3 autonomous_trading_bot.py > bot_output.log 2>&1 &
```

## 📊 Features

- ✅ Trading autonomo 24/7
- ✅ Market State Engine + Regime Controller
- ✅ Risk Management professionale
- ✅ Telegram notifications
- ✅ Persistence (JSON backup)
- ✅ Multi-asset (BTC/ETH/SOL)

## 🔧 Config

Capital: $200 | Max Positions: 3 | Risk: 0.5% | Cycle: 120 min

## 📱 Commands
```bash
~/qcheck      # Status
~/qanalysis   # Market
~/qmonitor    # Live log
```

## 📦 Core Files

- `autonomous_trading_bot.py` - Main bot
- `market_state_engine.py` - Market analysis
- `position_risk_manager.py` - Risk + Persistence
- `telegram_notifier.py` - Notifications
