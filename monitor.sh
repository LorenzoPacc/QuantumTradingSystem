#!/bin/bash
case $1 in
    "gating") tail -f quantum_v2.log | grep -E "(GATING|VALIDATION)" ;;
    "trades") tail -f quantum_v2.log | grep -E "(BUY|SELL|EXIT)" ;;
    *) tail -f quantum_v2.log | grep -E "(TRAILING|CICLO|DOTUSDT)" ;;
esac
