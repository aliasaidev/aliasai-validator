#!/bin/bash
# Quick test runner script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "🚀 ERC-8004 Validation Tester"
echo "=============================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo ""
    echo "💡 Please create .env file:"
    echo "   cp .env.example .env"
    echo "   # Then edit .env with your configuration"
    echo ""
    exit 1
fi

# Check if UV is installed
if command -v uv &> /dev/null; then
    echo "✅ Using UV package manager"
    uv run python -m src.main "$@"
else
    echo "✅ Using Python directly"
    python -m src.main "$@"
fi
