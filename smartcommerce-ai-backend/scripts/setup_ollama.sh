#!/bin/bash

# Setup script for Local AI with Ollama

set -e

echo "🦙 Setting up Local AI (Ollama)..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Installing via Homebrew..."
        if ! command -v brew &> /dev/null; then
             echo "❌ Homebrew not found. Please install Ollama manually: https://ollama.com"
             exit 1
        fi
        brew install ollama
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Installing via install script..."
        curl -fsSL https://ollama.com/install.sh | sh
    else
        echo "Please install Ollama manually from https://ollama.com"
        exit 1
    fi
else
    echo "✅ Ollama is already installed."
fi

# Start Ollama service (if not running)
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama server..."
    # Start in background
    ollama serve &
    OLLAMA_PID=$!
    echo "Waiting for Ollama to start..."
    sleep 5
fi

# Pull the model
MODEL="llama3.2"
echo "⬇️  Pulling model: $MODEL (this may take a while)..."
ollama pull $MODEL

echo "✅ Local AI setup complete!"
echo "   Run 'ollama run $MODEL' to test it interactively."
echo "   The backend is configured to use it automatically."
