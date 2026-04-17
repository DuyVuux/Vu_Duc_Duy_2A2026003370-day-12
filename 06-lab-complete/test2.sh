#!/bin/bash
unset IP_WHITELIST
export HOST=0.0.0.0
export PORT=8086
export JWT_SECRET="dev-jwt-secret"
export AGENT_API_KEY="dev-key-change-me"

python -m app.main > server_log_test.txt 2>&1 &
PID=$!
sleep 2

curl -i http://localhost:8086/health > out.txt 2>&1
echo -e "\n=== HEADERS ===" >> out.txt
curl -I http://localhost:8086/health >> out.txt 2>&1

kill $PID
wait $PID 2>/dev/null || true
sleep 1

export IP_WHITELIST="8.8.8.8"
python -m app.main > server_log_test.txt 2>&1 &
PID=$!
sleep 2

echo -e "\n=== BLOCK 8.8.8.8 ===" >> out.txt
curl -i http://localhost:8086/health >> out.txt 2>&1

kill $PID
wait $PID 2>/dev/null || true
pkill -f 'python -m app.main' || true
