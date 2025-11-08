"""
ERC-8004 Validation Management Module

Provides staking validation features:
- Stake tokens to become a validator
- Create validation requests
- Submit validation results
- Claim rewards
- Query validation status
"""

import json
import time
from typing import Dict, Optional, Tuple
from pathlib import Path

from web3 import Web3
from web3.contract import Contract
from eth_account import Account


# ValidationRegistry ABI - Copy from compiled contract
VALIDATION_REGISTRY_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "validatorAddress", "type": "address"},
            {"internalType": "uint256", "name": "agentId", "type": "uint256"},
            {"internalType": "string", "name": "requestUri", "type": "string"},
            {"internalType": "bytes32", "name": "requestHash", "type": "bytes32"}
        ],
        "name": "validationRequest",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "requestHash", "type": "bytes32"},
            {"internalType": "uint8", "name": "response", "type": "uint8"},
            {"internalType": "string", "name": "responseUri", "type": "string"},
            {"internalType": "bytes32", "name": "responseHash", "type": "bytes32"},
            {"internalType": "bytes32", "name": "tag", "type": "bytes32"}
        ],
        "name": "validationResponse",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "requestHash", "type": "bytes32"}],
        "name": "getValidationStatus",
        "outputs": [
            {"internalType": "address", "name": "validatorAddress", "type": "address"},
            {"internalType": "uint256", "name": "agentId", "type": "uint256"},
            {"internalType": "uint8", "name": "response", "type": "uint8"},
            {"internalType": "bytes32", "name": "responseHash", "type": "bytes32"},
            {"internalType": "bytes32", "name": "tag", "type": "bytes32"},
            {"internalType": "uint256", "name": "lastUpdate", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# StakingValidator ABI - Simplified version with main functions
STAKING_VALIDATOR_ABI = [
    {
        "inputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}],
        "name": "stake",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "requestUnstake",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "unstake",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "requestHash", "type": "bytes32"},
            {"internalType": "uint8", "name": "response", "type": "uint8"},
            {"internalType": "string", "name": "responseUri", "type": "string"},
            {"internalType": "bytes32", "name": "responseHash", "type": "bytes32"},
            {"internalType": "bytes32", "name": "tag", "type": "bytes32"}
        ],
        "name": "submitValidation",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "claimRewards",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "validator", "type": "address"}],
        "name": "getValidatorInfo",
        "outputs": [
            {"internalType": "uint256", "name": "stake", "type": "uint256"},
            {"internalType": "bool", "name": "active", "type": "bool"},
            {"internalType": "uint256", "name": "rewards", "type": "uint256"},
            {"internalType": "uint256", "name": "validations", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getStats",
        "outputs": [
            {"internalType": "uint256", "name": "_totalStaked", "type": "uint256"},
            {"internalType": "uint256", "name": "_totalRewards", "type": "uint256"},
            {"internalType": "uint256", "name": "_totalSlashed", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# ERC20 ABI - Simplified version
ERC20_ABI = [
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "spender", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "mint",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]


class ValidationManager:
    """
    ERC-8004 Validation Manager

    Core features:
    - Stake tokens to become a validator
    - Create validation requests (Agent owner)
    - Submit validation results (validator)
    - Claim rewards
    - Query validation status

    Usage example:
        >>> manager = ValidationManager(
        ...     rpc_url="https://sepolia.gateway.tenderly.co",
        ...     validation_registry="0x...",
        ...     staking_validator="0x...",
        ...     stake_token="0x...",
        ...     private_key="0x..."
        ... )
        >>> manager.stake_tokens(Web3.to_wei(100, 'ether'))
        >>> manager.submit_validation(request_hash, 100, ...)
    """

    def __init__(
        self,
        rpc_url: str,
        validation_registry: str,
        staking_validator: str,
        stake_token: str,
        private_key: str,
        chain_id: int = 11155111  # Sepolia
    ):
        """
        Initialize Validation Manager

        Args:
            rpc_url: Ethereum RPC node URL
            validation_registry: ValidationRegistry contract address
            staking_validator: StakingValidator contract address
            stake_token: StakeToken contract address
            private_key: Signing account private key
            chain_id: Chain ID
        """
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        # Try to connect multiple times, sometimes needs a bit of time
        for i in range(3):
            if self.w3.is_connected():
                break
            time.sleep(0.5)

        # If still connection failed, try to get chain_id as connection test
        try:
            actual_chain_id = self.w3.eth.chain_id
            if actual_chain_id != chain_id:
                print(f"⚠️ Warning: Chain ID mismatch (expected: {chain_id}, actual: {actual_chain_id})")
        except Exception as e:
            raise ConnectionError(f"Unable to connect to RPC node: {rpc_url}, error: {e}")

        self.chain_id = chain_id

        # Initialize account
        self.account = Account.from_key(private_key)
        self.address = self.account.address

        # Initialize contract instances
        self.validation_contract: Contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(validation_registry),
            abi=VALIDATION_REGISTRY_ABI
        )

        self.staking_contract: Contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(staking_validator),
            abi=STAKING_VALIDATOR_ABI
        )

        self.token_contract: Contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(stake_token),
            abi=ERC20_ABI
        )

        print(f"✅ ValidationManager initialized successfully")
        print(f"   ValidationRegistry: {validation_registry}")
        print(f"   StakingValidator: {staking_validator}")
        print(f"   StakeToken: {stake_token}")
        print(f"   Account Address: {self.address}")

    def stake_tokens(
        self,
        amount: int,
        wait_for_receipt: bool = True,
        timeout: int = 120
    ) -> str:
        """
        Stake tokens to become a validator

        Args:
            amount: Stake amount (wei, 1 STK = 10^18 wei)
            wait_for_receipt: Whether to wait for transaction confirmation
            timeout: Timeout in seconds

        Returns:
            Transaction hash

        Example:
            >>> amount = Web3.to_wei(100, 'ether')  # 100 STK
            >>> tx_hash = manager.stake_tokens(amount)
        """
        print(f"\n🔒 Staking tokens...")
        print(f"   Amount: {Web3.from_wei(amount, 'ether')} STK")

        try:
            # 1. Approve staking contract first
            print(f"📝 Approving StakingValidator contract...")
            approve_tx = self.token_contract.functions.approve(
                self.staking_contract.address,
                amount
            ).build_transaction({
                'from': self.address,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'gas': 100000,
                'maxFeePerGas': self.w3.to_wei(50, 'gwei'),
                'maxPriorityFeePerGas': self.w3.to_wei(2, 'gwei'),
                'chainId': self.chain_id
            })

            signed_approve = self.w3.eth.account.sign_transaction(approve_tx, self.account.key)
            approve_hash = self.w3.eth.send_raw_transaction(signed_approve.raw_transaction)
            print(f"   Approve TX: {approve_hash.hex()}")

            if wait_for_receipt:
                approve_receipt = self.w3.eth.wait_for_transaction_receipt(approve_hash, timeout=timeout)
                if approve_receipt['status'] != 1:
                    raise Exception("Approve transaction failed")

            # 2. Stake
            print(f"💰 Staking tokens...")
            stake_tx = self.staking_contract.functions.stake(amount).build_transaction({
                'from': self.address,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'gas': 300000,
                'maxFeePerGas': self.w3.to_wei(50, 'gwei'),
                'maxPriorityFeePerGas': self.w3.to_wei(2, 'gwei'),
                'chainId': self.chain_id
            })

            signed_stake = self.w3.eth.account.sign_transaction(stake_tx, self.account.key)
            stake_hash = self.w3.eth.send_raw_transaction(signed_stake.raw_transaction)
            stake_hash_hex = stake_hash.hex()
            print(f"   Stake TX: {stake_hash_hex}")

            if wait_for_receipt:
                receipt = self.w3.eth.wait_for_transaction_receipt(stake_hash, timeout=timeout)
                if receipt['status'] != 1:
                    raise Exception("Stake transaction failed")
                print(f"✅ Staking successful! Gas: {receipt['gasUsed']}")

            return stake_hash_hex

        except Exception as e:
            print(f"❌ Staking failed: {e}")
            raise

    def create_validation_request(
        self,
        agent_id: int,
        request_uri: str,
        request_data: str,
        validator_address: Optional[str] = None,
        wait_for_receipt: bool = True,
        timeout: int = 120
    ) -> Tuple[bytes, str]:
        """
        Create validation request (called by Agent owner)

        Args:
            agent_id: Agent ID
            request_uri: Validation request URI
            request_data: Validation request data (for hash calculation)
            validator_address: Specified validator address
            wait_for_receipt: Whether to wait for transaction confirmation
            timeout: Timeout in seconds

        Returns:
            (request_hash, tx_hash): Request hash and transaction hash
        """
        print(f"\n📋 Creating validation request...")
        print(f"   Agent ID: {agent_id}")
        print(f"   Request URI: {request_uri}")

        # Calculate request hash
        request_hash = Web3.keccak(text=request_data)
        print(f"   Request Hash: {request_hash.hex()}")

        validator_addr = Web3.to_checksum_address(validator_address or self.staking_contract.address)
        print(f"   Validator Address: {validator_addr}")

        try:
            nonce = self.w3.eth.get_transaction_count(self.address)

            txn = self.validation_contract.functions.validationRequest(
                validator_addr,
                agent_id,
                request_uri,
                request_hash
            ).build_transaction({
                'from': self.address,
                'nonce': nonce,
                'gas': 500000,
                'maxFeePerGas': self.w3.to_wei(50, 'gwei'),
                'maxPriorityFeePerGas': self.w3.to_wei(2, 'gwei'),
                'chainId': self.chain_id
            })

            signed_txn = self.w3.eth.account.sign_transaction(txn, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            tx_hash_hex = tx_hash.hex()
            print(f"   TX Hash: {tx_hash_hex}")

            if wait_for_receipt:
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
                if receipt['status'] != 1:
                    raise Exception("Transaction execution failed")
                print(f"✅ Validation request created successfully!")

            return (request_hash, tx_hash_hex)

        except Exception as e:
            print(f"❌ Create validation request failed: {e}")
            raise

    def submit_validation(
        self,
        request_hash: bytes,
        response: int,
        response_uri: str,
        response_data: str,
        tag: str = "",
        wait_for_receipt: bool = True,
        timeout: int = 120
    ) -> str:
        """
        Submit validation result (called by validator)

        Args:
            request_hash: Validation request hash
            response: Validation result (0-100)
            response_uri: Validation response URI
            response_data: Validation response data
            tag: Custom tag
            wait_for_receipt: Whether to wait for confirmation
            timeout: Timeout in seconds

        Returns:
            Transaction hash
        """
        print(f"\n✅ Submitting validation result...")
        print(f"   Request Hash: {request_hash.hex()}")
        print(f"   Response: {response}/100")

        if not (0 <= response <= 100):
            raise ValueError(f"Response must be between 0-100, current value: {response}")

        response_hash = Web3.keccak(text=response_data)
        tag_hash = Web3.keccak(text=tag) if tag else b'\x00' * 32

        try:
            nonce = self.w3.eth.get_transaction_count(self.address)

            txn = self.staking_contract.functions.submitValidation(
                request_hash,
                response,
                response_uri,
                response_hash,
                tag_hash
            ).build_transaction({
                'from': self.address,
                'nonce': nonce,
                'gas': 600000,
                'maxFeePerGas': self.w3.to_wei(50, 'gwei'),
                'maxPriorityFeePerGas': self.w3.to_wei(2, 'gwei'),
                'chainId': self.chain_id
            })

            signed_txn = self.w3.eth.account.sign_transaction(txn, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            tx_hash_hex = tx_hash.hex()
            print(f"   TX Hash: {tx_hash_hex}")

            if wait_for_receipt:
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
                if receipt['status'] != 1:
                    raise Exception("Transaction execution failed")
                print(f"✅ Validation result submitted successfully! Gas: {receipt['gasUsed']}")

            return tx_hash_hex

        except Exception as e:
            print(f"❌ Submit validation failed: {e}")
            raise

    def claim_rewards(
        self,
        wait_for_receipt: bool = True,
        timeout: int = 120
    ) -> str:
        """Claim rewards"""
        print(f"\n💰 Claiming rewards...")

        try:
            nonce = self.w3.eth.get_transaction_count(self.address)

            txn = self.staking_contract.functions.claimRewards().build_transaction({
                'from': self.address,
                'nonce': nonce,
                'gas': 250000,
                'maxFeePerGas': self.w3.to_wei(50, 'gwei'),
                'maxPriorityFeePerGas': self.w3.to_wei(2, 'gwei'),
                'chainId': self.chain_id
            })

            signed_txn = self.w3.eth.account.sign_transaction(txn, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            tx_hash_hex = tx_hash.hex()
            print(f"   TX Hash: {tx_hash_hex}")

            if wait_for_receipt:
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
                if receipt['status'] != 1:
                    raise Exception("Transaction execution failed")
                print(f"✅ Rewards claimed successfully! Gas: {receipt['gasUsed']}")

            return tx_hash_hex

        except Exception as e:
            print(f"❌ Claim rewards failed: {e}")
            raise

    def get_validation_status(self, request_hash: bytes) -> Dict:
        """Query validation status"""
        try:
            result = self.validation_contract.functions.getValidationStatus(request_hash).call()

            return {
                "validatorAddress": result[0],
                "agentId": int(result[1]),
                "response": int(result[2]),
                "responseHash": result[3].hex(),
                "tag": result[4].hex(),
                "lastUpdate": int(result[5])
            }
        except Exception as e:
            print(f"❌ Query validation status failed: {e}")
            raise

    def get_validator_info(self, validator_address: Optional[str] = None) -> Dict:
        """Query validator information"""
        addr = validator_address or self.address

        try:
            result = self.staking_contract.functions.getValidatorInfo(addr).call()

            return {
                "stakedAmount": int(result[0]),
                "isActive": result[1],
                "pendingRewards": int(result[2]),
                "validationCount": int(result[3]),
                "stakedAmountETH": Web3.from_wei(result[0], 'ether'),
                "pendingRewardsETH": Web3.from_wei(result[2], 'ether')
            }
        except Exception as e:
            print(f"❌ Query validator information failed: {e}")
            raise

    def get_staking_stats(self) -> Dict:
        """Query staking statistics"""
        try:
            result = self.staking_contract.functions.getStats().call()

            return {
                "totalStaked": int(result[0]),
                "totalRewards": int(result[1]),
                "totalSlashed": int(result[2]),
                "totalStakedETH": Web3.from_wei(result[0], 'ether'),
                "totalRewardsETH": Web3.from_wei(result[1], 'ether'),
                "totalSlashedETH": Web3.from_wei(result[2], 'ether')
            }
        except Exception as e:
            print(f"❌ Query staking statistics failed: {e}")
            raise
