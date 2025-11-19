#!/bin/bash
# Quick setup script for Diplomacy LLM

echo "Diplomacy LLM Setup"
echo "==================="
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found"
    exit 1
fi

echo "✓ Python 3 found"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f .env ]; then
    echo ""
    echo "⚠ No .env file found"
    echo ""
    echo "Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "Please edit .env and add your Gemini API key:"
    echo "  GEMINI_API_KEY=your_key_here"
    echo ""
    echo "Get your API key from: https://aistudio.google.com/app/apikey"
else
    echo "✓ .env file exists"
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Make sure your API key is in .env"
echo "  2. Update game_history.md files with initial game state"
echo "  3. Run: python diplomacy.py status"
echo "  4. Start playing: python diplomacy.py france"
echo ""
