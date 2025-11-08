#!/usr/bin/env python3
"""
Simple Usage Example for ERC-8004 Validation Manager

This example demonstrates how to use the ValidationManager
in your own Python scripts.
"""

import os
from web3 import Web3
from dotenv import load_dotenv
from src.validation_manager import ValidationManager

# Load environment variables
load_dotenv()


def main():
    """Simple usage example"""

    print("🚀 ERC-8004 ValidationManager Simple Example\n")

    # Initialize manager
    manager = ValidationManager(
        rpc_url=os.getenv("ERC8004_RPC_URL"),
        validation_registry=os.getenv("ERC8004_VALIDATION_REGISTRY"),
        staking_validator=os.getenv("ERC8004_STAKING_VALIDATOR"),
        stake_token=os.getenv("ERC8004_STAKE_TOKEN"),
        private_key=os.getenv("ERC8004_ADMIN_PRIVATE_KEY"),
        chain_id=int(os.getenv("ERC8004_CHAIN_ID", "11155111"))
    )

    # Example 1: Check validator info
    print("\n📊 Example 1: Check Validator Info")
    print("=" * 50)

    try:
        info = manager.get_validator_info()
        print(f"✅ Validator Status:")
        print(f"   Staked Amount: {info['stakedAmountETH']:.2f} ALIAS")
        print(f"   Active: {info['isActive']}")
        print(f"   Pending Rewards: {info['pendingRewardsETH']:.2f} ALIAS")
        print(f"   Validations: {info['validationCount']}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Example 2: Check global stats
    print("\n📈 Example 2: Check Global Statistics")
    print("=" * 50)

    try:
        stats = manager.get_staking_stats()
        print(f"✅ Global Stats:")
        print(f"   Total Staked: {stats['totalStakedETH']:.2f} ALIAS")
        print(f"   Total Rewards: {stats['totalRewardsETH']:.2f} ALIAS")
        print(f"   Total Slashed: {stats['totalSlashedETH']:.2f} ALIAS")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Example 3: Check token balance
    print("\n💰 Example 3: Check Token Balance")
    print("=" * 50)

    try:
        balance = manager.token_contract.functions.balanceOf(manager.address).call()
        balance_eth = Web3.from_wei(balance, 'ether')
        print(f"✅ ALIAS Balance: {balance_eth:.2f} ALIAS")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n✨ Examples completed!")


if __name__ == "__main__":
    main()
