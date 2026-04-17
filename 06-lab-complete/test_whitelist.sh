#!/bin/bash
pkill -f 'python -m app.main' || true
sleep 1
unset IP_WHITELIST
export HOST=0.0.0.0
export PORT=8086
export JWT_SECRET="dev-jwt-secret"
export AGENT_API_KEY="dev-key-change-me"
python -m app.main > server_log.txt 2>&1 &
PID=$!
sleep 3

echo "=== TEST NO WHITELIST ==="
curl -s http://localhost:8086/health

echo -e "\n=== TEST GET HEADERS ==="
curl -s -I http://localhost:8086/health

kill $PID
wait $PID 2>/dev/null || true
pkill -f 'python -m app.main' || true
sleep 1

export IP_WHITELIST="127.0.0.1"
python -m app.main > server_log.txt 2>&1 &
PID=$!
sleep 3

echo -e "\n=== TEST WHITELIST = 127.0.0.1 ==="
curl -s http://localhost:8086/health

kill $PID
wait $PID 2>/dev/null || true
pkill -f 'python -m app.main' || true
sleep 1

export IP_WHITELIST="8.8.8.8"
python -m app.main > server_log.txt 2>&1 &
PID=$!
sleep 3
echo -e "\n=== TEST WHITELIST = 8.8.8.8 ==="
curl -s http://localhost:8086/health || echo "Failed"

kill $PID
wait $PID 2>/dev/null || true
pkill -f 'python -m app.main' || true
