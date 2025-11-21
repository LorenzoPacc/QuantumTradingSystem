#!/bin/bash
echo "🚀 QUANTUM TRADING - OVERVIEW COMPLETO"
echo "======================================"
echo ""

echo "📊 1. PORTAFOGLIO DATABASE:"
echo "---------------------------"
./quantum_commands.sh database | tail -n +3

echo ""
echo "📈 2. PERFORMANCE REPORT:"
echo "-------------------------"
./quantum_commands.sh performance | tail -n +3

echo ""
echo "🔍 3. ANALISI CRYPTO:"
echo "--------------------"
./crypto_analysis.sh | grep -A 20 "CRYPTO IN MONITORAGGIO"

echo ""
echo "🔄 4. STATO SISTEMA:"
echo "-------------------"
./quantum_commands.sh status | grep -E "(Trader|Portfolio|Ciclo)"
