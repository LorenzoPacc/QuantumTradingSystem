# Quantum Trader Lite

Bot di trading crypto ottimizzato per capitale ridotto ($200-1000).

## 🚀 Quick Start

```bash
# 1. Installa dipendenze
pip install -r requirements.txt

# 2. Configura API keys (crea file .env)
echo "BINANCE_API_KEY=your_key" > .env
echo "BINANCE_SECRET=your_secret" >> .env

# 3. Test con backtest
python backtest.py

# 4. Dry-run su testnet
# Modifica config/config.yaml: testnet: true
python run.py

# 5. Live (SOLO DOPO 2 SETTIMANE DI DRY-RUN!)
# Modifica config/config.yaml: testnet: false
python run.py
```

## ✅ Bug Corretti vs Versione Precedente

1. ✅ Trailing stop con tracking max profit
2. ✅ Confidence threshold (no trade sotto 60%)
3. ✅ Calcolo trend con fallback robusto
4. ✅ Position sizing con limite confidence
5. ✅ EMA calculation safe (gestisce valori mancanti)
6. ✅ Win rate con commissioni incluse

## 📊 Performance Attese (Backtest 6 mesi)

- Win Rate: 40-50% (vs 11% precedente)
- Max Drawdown: <10%
- Sharpe Ratio: >1.5
- Trades/mese: 8-12

## ⚠️ Checklist Prima di Live

- [ ] Backtest >6 mesi positivo
- [ ] Dry-run 2 settimane su testnet
- [ ] Max 3 posizioni simultanee
- [ ] Stop-loss attivi su tutte le posizioni
- [ ] Alert Telegram configurati
- [ ] Capitale non necessario per vivere

## 📁 Struttura

```
crypto_bot/
├── strategy.py      # Logic di trading (200 righe)
├── backtest.py      # Test rapido
├── run.py           # Main loop (crea tu)
├── config/
│   └── config.yaml  # Configurazione
└── logs/            # Log operazioni
```

## 🆘 Support

Se win rate < 35% dopo 30 trade → STOP e rivedi parametri.
