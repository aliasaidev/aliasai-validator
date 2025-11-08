#!/bin/bash
# Environment configuration checker

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "🔍 Environment Configuration Checker"
echo "====================================="
echo ""

# Load .env file
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo ""
    echo "💡 Create .env from template:"
    echo "   cp .env.example .env"
    exit 1
fi

# Source .env
set -a
source .env
set +a

# Check required variables
REQUIRED_VARS=(
    "ERC8004_RPC_URL"
    "ERC8004_VALIDATION_REGISTRY"
    "ERC8004_STAKING_VALIDATOR"
    "ERC8004_STAKE_TOKEN"
    "ERC8004_ADMIN_PRIVATE_KEY"
)

MISSING=0

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Missing: $var"
        MISSING=1
    else
        # Mask private key
        if [[ "$var" == *"PRIVATE_KEY"* ]]; then
            echo "✅ $var: ${!var:0:10}...${!var: -10}"
        else
            echo "✅ $var: ${!var}"
        fi
    fi
done

echo ""

if [ $MISSING -eq 1 ]; then
    echo "❌ Configuration incomplete!"
    echo ""
    echo "💡 Please edit .env and fill in all required values"
    exit 1
else
    echo "🎉 Configuration looks good!"
    echo ""
    echo "📋 Test parameters:"
    echo "   Agent ID: ${ERC8004_DEFAULT_AGENT_ID:-377}"
    echo "   Chain ID: ${ERC8004_CHAIN_ID:-11155111}"
fi
