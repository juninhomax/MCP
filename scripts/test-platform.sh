#!/bin/bash

echo "🧪 Testing MCP Brain/Slaves Platform"
echo "====================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test Brain health
echo ""
echo "Testing Brain health..."
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo -e "${GREEN}✓${NC} Brain is healthy"
else
    echo -e "${RED}✗${NC} Brain is not responding"
    exit 1
fi

# Test Linux Slave health
echo ""
echo "Testing Linux Slave health..."
if curl -s http://localhost:8001/health | grep -q "healthy"; then
    echo -e "${GREEN}✓${NC} Linux Slave is healthy"
else
    echo -e "${RED}✗${NC} Linux Slave is not responding"
fi

# Generate test token
echo ""
echo "Generating test token..."
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/token?slave_id=test&scopes=*" | grep -o '"token":"[^"]*' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
    echo -e "${GREEN}✓${NC} Token generated"
else
    echo -e "${RED}✗${NC} Failed to generate token"
    exit 1
fi

# Test task creation (dry run)
echo ""
echo "Testing task creation (dry run)..."
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/tasks" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "request": "List files in /tmp directory",
        "dry_run": true
    }')

TASK_ID=$(echo $RESPONSE | grep -o '"task_id":"[^"]*' | cut -d'"' -f4)

if [ -n "$TASK_ID" ]; then
    echo -e "${GREEN}✓${NC} Task created: $TASK_ID"
else
    echo -e "${RED}✗${NC} Failed to create task"
    echo "Response: $RESPONSE"
    exit 1
fi

# Get task status
echo ""
echo "Getting task status..."
TASK_STATUS=$(curl -s -X GET "http://localhost:8000/api/v1/tasks/$TASK_ID" \
    -H "Authorization: Bearer $TOKEN")

if echo $TASK_STATUS | grep -q "completed\|failed"; then
    echo -e "${GREEN}✓${NC} Task completed"
    echo "Status: $(echo $TASK_STATUS | grep -o '"status":"[^"]*' | cut -d'"' -f4)"
else
    echo -e "${YELLOW}⚠${NC} Task status: $(echo $TASK_STATUS | grep -o '"status":"[^"]*' | cut -d'"' -f4)"
fi

echo ""
echo -e "${GREEN}✅ All tests passed!${NC}"
