# 🚀 PERPETUAL BOT V1

Bot di trading automatico per Binance Futures con leva 2-3x.

## 📊 CARATTERISTICHE

- **Capitale:** $100 USDT (separato da V37)
- **Leva:** 2x (max 3x dopo 30 trade)
- **Direzioni:** LONG + SHORT
- **Assets:** BTC/USDT, ETH/USDT
- **Timeframe:** 1H principale, 4H conferma
- **Stop Loss:** -3% fisso
- **Take Profit:** +7% base
- **Trailing Stop:** Attivo a +4%, trail 2%

## 🎯 STRATEGIA

### Entry Conditions
**LONG:**
- Prezzo > EMA200
- EMA50 > EMA200
- Pullback a EMA20
- RSI 45-55
- Volume > 1.2x media

**SHORT:**
- Prezzo < EMA200
- EMA50 < EMA200
- Pullback a EMA20
- RSI 45-55
- Volume > 1.2x media

### Risk Management
- Position size: 20% capitale
- Rischio per trade: 0.75%
- Daily loss limit: -8%
- Max consecutive losses: 2 → Cooldown 24h
- Max trades/day: 1

### Blockers
- ATR > 3.5% → NO TRADE
- Funding rate extremo → Block direzione
- Volume insufficiente → NO TRADE
- Market RANGING → NO TRADE

## 🎮 COMANDI

### Start Bot
```bash
./start_perpetual.sh
```

### Stop Bot
```bash
./stop_perpetual.sh
```

### Check Status
```bash
./status_perpetual.sh
```

### Monitor Live
```bash
tail -f perpetual_output.log
```

## 📋 FILES

- `perpetual_config.json` - Configurazione
- `perpetual_bot.py` - Core engine
- `signal_generator.py` - Generazione segnali
- `risk_manager.py` - Gestione rischio
- `indicators.py` - Indicatori tecnici
- `main.py` - Main runner

## ⚠️ IMPORTANTE

- **PAPER TRADING MODE** - Nessun trade reale
- Capitale separato da V37 Spot
- Cicli ogni 2 ore (come V37)
- Diversificazione strategia

## 🎯 TARGETS

- Win Rate: 45-55%
- Sharpe: 2-3
- Trades/mese: 5-10
- Max DD: -15%

## 🚨 SAFETY

- Leva MAX 3x
- Position size cap 20%
- Stop loss sempre attivo
- Daily loss limit -8%
- Cooldown dopo 2 loss consecutive

---

**Bot V1 - Production Ready** 🚀
