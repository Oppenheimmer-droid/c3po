#!/bin/bash

# C3PO Launcher Script
# Usage: ./run.sh [port]
# Default port: 8000

PORT=${1:-8000}

# Kill any process on the port
fuser -k ${PORT}/tcp 2>/dev/null || true

# Set working directory
cd /workspace/project/c3po

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set - Running in offline mode"
fi

echo "🚀 Starting C3PO on port ${PORT}..."

# Start the server
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
