# AliasAI Validator

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Web3.py](https://img.shields.io/badge/web3.py-6.15+-orange.svg)](https://web3py.readthedocs.io/)
[![Ethereum](https://img.shields.io/badge/Ethereum-Sepolia-blue.svg)](https://sepolia.etherscan.io/)
[![BSC](https://img.shields.io/badge/BSC-Ready-yellow.svg)](https://www.bnbchain.org/)

Complete ERC-8004 staking validation system testing toolkit for interacting with validation smart contracts on **Ethereum** and **BNB Smart Chain (BSC)**.

> 🌟 **Multi-Chain Support**: Currently testing on Ethereum Sepolia. Ready for BSC Testnet and will seamlessly support both Ethereum and BSC mainnets when ERC-8004 goes live.

## ✨ Features

- 🔒 **Stake Tokens to Become Validator** - Stake ALIAS tokens to activate validator status
- 📋 **Create Validation Requests** - Agent owners initiate validation requests
- ✅ **Submit Validation Results** - Validators submit scores and earn rewards
- 💰 **Claim Rewards** - Extract accumulated rewards from validation work
- 📊 **Query Statistics** - View validator information and global stats in real-time
- 🌐 **Multi-Chain Ready** - Seamlessly switch between Ethereum and BSC networks with simple configuration

## 🎯 Testing Workflow

This tool implements a complete seven-stage validation workflow:

1. **Environment Check** - RPC connection, balance check, mint test tokens
2. **Register Agent** - Register Agent on IdentityRegistry (or use existing Agent ID)
3. **Stake Tokens** - Stake 100 ALIAS to become a validator via StakingValidator
4. **Create Validation Request** - Generate requestHash with your Agent ID
5. **Submit Validation Result** - Submit score and earn 10 ALIAS reward
6. **Claim Rewards** - Extract accumulated rewards to wallet
7. **Statistics & Verification** - View validator stats and verify Agent information

**✨ Key Features:**
- **Any Private Key Works** - No need for admin privileges
- **Dynamic Agent Registration** - Automatically registers Agent if not specified
- **Complete Staking Integration** - Uses StakingValidator contract
- **Full Chain Verification** - Verifies Agent metadata on-chain

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- UV package manager (recommended) or pip

### Install with UV (Recommended)

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone https://github.com/AliasAI/aliasai-validator.git
cd aliasai-validator

# Sync dependencies
uv sync
```

### Install with pip

```bash
# Clone repository
git clone https://github.com/AliasAI/aliasai-validator.git
cd aliasai-validator

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

## ⚙️ Configuration

### 1. Create Environment Configuration File

```bash
cp .env.example .env
```

### 2. Edit .env File

#### Option A: Ethereum Sepolia Testnet (Current)

```bash
# RPC Configuration
ERC8004_RPC_URL=https://sepolia.gateway.tenderly.co

# Contract Addresses (Sepolia Testnet)
ERC8004_VALIDATION_REGISTRY=0x8004CB39f29c09145F24Ad9dDe2A108C1A2cdfC5
ERC8004_STAKING_VALIDATOR=0x730fb503a2165cf0a31b818522cd15e4611a1fc7
ERC8004_STAKE_TOKEN=0x4f49f864b44f10dd19d80eb0ccf738417122eb04
ERC8004_IDENTITY_REGISTRY=0x8004a6090Cd10A7288092483047B097295Fb8847

# Account Configuration (⚠️ Never commit real private keys!)
ERC8004_ADMIN_PRIVATE_KEY=your_private_key_here_without_0x_prefix

# Test Parameters
# Leave empty to automatically register a new Agent
# Or set an existing Agent ID to use
ERC8004_DEFAULT_AGENT_ID=
ERC8004_CHAIN_ID=11155111
```

#### Option B: BSC Testnet (Coming Soon)

```bash
# RPC Configuration - BSC Testnet
ERC8004_RPC_URL=https://data-seed-prebsc-1-s1.bnbchain.org:8545

# Contract Addresses (BSC Testnet - will be available soon)
ERC8004_VALIDATION_REGISTRY=0x1234567890123456789012345678901234567890
ERC8004_STAKING_VALIDATOR=0x1234567890123456789012345678901234567890
ERC8004_STAKE_TOKEN=0x1234567890123456789012345678901234567890

# Account Configuration (⚠️ Never commit real private keys!)
ERC8004_ADMIN_PRIVATE_KEY=your_private_key_here_without_0x_prefix

# Test Parameters
ERC8004_DEFAULT_AGENT_ID=377
ERC8004_CHAIN_ID=97  # BSC Testnet Chain ID
```

> 💡 **Tip**: Simply update the `ERC8004_RPC_URL` and `ERC8004_CHAIN_ID` to switch between networks. When ERC-8004 launches on mainnet, update to production RPC URLs and contract addresses.

### 3. Get Test Tokens

#### For Ethereum Sepolia:
Get test ETH from Sepolia faucets to pay for gas fees:
- https://sepoliafaucet.com/
- https://www.alchemy.com/faucets/ethereum-sepolia

#### For BSC Testnet:
Get test BNB from BSC testnet faucets:
- https://testnet.bnbchain.org/faucet-smart
- https://testnet.binance.org/faucet-smart

## 🚀 Usage

### Quick Start

```bash
# Run with UV
uv run python -m src.main

# Or run with Python directly
python -m src.main

# If installed as package
erc8004-test
```

### Example Output

```bash
$ uv run python -m src.main

============================================================
ERC-8004 Staking Validation System Complete Test
============================================================

📋 Test Parameters:
   Agent ID: (Will register dynamically)
   Stake Amount: 100 ALIAS
   Validation Score: 100/100

────────────────────────────────────────────────────────────
✅ Stage 1: Environment Check and Preparation
────────────────────────────────────────────────────────────

✅ Environment variables configured
   ValidationRegistry: 0x...
   StakingValidator: 0x...
   StakeToken: 0x...
   IdentityRegistry: 0x...

💰 Account Balance Check:
   Address: 0xYourAddress...
   ETH Balance: 0.500000 ETH
   STK Balance: 200.00 ALIAS
   ✅ STK balance sufficient

────────────────────────────────────────────────────────────
✅ Stage 2: Register Agent on IdentityRegistry
────────────────────────────────────────────────────────────

📝 Preparing to register Agent...
   TokenURI: https://api.aliasai.io/agent/0xYourAddress.json
   Metadata count: 3
     - agentType: validator
     - createdBy: aliasai-validator
     - version: 1.0

✅ Agent registered successfully!
   Agent ID: 1234
   📍 Register Agent TX: 0x...
   🔗 Etherscan: https://sepolia.etherscan.io/tx/0x...

────────────────────────────────────────────────────────────
✅ Stage 3: Stake 100 ALIAS to Become Validator
────────────────────────────────────────────────────────────

🔒 Staking tokens...
   Amount: 100.0 STK
   📍 Stake STK TX: 0x...
   🔗 Etherscan: https://sepolia.etherscan.io/tx/0x...

✅ Validator Information:
   Staked Amount: 100 ALIAS
   Status: ✅ Active
   Pending Rewards: 0.00 ALIAS
   Validation Count: 0

# ... More stage outputs ...

============================================================
📋 Test Summary
============================================================

✅ All stages completed

🔗 Transaction Links:
   Stake STK: https://sepolia.etherscan.io/tx/0x...
   Create Validation Request: https://sepolia.etherscan.io/tx/0x...
   Submit Validation Result: https://sepolia.etherscan.io/tx/0x...
   Claim Rewards: https://sepolia.etherscan.io/tx/0x...

💾 Test report saved: validation_test_report.json
```

## 📖 API Documentation

### ValidationManager Class

Core manager providing all interaction features with ERC-8004 contracts.

#### Initialization

```python
from src.validation_manager import ValidationManager

manager = ValidationManager(
    rpc_url="https://sepolia.gateway.tenderly.co",
    validation_registry="0x...",
    staking_validator="0x...",
    stake_token="0x...",
    private_key="0x...",
    chain_id=11155111
)
```

#### Main Methods

##### stake_tokens()
Stake tokens to become a validator

```python
from web3 import Web3

amount = Web3.to_wei(100, 'ether')  # 100 ALIAS
tx_hash = manager.stake_tokens(amount, wait_for_receipt=True)
```

##### create_validation_request()
Create validation request (called by Agent owner)

```python
request_hash, tx_hash = manager.create_validation_request(
    agent_id=377,
    request_uri="https://api.example.com/validation/377/request",
    request_data="Validation request data",
    wait_for_receipt=True
)
```

##### submit_validation()
Submit validation result (called by validator)

```python
tx_hash = manager.submit_validation(
    request_hash=request_hash,
    response=100,  # Score 0-100
    response_uri="https://api.example.com/validation/377/response",
    response_data="Validation result data",
    tag="test",
    wait_for_receipt=True
)
```

##### claim_rewards()
Claim rewards

```python
tx_hash = manager.claim_rewards(wait_for_receipt=True)
```

##### get_validator_info()
Query validator information

```python
info = manager.get_validator_info()
print(f"Staked: {info['stakedAmountETH']} ALIAS")
print(f"Pending Rewards: {info['pendingRewardsETH']} ALIAS")
print(f"Validations: {info['validationCount']}")
```

##### get_staking_stats()
Query global statistics

```python
stats = manager.get_staking_stats()
print(f"Total Staked: {stats['totalStakedETH']} ALIAS")
print(f"Total Rewards: {stats['totalRewardsETH']} ALIAS")
```

## 📊 Test Report

After test completion, a `validation_test_report.json` file is generated containing:

```json
{
  "test_time": "2025-10-31T10:30:00.000000",
  "stages": {
    "stage1_environment": {
      "status": "success",
      "account": "0x...",
      "eth_balance": 0.5,
      "stk_balance": 200.0
    },
    "stage2_stake": {
      "status": "success",
      "tx_hash": "0x...",
      "staked_amount": 100.0,
      "is_active": true
    }
    // ... other stages
  },
  "transactions": [
    {
      "name": "Stake STK",
      "tx_hash": "0x...",
      "explorer_url": "https://sepolia.etherscan.io/tx/0x..."
    }
    // ... other transactions
  ]
}
```

## 🔧 Troubleshooting

### Common Issues

#### 1. RPC Connection Failed
```
❌ Unable to connect to RPC node
```

**Solution:**
- Check `ERC8004_RPC_URL` configuration
- Try other RPC nodes (Alchemy, Infura)
- Verify network connection

#### 2. Insufficient ETH Balance
```
❌ Insufficient ETH balance, cannot pay gas
```

**Solution:**
- Get test ETH from Sepolia faucets
- Verify account address is correct

#### 3. Invalid Private Key Format
```
❌ Invalid private key
```

**Solution:**
- Private key should be a 64-character hexadecimal string
- Do not include `0x` prefix
- Example: `abcd1234...` (64 characters)

#### 4. Incorrect Contract Address
```
❌ Transaction execution failed
```

**Solution:**
- Verify all contract addresses are correct
- Confirm using the correct testnet (Sepolia)

## 🛡️ Security Notes

⚠️ **Important:**
- **Never** commit `.env` file to version control
- **Never** use mainnet private keys in `.env`
- **For testnet only**, test tokens have no real value
- Use dedicated test accounts, not accounts holding real assets

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌐 Multi-Chain Support

### Supported Networks

| Network | Status | Chain ID | RPC Endpoint | Explorer |
|---------|--------|----------|--------------|----------|
| Ethereum Sepolia | ✅ Active | 11155111 | https://sepolia.gateway.tenderly.co | https://sepolia.etherscan.io/ |
| BSC Testnet | 🔄 Coming Soon | 97 | https://data-seed-prebsc-1-s1.bnbchain.org:8545 | https://testnet.bscscan.com/ |
| Ethereum Mainnet | 🚀 Post ERC-8004 Launch | 1 | https://mainnet.infura.io/v3/YOUR-KEY | https://etherscan.io/ |
| BSC Mainnet | 🚀 Post ERC-8004 Launch | 56 | https://bsc-dataseed.bnbchain.org | https://bscscan.com/ |

### RPC Provider Recommendations

#### Ethereum
- **Public RPC**: Tenderly Gateway, Ankr, Public Node
- **Premium RPC**: Alchemy, Infura, QuickNode
- **Best for Production**: Use premium providers for reliability and rate limits

#### BSC (BNB Smart Chain)
- **Public RPC**: BNB Chain Official RPC, NodeReal, Ankr
- **Premium RPC**: NodeReal MegaNode, QuickNode, GetBlock
- **Best for Production**: BNB Chain official nodes or premium providers

> 🎯 **Mainnet Ready**: Once ERC-8004 contracts are deployed on Ethereum and BSC mainnets, you can immediately start using this tool by simply updating the RPC URLs and contract addresses in your `.env` file. No code changes required!

## 🔗 Related Resources

- [ERC-8004 Standard](https://eips.ethereum.org/EIPS/eip-8004)
- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [Sepolia Etherscan](https://sepolia.etherscan.io/)
- [Ethereum Testnet Faucets](https://sepoliafaucet.com/)
- [BSC Official Website](https://www.bnbchain.org/)
- [BSC Developer Docs](https://docs.bnbchain.org/)
- [BscScan Explorer](https://bscscan.com/)

## 💬 Support

For questions or suggestions:
- Open an [Issue](https://github.com/AliasAI/aliasai-validator/issues)
- Check the [Documentation](docs/)
- Contact maintainers

## 🙏 Acknowledgments

- ERC-8004 standard authors
- Web3.py development team
- Ethereum community

---

**Made with ❤️ by Alias AI Team**
