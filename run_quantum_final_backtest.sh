#!/bin/bash
source quantum_env/bin/activate
python3 quantum_trader_ultimate_final.py --backtest --symbol BTCUSDT --start 2024-01-01 --end 2024-03-01
