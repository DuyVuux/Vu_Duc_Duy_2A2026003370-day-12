#!/bin/bash
pkill -9 -f 'python -m app.main' || true
sleep 1
export HOST=0.0.0.0
export PORT=8086
export JWT_SECRET="dev-jwt-secret"
export AGENT_API_KEY="dev-key-change-me"

export IP_WHITELIST="8.8.8.8"
python -m app.main > server_log_test4.txt 2>&1 &
PID=$!
sleep 2

echo -e "\n=== BLOCK 8.8.8.8 ===" > out4.txt
curl -i http://localhost:8086/health >> out4.txt 2>&1

kill -9 $PID
wait $PID 2>/dev/null || true
