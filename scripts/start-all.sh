#!/bin/bash

echo "🚀 Starting MCP Brain/Slaves Platform"
echo "======================================"

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Warning: Ollama is not running. Please start Ollama first."
    echo "   Run: ollama serve"
    exit 1
fi

# Start MCP Brain
echo ""
echo "📡 Starting MCP Brain..."
cd brain
source venv/bin/activate 2>/dev/null || python -m venv venv && source venv/bin/activate
pip install -q -r requirements.txt
python main.py &
BRAIN_PID=$!
echo "   Brain started (PID: $BRAIN_PID)"
cd ..

# Wait for brain to be ready
echo "   Waiting for Brain to be ready..."
sleep 5

# Generate tokens
echo ""
echo "🔑 Generating authentication tokens..."
LINUX_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/token?slave_id=linux-slave-01&scopes=*" | grep -o '"token":"[^"]*' | cut -d'"' -f4)
WINDOWS_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/token?slave_id=windows-slave-01&scopes=*" | grep -o '"token":"[^"]*' | cut -d'"' -f4)

if [ -n "$LINUX_TOKEN" ]; then
    echo "   Linux token generated"
    echo "AUTH_TOKEN=$LINUX_TOKEN" >> slaves/linux/.env
else
    echo "   ⚠️  Failed to generate Linux token"
fi

if [ -n "$WINDOWS_TOKEN" ]; then
    echo "   Windows token generated"
    echo "AUTH_TOKEN=$WINDOWS_TOKEN" >> slaves/windows/.env
else
    echo "   ⚠️  Failed to generate Windows token"
fi

# Start Linux Slave
echo ""
echo "🐧 Starting Linux Slave..."
cd slaves/linux
source venv/bin/activate 2>/dev/null || python -m venv venv && source venv/bin/activate
pip install -q -r requirements.txt
python main.py &
LINUX_PID=$!
echo "   Linux Slave started (PID: $LINUX_PID)"
cd ../..

echo ""
echo "✅ Platform started successfully!"
echo ""
echo "Services:"
echo "  - MCP Brain:    http://localhost:8000"
echo "  - Linux Slave:  http://localhost:8001"
echo ""
echo "To stop all services, run: ./scripts/stop-all.sh"
echo ""
echo "PIDs saved to .pids file"
echo "$BRAIN_PID" > .pids
echo "$LINUX_PID" >> .pids
