#!/usr/bin/env bash
# Instant Free Public Live Tunnel for Pan & Tobacco Wholesale App
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

PORT="${1:-8080}"

# 1. Check if server is running, if not start it
if ! curl -s "http://127.0.0.1:$PORT/api/config" > /dev/null 2>&1; then
    echo "Starting local server on port $PORT..."
    python3 server.py "$PORT" > server.log 2>&1 &
    sleep 2
fi

echo "================================================================"
echo " Starting Free Public Live Tunnel via localhost.run..."
echo " Opening your webapp to the world on HTTPS..."
echo "================================================================"
ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -R 80:localhost:$PORT nokey@localhost.run
