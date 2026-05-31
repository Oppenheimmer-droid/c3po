#!/bin/bash

# C3PO - AI Tutor Platform Startup Script

set -e

echo "======================================"
echo "🚀 C3PO - AI Tutor Platform"
echo "======================================"

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --quiet fastapi uvicorn pydantic pydantic-settings httpx openai chromadb

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set. Running in OFFLINE mode."
    echo "    To enable AI responses, set: export OPENAI_API_KEY=sk-..."
fi

# Start the server
echo "🚀 Starting server at http://localhost:8000"
echo "   UI: http://localhost:8000/ui"
echo "   API: http://localhost:8000/api/v1"
echo ""
echo "Press Ctrl+C to stop"
echo "======================================"

# Start uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
