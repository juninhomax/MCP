#!/bin/bash

echo "🛑 Stopping MCP Brain/Slaves Platform"
echo "======================================"

if [ -f .pids ]; then
    while read pid; do
        if ps -p $pid > /dev/null 2>&1; then
            echo "Stopping process $pid..."
            kill $pid
        fi
    done < .pids
    rm .pids
    echo "✅ All services stopped"
else
    echo "⚠️  No .pids file found. Searching for processes..."
    pkill -f "python main.py"
    echo "✅ Killed all matching processes"
fi
