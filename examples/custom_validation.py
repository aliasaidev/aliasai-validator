#!/usr/bin/env python3
"""
Custom Validation Example

This example shows how to customize the validation process
with your own parameters and logic.
"""

import os
import random
from datetime import datetime
from web3 import Web3
from dotenv import load_dotenv
from src.validation_manager import ValidationManager

load_dotenv()


def custom_validation_workflow(
    agent_id: int = 377,
    stake_amount_eth: float = 100.0,
    validation_score: int = 85
):
    """
    Custom validation workflow with configurable parameters

    Args:
        agent_id: Target agent ID
        stake_amount_eth: Amount to stake (in ALIAS)
        validation_score: Validation score (0-100)
    """

    print(f"\n🎯 Custom Validation Workflow")
    print(f"=" * 60)
    print(f"Agent ID: {agent_id}")
    print(f"Stake Amount: {stake_amount_eth} ALIAS")
    print(f"Score: {validation_score}/100")
    print(f"=" * 60)

    # Initialize manager
    manager = ValidationManager(
        rpc_url=os.getenv("ERC8004_RPC_URL"),
        validation_registry=os.getenv("ERC8004_VALIDATION_REGISTRY"),
        staking_validator=os.getenv("ERC8004_STAKING_VALIDATOR"),
        stake_token=os.getenv("ERC8004_STAKE_TOKEN"),
        private_key=os.getenv("ERC8004_ADMIN_PRIVATE_KEY"),
        chain_id=int(os.getenv("ERC8004_CHAIN_ID", "11155111"))
    )

    try:
        # Step 1: Create validation request
        print("\n📋 Step 1: Creating validation request...")

        request_data = f"Custom validation at {datetime.now().isoformat()} - nonce:{random.randint(1000, 9999)}"
        request_uri = f"https://api.aliasai.io/validation/{agent_id}/request"

        request_hash, tx_hash = manager.create_validation_request(
            agent_id=agent_id,
            request_uri=request_uri,
            request_data=request_data,
            wait_for_receipt=True
        )

        print(f"✅ Request created!")
        print(f"   Request Hash: {request_hash.hex()}")
        print(f"   TX: https://sepolia.etherscan.io/tx/{tx_hash}")

        # Step 2: Submit validation
        print("\n✅ Step 2: Submitting validation result...")

        response_uri = f"https://api.aliasai.io/validation/{agent_id}/response"
        response_data = f"Validation result: {validation_score}/100 - Custom workflow"

        # Check rewards before
        info_before = manager.get_validator_info()
        rewards_before = info_before['pendingRewardsETH']

        tx_hash = manager.submit_validation(
            request_hash=request_hash,
            response=validation_score,
            response_uri=response_uri,
            response_data=response_data,
            tag="custom",
            wait_for_receipt=True
        )

        # Check rewards after
        info_after = manager.get_validator_info()
        rewards_after = info_after['pendingRewardsETH']
        reward_earned = rewards_after - rewards_before

        print(f"✅ Validation submitted!")
        print(f"   Score: {validation_score}/100")
        print(f"   Reward Earned: +{reward_earned:.2f} ALIAS")
        print(f"   TX: https://sepolia.etherscan.io/tx/{tx_hash}")

        # Step 3: Query validation status
        print("\n📊 Step 3: Querying validation status...")

        status = manager.get_validation_status(request_hash)
        print(f"✅ Validation Status:")
        print(f"   Validator: {status['validatorAddress']}")
        print(f"   Agent ID: {status['agentId']}")
        print(f"   Response: {status['response']}/100")
        print(f"   Last Update: {status['lastUpdate']}")

        print(f"\n🎉 Custom validation workflow completed successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Example 1: Default parameters
    custom_validation_workflow()

    # Example 2: Custom parameters
    # custom_validation_workflow(
    #     agent_id=379,
    #     stake_amount_eth=50.0,
    #     validation_score=95
    # )
