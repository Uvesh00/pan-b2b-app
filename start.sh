#!/usr/bin/env bash
# Startup script for Pan & Tobacco B2B Wholesale App
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

PORT="${1:-8080}"
echo "Starting Pan B2B Web App on port $PORT..."
python3 server.py "$PORT"
