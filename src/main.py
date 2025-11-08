#!/usr/bin/env python3
"""
ERC-8004 Staking Validation System Complete Test Script

Complete test workflow:
1. Environment check (RPC connection, balance check, mint STK)
2. Stake to become a validator (stake 100 STK)
3. Create validation request (requestHash)
4. Submit validation result (earn 10 STK reward)
5. Claim rewards
6. Statistics and verification

Usage:
    python -m src.main
    or
    erc8004-test (if installed)
"""

import os
import sys
import json
import time
import random
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from datetime import datetime

from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv

from .validation_manager import ValidationManager
from .agent_registry import AgentRegistry

# Load environment variables
load_dotenv()


class ValidationTester:
    """ERC-8004 Validation System Tester"""

    def __init__(self):
        self.report = {
            "test_time": datetime.now().isoformat(),
            "stages": {},
            "transactions": []
        }
        self.transactions = []

        # Test parameters
        # Agent ID: either use predefined or will be dynamically registered
        self.agent_id = os.getenv("ERC8004_DEFAULT_AGENT_ID")
        if self.agent_id:
            self.agent_id = int(self.agent_id)
        else:
            self.agent_id = None  # Will register dynamically

        self.stake_amount = Web3.to_wei(100, 'ether')  # 100 ALIAS
        # Use timestamp + random number to ensure requestData uniqueness
        self.request_data = f"Validation test at {datetime.now().isoformat()} - nonce:{random.randint(10000, 99999)}"
        self.response_score = 100  # Validation passed

    def print_header(self, text: str):
        """Print header"""
        print(f"\n{'='*60}")
        print(f"{text}")
        print(f"{'='*60}\n")

    def print_stage(self, stage: int, text: str):
        """Print stage"""
        print(f"\n{'─'*60}")
        print(f"✅ Stage {stage}: {text}")
        print(f"{'─'*60}\n")

    def add_transaction(self, name: str, tx_hash: str):
        """Record transaction"""
        self.transactions.append({
            "name": name,
            "tx_hash": tx_hash,
            "explorer_url": f"https://sepolia.etherscan.io/tx/0x{tx_hash}"
        })
        print(f"   📍 {name} TX: {tx_hash}")
        print(f"   🔗 Etherscan: https://sepolia.etherscan.io/tx/0x{tx_hash}")

    def stage1_environment_check(self) -> ValidationManager:
        """Stage 1: Environment Check"""
        self.print_stage(1, "Environment Check and Preparation")

        # Check environment variables
        required_vars = {
            "ERC8004_RPC_URL": os.getenv("ERC8004_RPC_URL"),
            "ERC8004_VALIDATION_REGISTRY": os.getenv("ERC8004_VALIDATION_REGISTRY"),
            "ERC8004_STAKING_VALIDATOR": os.getenv("ERC8004_STAKING_VALIDATOR"),
            "ERC8004_STAKE_TOKEN": os.getenv("ERC8004_STAKE_TOKEN"),
            "ERC8004_IDENTITY_REGISTRY": os.getenv("ERC8004_IDENTITY_REGISTRY"),
            "ERC8004_ADMIN_PRIVATE_KEY": os.getenv("ERC8004_ADMIN_PRIVATE_KEY")
        }

        missing_vars = [k for k, v in required_vars.items() if not v]
        if missing_vars:
            print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            print(f"\n💡 Please copy .env.example to .env and configure:")
            print(f"   cp .env.example .env")
            print(f"   # Then edit .env with your values")
            sys.exit(1)

        print("✅ Environment variables configured")
        print(f"   ValidationRegistry: {required_vars['ERC8004_VALIDATION_REGISTRY']}")
        print(f"   StakingValidator: {required_vars['ERC8004_STAKING_VALIDATOR']}")
        print(f"   StakeToken: {required_vars['ERC8004_STAKE_TOKEN']}")
        print(f"   IdentityRegistry: {required_vars['ERC8004_IDENTITY_REGISTRY']}")

        # Initialize Manager
        manager = ValidationManager(
            rpc_url=required_vars["ERC8004_RPC_URL"],
            validation_registry=required_vars["ERC8004_VALIDATION_REGISTRY"],
            staking_validator=required_vars["ERC8004_STAKING_VALIDATOR"],
            stake_token=required_vars["ERC8004_STAKE_TOKEN"],
            private_key=required_vars["ERC8004_ADMIN_PRIVATE_KEY"],
            chain_id=int(os.getenv("ERC8004_CHAIN_ID", "11155111"))
        )

        # Check ETH balance
        eth_balance = manager.w3.eth.get_balance(manager.address)
        eth_balance_ether = Web3.from_wei(eth_balance, 'ether')
        print(f"\n💰 Account Balance Check:")
        print(f"   Address: {manager.address}")
        print(f"   ETH Balance: {eth_balance_ether:.6f} ETH")

        if eth_balance == 0:
            print(f"   ⚠️  Insufficient ETH balance, cannot pay gas")
            print(f"   💡 Please get test ETH from Sepolia faucet:")
            print(f"      https://sepoliafaucet.com/")
            sys.exit(1)

        # Check STK balance
        stk_balance = manager.token_contract.functions.balanceOf(manager.address).call()
        stk_balance_ether = Web3.from_wei(stk_balance, 'ether')
        print(f"   STK Balance: {stk_balance_ether:.2f} ALIAS")

        # Mint test tokens if STK is insufficient
        if stk_balance < self.stake_amount:
            print(f"   ⚠️  Insufficient STK balance, minting test tokens...")
            mint_amount = Web3.to_wei(100, 'ether')

            try:
                mint_tx = manager.token_contract.functions.mint(
                    manager.address,
                    mint_amount
                ).build_transaction({
                    'from': manager.address,
                    'nonce': manager.w3.eth.get_transaction_count(manager.address),
                    'gas': 100000,
                    'maxFeePerGas': manager.w3.to_wei(50, 'gwei'),
                    'maxPriorityFeePerGas': manager.w3.to_wei(2, 'gwei'),
                    'chainId': manager.chain_id
                })

                signed_mint = manager.w3.eth.account.sign_transaction(mint_tx, manager.account.key)
                mint_hash = manager.w3.eth.send_raw_transaction(signed_mint.raw_transaction)
                print(f"   📝 Mint TX: {mint_hash.hex()}")

                receipt = manager.w3.eth.wait_for_transaction_receipt(mint_hash, timeout=120)
                if receipt['status'] == 1:
                    print(f"   ✅ Mint successful! Received 100 ALIAS")
                    self.add_transaction("Mint ALIAS", mint_hash.hex())
                else:
                    print(f"   ❌ Mint failed")
                    sys.exit(1)

                # Update balance
                stk_balance = manager.token_contract.functions.balanceOf(manager.address).call()
                stk_balance_ether = Web3.from_wei(stk_balance, 'ether')
                print(f"   New STK Balance: {stk_balance_ether:.2f} ALIAS")

            except Exception as e:
                print(f"   ❌ Mint failed: {e}")
                sys.exit(1)
        else:
            print(f"   ✅ STK balance sufficient")

        self.report["stages"]["stage1_environment"] = {
            "status": "success",
            "account": manager.address,
            "eth_balance": float(eth_balance_ether),
            "stk_balance": float(stk_balance_ether)
        }

        return manager

    def stage2_register_agent(self, required_vars: dict) -> Tuple[int, AgentRegistry]:
        """Stage 2: Register Agent (if not already specified)"""
        # If agent_id already specified, skip registration
        if self.agent_id is not None:
            self.print_stage(2, f"Using Pre-configured Agent ID: {self.agent_id}")
            print(f"   ℹ️  Skipping Agent registration (using ERC8004_DEFAULT_AGENT_ID={self.agent_id})")

            # Still return AgentRegistry for potential verification later
            agent_registry = AgentRegistry(
                rpc_url=required_vars["ERC8004_RPC_URL"],
                contract_address=required_vars["ERC8004_IDENTITY_REGISTRY"],
                private_key=required_vars["ERC8004_ADMIN_PRIVATE_KEY"],
                chain_id=int(os.getenv("ERC8004_CHAIN_ID", "11155111"))
            )

            self.report["stages"]["stage2_register_agent"] = {
                "status": "skipped",
                "agent_id": self.agent_id,
                "reason": "Using pre-configured Agent ID"
            }

            return (self.agent_id, agent_registry)

        # Dynamic Agent registration
        self.print_stage(2, "Register Agent on IdentityRegistry")

        try:
            # Initialize AgentRegistry
            agent_registry = AgentRegistry(
                rpc_url=required_vars["ERC8004_RPC_URL"],
                contract_address=required_vars["ERC8004_IDENTITY_REGISTRY"],
                private_key=required_vars["ERC8004_ADMIN_PRIVATE_KEY"],
                chain_id=int(os.getenv("ERC8004_CHAIN_ID", "11155111"))
            )

            # Generate token URI based on account address
            token_uri = f"https://api.aliasai.io/agent/{agent_registry.address}.json"

            # Prepare metadata
            metadata = [
                {"key": "agentType", "value": "validator"},
                {"key": "createdBy", "value": "aliasai-validator"},
                {"key": "version", "value": "1.0"}
            ]

            # Register Agent
            agent_id, tx_hash = agent_registry.register_agent(
                token_uri=token_uri,
                metadata=metadata,
                wait_for_receipt=True,
                timeout=120
            )

            self.add_transaction("Register Agent", tx_hash)

            # Update instance variable
            self.agent_id = agent_id

            print(f"\n✅ Agent Registration Summary:")
            print(f"   Agent ID: {agent_id}")
            print(f"   Token URI: {token_uri}")
            print(f"   Owner: {agent_registry.address}")

            self.report["stages"]["stage2_register_agent"] = {
                "status": "success",
                "agent_id": agent_id,
                "tx_hash": tx_hash,
                "token_uri": token_uri,
                "owner": agent_registry.address
            }

            return (agent_id, agent_registry)

        except Exception as e:
            print(f"❌ Agent registration failed: {e}")
            self.report["stages"]["stage2_register_agent"] = {
                "status": "failed",
                "error": str(e)
            }
            sys.exit(1)

    def stage3_stake(self, manager: ValidationManager) -> str:
        """Stage 3: Stake to Become Validator"""
        self.print_stage(3, f"Stake {Web3.from_wei(self.stake_amount, 'ether'):.0f} ALIAS to Become Validator")

        try:
            tx_hash = manager.stake_tokens(
                amount=self.stake_amount,
                wait_for_receipt=True,
                timeout=120
            )

            self.add_transaction("Stake STK", tx_hash)

            # Verify staking success
            validator_info = manager.get_validator_info()
            print(f"\n✅ Validator Information:")
            print(f"   Staked Amount: {validator_info['stakedAmountETH']:.0f} ALIAS")
            print(f"   Status: {'✅ Active' if validator_info['isActive'] else '❌ Inactive'}")
            print(f"   Pending Rewards: {validator_info['pendingRewardsETH']:.2f} ALIAS")
            print(f"   Validation Count: {validator_info['validationCount']}")

            self.report["stages"]["stage3_stake"] = {
                "status": "success",
                "tx_hash": tx_hash,
                "staked_amount": float(validator_info['stakedAmountETH']),
                "is_active": validator_info['isActive']
            }

            return tx_hash

        except Exception as e:
            print(f"❌ Staking failed: {e}")
            self.report["stages"]["stage3_stake"] = {
                "status": "failed",
                "error": str(e)
            }
            sys.exit(1)

    def stage4_create_request(self, manager: ValidationManager) -> bytes:
        """Stage 4: Create Validation Request"""
        self.print_stage(4, "Create Validation Request")

        try:
            request_uri = f"https://api.aliasai.io/validation/{self.agent_id}/request"

            request_hash, tx_hash = manager.create_validation_request(
                agent_id=self.agent_id,
                request_uri=request_uri,
                request_data=self.request_data,
                wait_for_receipt=True,
                timeout=120
            )

            self.add_transaction("Create Validation Request", tx_hash)

            print(f"\n✅ Validation Request Created Successfully:")
            print(f"   Agent ID: {self.agent_id}")
            print(f"   Request URI: {request_uri}")
            print(f"   Request Hash: {request_hash.hex()}")

            self.report["stages"]["stage4_create_request"] = {
                "status": "success",
                "tx_hash": tx_hash,
                "request_hash": request_hash.hex(),
                "agent_id": self.agent_id
            }

            return request_hash

        except Exception as e:
            print(f"❌ Create validation request failed: {e}")
            self.report["stages"]["stage4_create_request"] = {
                "status": "failed",
                "error": str(e)
            }
            sys.exit(1)

    def stage5_submit_validation(self, manager: ValidationManager, request_hash: bytes) -> str:
        """Stage 5: Submit Validation Result"""
        self.print_stage(5, "Submit Validation Result")

        try:
            response_uri = f"https://api.aliasai.io/validation/{self.agent_id}/response"
            response_data = f"Validation result: {self.response_score}/100"

            # Query rewards before validation
            validator_info_before = manager.get_validator_info()
            rewards_before = validator_info_before['pendingRewardsETH']

            tx_hash = manager.submit_validation(
                request_hash=request_hash,
                response=self.response_score,
                response_uri=response_uri,
                response_data=response_data,
                tag="test",
                wait_for_receipt=True,
                timeout=120
            )

            self.add_transaction("Submit Validation Result", tx_hash)

            # Query rewards after validation
            validator_info_after = manager.get_validator_info()
            rewards_after = validator_info_after['pendingRewardsETH']
            reward_earned = rewards_after - rewards_before

            print(f"\n✅ Validation Result Submitted Successfully:")
            print(f"   Score: {self.response_score}/100")
            print(f"   Reward: +{reward_earned:.2f} ALIAS")
            print(f"   Total Pending: {rewards_after:.2f} ALIAS")
            print(f"   Validation Count: {validator_info_after['validationCount']}")

            # Query validation status
            validation_status = manager.get_validation_status(request_hash)
            print(f"\n📊 Validation Status:")
            print(f"   Validator: {validation_status['validatorAddress']}")
            print(f"   Agent ID: {validation_status['agentId']}")
            print(f"   Response: {validation_status['response']}/100")

            self.report["stages"]["stage5_submit_validation"] = {
                "status": "success",
                "tx_hash": tx_hash,
                "response": self.response_score,
                "reward_earned": float(reward_earned),
                "validation_count": validator_info_after['validationCount']
            }

            return tx_hash

        except Exception as e:
            print(f"❌ Submit validation failed: {e}")
            self.report["stages"]["stage5_submit_validation"] = {
                "status": "failed",
                "error": str(e)
            }
            sys.exit(1)

    def stage6_claim_rewards(self, manager: ValidationManager) -> str:
        """Stage 6: Claim Rewards"""
        self.print_stage(6, "Claim Rewards")

        try:
            # Query pending rewards
            validator_info_before = manager.get_validator_info()
            pending_rewards = validator_info_before['pendingRewardsETH']

            if pending_rewards == 0:
                print(f"⚠️  No pending rewards")
                self.report["stages"]["stage6_claim_rewards"] = {
                    "status": "skipped",
                    "reason": "No pending rewards"
                }
                return ""

            print(f"💰 Pending Rewards: {pending_rewards:.2f} ALIAS")

            # Query STK balance before claiming
            stk_balance_before = manager.token_contract.functions.balanceOf(manager.address).call()

            tx_hash = manager.claim_rewards(
                wait_for_receipt=True,
                timeout=120
            )

            self.add_transaction("Claim Rewards", tx_hash)

            # Query balance after claiming
            stk_balance_after = manager.token_contract.functions.balanceOf(manager.address).call()
            stk_received = Web3.from_wei(stk_balance_after - stk_balance_before, 'ether')

            validator_info_after = manager.get_validator_info()

            print(f"\n✅ Rewards Claimed Successfully:")
            print(f"   Claimed Amount: {stk_received:.2f} ALIAS")
            print(f"   New STK Balance: {Web3.from_wei(stk_balance_after, 'ether'):.2f} ALIAS")
            print(f"   Remaining Pending: {validator_info_after['pendingRewardsETH']:.2f} ALIAS")

            self.report["stages"]["stage6_claim_rewards"] = {
                "status": "success",
                "tx_hash": tx_hash,
                "claimed_amount": float(stk_received),
                "new_balance": float(Web3.from_wei(stk_balance_after, 'ether'))
            }

            return tx_hash

        except Exception as e:
            print(f"❌ Claim rewards failed: {e}")
            self.report["stages"]["stage6_claim_rewards"] = {
                "status": "failed",
                "error": str(e)
            }
            sys.exit(1)

    def stage7_statistics(self, manager: ValidationManager, agent_registry: Optional[AgentRegistry] = None):
        """Stage 7: Statistics and Verification"""
        self.print_stage(7, "Statistics and Agent Verification")

        try:
            # Query validator information
            validator_info = manager.get_validator_info()
            print(f"📊 Validator Information:")
            print(f"   Staked Amount: {validator_info['stakedAmountETH']:.2f} ALIAS")
            print(f"   Validation Count: {validator_info['validationCount']}")
            print(f"   Pending Rewards: {validator_info['pendingRewardsETH']:.2f} ALIAS")
            print(f"   Status: {'✅ Active' if validator_info['isActive'] else '❌ Inactive'}")

            # Query global statistics
            stats = manager.get_staking_stats()
            print(f"\n📈 Global Statistics:")
            print(f"   Total Staked: {stats['totalStakedETH']:.2f} ALIAS")
            print(f"   Total Rewards: {stats['totalRewardsETH']:.2f} ALIAS")
            print(f"   Total Slashed: {stats['totalSlashedETH']:.2f} ALIAS")

            # Verify Agent information if registry is available
            agent_verification_passed = None
            if agent_registry and self.agent_id is not None:
                print(f"\n🔍 Verifying Agent Information:")
                print(f"   Agent ID: {self.agent_id}")

                try:
                    token_uri = agent_registry.get_token_uri(self.agent_id)
                    print(f"   ✅ Token URI: {token_uri}")

                    expected_metadata = {
                        "agentType": "validator",
                        "createdBy": "aliasai-validator"
                    }
                    agent_verification_passed = agent_registry.verify_agent(self.agent_id, expected_metadata)
                except Exception as e:
                    print(f"   ⚠️  Agent verification skipped: {e}")

            self.report["stages"]["stage7_statistics"] = {
                "status": "success",
                "validator_info": {
                    "staked_amount": float(validator_info['stakedAmountETH']),
                    "validation_count": validator_info['validationCount'],
                    "pending_rewards": float(validator_info['pendingRewardsETH']),
                    "is_active": validator_info['isActive']
                },
                "global_stats": {
                    "total_staked": float(stats['totalStakedETH']),
                    "total_rewards": float(stats['totalRewardsETH']),
                    "total_slashed": float(stats['totalSlashedETH'])
                },
                "agent_verification": agent_verification_passed
            }

        except Exception as e:
            print(f"❌ Query statistics failed: {e}")
            self.report["stages"]["stage7_statistics"] = {
                "status": "failed",
                "error": str(e)
            }

    def run(self):
        """Run Complete Test - 7 Stage Workflow"""
        self.print_header("ERC-8004 Staking Validation System Complete Test (7 Stages)")

        print(f"📋 Test Parameters:")
        print(f"   Agent ID: {self.agent_id if self.agent_id else '(Will register dynamically)'}")
        print(f"   Stake Amount: {Web3.from_wei(self.stake_amount, 'ether'):.0f} ALIAS")
        print(f"   Validation Score: {self.response_score}/100")

        try:
            # Stage 1: Environment Check
            manager = self.stage1_environment_check()

            # Save required_vars for Agent registration
            required_vars = {
                "ERC8004_RPC_URL": os.getenv("ERC8004_RPC_URL"),
                "ERC8004_VALIDATION_REGISTRY": os.getenv("ERC8004_VALIDATION_REGISTRY"),
                "ERC8004_STAKING_VALIDATOR": os.getenv("ERC8004_STAKING_VALIDATOR"),
                "ERC8004_STAKE_TOKEN": os.getenv("ERC8004_STAKE_TOKEN"),
                "ERC8004_IDENTITY_REGISTRY": os.getenv("ERC8004_IDENTITY_REGISTRY"),
                "ERC8004_ADMIN_PRIVATE_KEY": os.getenv("ERC8004_ADMIN_PRIVATE_KEY")
            }

            # Wait to ensure transaction confirmation
            print(f"\n⏳ Waiting 5 seconds for transaction confirmation...")
            time.sleep(5)

            # Stage 2: Register Agent (or skip if already configured)
            agent_id, agent_registry = self.stage2_register_agent(required_vars)

            # Wait to ensure transaction confirmation
            print(f"\n⏳ Waiting 5 seconds for transaction confirmation...")
            time.sleep(5)

            # Stage 3: Stake
            self.stage3_stake(manager)

            # Wait to ensure transaction confirmation
            print(f"\n⏳ Waiting 5 seconds for transaction confirmation...")
            time.sleep(5)

            # Stage 4: Create Validation Request
            request_hash = self.stage4_create_request(manager)

            # Wait to ensure transaction confirmation
            print(f"\n⏳ Waiting 5 seconds for transaction confirmation...")
            time.sleep(5)

            # Stage 5: Submit Validation
            self.stage5_submit_validation(manager, request_hash)

            # Wait to ensure transaction confirmation
            print(f"\n⏳ Waiting 5 seconds for transaction confirmation...")
            time.sleep(5)

            # Stage 6: Claim Rewards
            self.stage6_claim_rewards(manager)

            # Stage 7: Statistics and Agent Verification
            self.stage7_statistics(manager, agent_registry)

            # Print test summary
            self.print_summary()

            # Save report
            self.save_report()

        except KeyboardInterrupt:
            print(f"\n\n⚠️  Test interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def print_summary(self):
        """Print Test Summary"""
        self.print_header("📋 Test Summary")

        print("✅ All stages completed")
        print()
        print("🔗 Transaction Links:")
        for tx in self.transactions:
            print(f"   {tx['name']}: {tx['explorer_url']}")
        print()
        print("📊 Test Results:")
        for stage, data in self.report["stages"].items():
            status_emoji = "✅" if data["status"] == "success" else "❌"
            print(f"   {status_emoji} {stage}: {data['status']}")

    def save_report(self):
        """Save Test Report"""
        report_file = Path("validation_test_report.json")
        self.report["transactions"] = self.transactions

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Test report saved: {report_file.absolute()}")


def main():
    """Main Function"""
    tester = ValidationTester()
    tester.run()


if __name__ == "__main__":
    main()
