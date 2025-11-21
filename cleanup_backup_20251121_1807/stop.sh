#!/bin/bash
if [ "$1" = "force" ]; then
    pkill -f "python3"
else
    ./quantum_v31_commands.sh stop
fi
