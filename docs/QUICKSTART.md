# Quick Start Guide

## Get Started with ERC-8004 Validation Testing in 5 Minutes

### Step 1: Install Dependencies

```bash
# Using UV (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
cd aliasai-validator
uv sync

# Or using pip
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Step 2: Configure Environment

```bash
# Copy configuration template
cp .env.example .env

# Edit .env file
nano .env  # Or use your favorite editor
```

**Required Fields:**

```bash
# RPC URL (free public node)
ERC8004_RPC_URL=https://sepolia.gateway.tenderly.co

# Contract addresses (obtain from project team)
ERC8004_VALIDATION_REGISTRY=0x...
ERC8004_STAKING_VALIDATOR=0x...
ERC8004_STAKE_TOKEN=0x...

# Your test private key (never use mainnet account!)
ERC8004_ADMIN_PRIVATE_KEY=abc123...  # 64-character hex, no 0x prefix
```

### Step 3: Get Test ETH

Visit any Sepolia faucet:
- https://sepoliafaucet.com/
- https://www.alchemy.com/faucets/ethereum-sepolia

Enter your wallet address to receive 0.5 ETH test tokens.

### Step 4: Run Test

```bash
# Using UV
uv run python -m src.main

# Or using Python
python -m src.main
```

### Expected Output

```
============================================================
ERC-8004 Staking Validation System Complete Test
============================================================

📋 Test Parameters:
   Agent ID: 377
   Stake Amount: 100 ALIAS
   Validation Score: 100/100

────────────────────────────────────────────────────────────
✅ Stage 1: Environment Check and Preparation
────────────────────────────────────────────────────────────

✅ Environment variables configured
💰 Account Balance Check:
   Address: 0xYourAddress...
   ETH Balance: 0.500000 ETH
   STK Balance: 0.00 ALIAS
   ⚠️  Insufficient STK balance, minting test tokens...
   ✅ Mint successful! Received 100 ALIAS

# ... Execute 6 test stages ...

============================================================
📋 Test Summary
============================================================

✅ All stages completed

🔗 Transaction Links:
   Mint ALIAS: https://sepolia.etherscan.io/tx/0x...
   Stake STK: https://sepolia.etherscan.io/tx/0x...
   Create Validation Request: https://sepolia.etherscan.io/tx/0x...
   Submit Validation Result: https://sepolia.etherscan.io/tx/0x...
   Claim Rewards: https://sepolia.etherscan.io/tx/0x...

💾 Test report saved: validation_test_report.json
```

### Step 5: View Test Report

```bash
# View JSON report
cat validation_test_report.json

# Or use jq for formatting
jq . validation_test_report.json
```

## Quick Troubleshooting

### Q: "Unable to connect to RPC node" error
**A:** Check if `ERC8004_RPC_URL` is correct, try switching RPC nodes.

### Q: "Insufficient ETH balance" error
**A:** Get test ETH from Sepolia faucets.

### Q: "Missing environment variables" error
**A:** Confirm `.env` file exists and contains all required fields.

### Q: Transaction failed or timeout
**A:** Sepolia network may be congested, wait a few minutes and retry.

## Next Steps

- 📖 Read the complete [API Documentation](../README.md#-api-documentation)
- 🔧 Customize test parameters (modify `ERC8004_DEFAULT_AGENT_ID` etc. in `.env`)
- 💻 Integrate into your project (see [examples/](../examples/))

## Need Help?

- View [Complete Documentation](../README.md)
- Open an [Issue](https://github.com/AliasAI/aliasai-validator/issues)
- Contact maintainers
