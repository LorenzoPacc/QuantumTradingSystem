#!/bin/bash
if [ "$1" = "original" ]; then
    python3 quantum_v3_enhanced.py --dry-run
else
    python3 quantum_v31_wrapper.py --dry-run
fi
