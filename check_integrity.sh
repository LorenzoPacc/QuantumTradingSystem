#!/bin/bash
echo "🔍 CHECK INTEGRITÀ SISTEMA"
ps aux | grep -E "(quantum|python)" | grep -v grep
ls -lth *state*.json | head -3
