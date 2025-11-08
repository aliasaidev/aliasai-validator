"""
ERC-8004 Agent Registry Management Module

Provides interaction features with ERC-8004 IdentityRegistry contract:
- Agent registration (with tokenURI and metadata)
- Agent metadata query
- Agent URI updates
"""

import json
import time
import warnings
from typing import Dict, List, Tuple, Optional
from pathlib import Path

from web3 import Web3
from web3.contract import Contract
from web3.exceptions import ContractLogicError
from eth_account import Account

# Suppress MismatchedABI warnings from other contracts' events in the same transaction
warnings.filterwarnings("ignore", message=".*MismatchedABI.*")


# Load contract ABI
ABI_PATH = Path(__file__).parent / "abi" / "IdentityRegistry.json"
with open(ABI_PATH, "r") as f:
    IDENTITY_REGISTRY_ABI = json.load(f)


class AgentRegistry:
    """
    ERC-8004 Agent Registry Manager

    Uses Web3.py to interact with IdentityRegistry contract, providing:
    - Register Agent (auto-parse agentId from events)
    - Query on-chain metadata
    - Update Agent URI

    Usage example:
        >>> registry = AgentRegistry(
        ...     rpc_url="https://sepolia.gateway.tenderly.co",
        ...     contract_address="0x8004a6090Cd10A7288092483047B097295Fb8847",
        ...     private_key="0x..."
        ... )
        >>> agent_id, tx_hash = registry.register_agent(
        ...     token_uri="https://api.aliasai.io/agent/0x123.json",
        ...     metadata=[
        ...         {"key": "agentType", "value": "validator"},
        ...         {"key": "createdBy", "value": "aliasai-validator"}
        ...     ]
        ... )
        >>> print(f"Agent registered! ID: {agent_id}, TX: {tx_hash}")
    """

    def __init__(
        self,
        rpc_url: str,
        contract_address: str,
        private_key: str,
        chain_id: int = 11155111,  # Sepolia default
        gas_limit: int = 500000,
        max_priority_fee_per_gas: int = 2_000_000_000,  # 2 gwei
        max_fee_per_gas: int = 50_000_000_000  # 50 gwei
    ):
        """
        Initialize Agent Registry Manager

        Args:
            rpc_url: Ethereum RPC node URL
            contract_address: IdentityRegistry contract address
            private_key: Signing account private key
            chain_id: Chain ID (Sepolia=11155111, Mainnet=1)
            gas_limit: Gas limit (default 500k)
            max_priority_fee_per_gas: Max priority fee (default 2 gwei)
            max_fee_per_gas: Max gas fee (default 50 gwei)
        """
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

        # Try to connect multiple times
        for i in range(3):
            if self.w3.is_connected():
                break
            time.sleep(0.5)

        # If still connection failed, verify by getting chain_id
        try:
            actual_chain_id = self.w3.eth.chain_id
            if actual_chain_id != chain_id:
                print(f"⚠️  Warning: Chain ID mismatch (expected: {chain_id}, actual: {actual_chain_id})")
        except Exception as e:
            raise ConnectionError(f"Unable to connect to RPC node: {rpc_url}, error: {e}")

        self.chain_id = chain_id
        self.gas_limit = gas_limit
        self.max_priority_fee_per_gas = max_priority_fee_per_gas
        self.max_fee_per_gas = max_fee_per_gas

        # Initialize account
        self.account = Account.from_key(private_key)
        self.address = self.account.address

        # Initialize contract instance
        self.contract: Contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=IDENTITY_REGISTRY_ABI
        )

        print(f"✅ AgentRegistry initialized successfully")
        print(f"   IdentityRegistry: {contract_address}")
        print(f"   Account Address: {self.address}")

    def register_agent(
        self,
        token_uri: str,
        metadata: List[Dict[str, str]],
        wait_for_receipt: bool = True,
        timeout: int = 120
    ) -> Tuple[int, str]:
        """
        Register Agent on-chain

        Args:
            token_uri: Agent metadata URI (e.g., https://api.aliasai.io/agent/0x123.json)
            metadata: Metadata list [{"key": "agentType", "value": "validator"}, ...]
            wait_for_receipt: Whether to wait for transaction confirmation
            timeout: Wait timeout (seconds)

        Returns:
            (agent_id, tx_hash): Agent ID and transaction hash

        Raises:
            ContractLogicError: Contract execution failed
            TimeoutError: Transaction confirmation timeout
        """
        print(f"\n📝 Preparing to register Agent...")
        print(f"   TokenURI: {token_uri}")
        print(f"   Metadata count: {len(metadata)}")

        # Convert metadata format: string value to bytes
        formatted_metadata = []
        for item in metadata:
            key = item["key"]
            value = item["value"]
            # Convert string to bytes (UTF-8 encoding)
            value_bytes = value.encode('utf-8') if isinstance(value, str) else value
            formatted_metadata.append((key, value_bytes))
            print(f"     - {key}: {value}")

        # Build transaction
        try:
            # Get nonce
            nonce = self.w3.eth.get_transaction_count(self.address)

            # Call register function
            txn = self.contract.functions.register(
                token_uri,
                formatted_metadata
            ).build_transaction({
                'from': self.address,
                'nonce': nonce,
                'gas': self.gas_limit,
                'maxFeePerGas': self.max_fee_per_gas,
                'maxPriorityFeePerGas': self.max_priority_fee_per_gas,
                'chainId': self.chain_id
            })

            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(txn, self.account.key)

            # Send transaction
            print(f"\n📤 Sending transaction...")
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            tx_hash_hex = tx_hash.hex()
            print(f"   TX Hash: {tx_hash_hex}")

            if not wait_for_receipt:
                return (0, tx_hash_hex)  # Don't wait for confirmation, return agentId=0

            # Wait for transaction confirmation
            print(f"⏳ Waiting for transaction confirmation (max {timeout} seconds)...")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)

            if receipt['status'] != 1:
                raise ContractLogicError("Transaction execution failed (status=0)")

            # Parse agentId from event logs
            agent_id = self._parse_agent_id_from_receipt(receipt)

            print(f"✅ Agent registered successfully!")
            print(f"   Agent ID: {agent_id}")
            print(f"   Gas Used: {receipt['gasUsed']}")
            print(f"   Block: {receipt['blockNumber']}")

            return (agent_id, tx_hash_hex)

        except ContractLogicError as e:
            print(f"❌ Contract execution failed: {e}")
            raise
        except Exception as e:
            print(f"❌ Transaction failed: {e}")
            raise

    def _parse_agent_id_from_receipt(self, receipt: Dict) -> int:
        """
        Parse agentId from Registered event in transaction receipt

        Args:
            receipt: Transaction receipt

        Returns:
            agent_id: Agent ID
        """
        # Get Registered event definition
        registered_event = self.contract.events.Registered()

        # Parse logs
        logs = registered_event.process_receipt(receipt)

        if not logs:
            raise ValueError("Registered event not found")

        # Return agentId from first event
        agent_id = logs[0]['args']['agentId']
        return int(agent_id)

    def get_metadata(self, agent_id: int, key: str) -> bytes:
        """
        Query Agent on-chain metadata

        Args:
            agent_id: Agent ID
            key: Metadata key (e.g., "agentType")

        Returns:
            Metadata value (bytes format)
        """
        try:
            value = self.contract.functions.getMetadata(agent_id, key).call()
            return value
        except Exception as e:
            print(f"❌ Query metadata failed: {e}")
            raise

    def get_metadata_decoded(self, agent_id: int, key: str) -> str:
        """
        Query and decode Agent metadata to string

        Args:
            agent_id: Agent ID
            key: Metadata key

        Returns:
            Metadata value (UTF-8 decoded string)
        """
        value_bytes = self.get_metadata(agent_id, key)
        if not value_bytes:
            return ""
        try:
            return value_bytes.decode('utf-8')
        except Exception:
            return value_bytes.hex()  # If can't decode to UTF-8, return hex

    def get_token_uri(self, agent_id: int) -> str:
        """
        Query Agent's tokenURI

        Args:
            agent_id: Agent ID

        Returns:
            tokenURI string
        """
        try:
            uri = self.contract.functions.tokenURI(agent_id).call()
            return uri
        except Exception as e:
            print(f"❌ Query tokenURI failed: {e}")
            raise

    def verify_agent(self, agent_id: int, expected_metadata: Dict[str, str]) -> bool:
        """
        Verify Agent registration information

        Args:
            agent_id: Agent ID
            expected_metadata: Expected metadata dict {"key": "value", ...}

        Returns:
            Whether verification passed
        """
        print(f"\n🔍 Verifying Agent information...")
        print(f"   Agent ID: {agent_id}")

        all_passed = True

        # Verify tokenURI
        try:
            token_uri = self.get_token_uri(agent_id)
            print(f"   ✅ TokenURI: {token_uri}")
        except Exception as e:
            print(f"   ❌ TokenURI query failed: {e}")
            all_passed = False

        # Verify metadata
        for key, expected_value in expected_metadata.items():
            try:
                actual_value = self.get_metadata_decoded(agent_id, key)
                if actual_value == expected_value:
                    print(f"   ✅ {key}: {actual_value}")
                else:
                    print(f"   ❌ {key}: Expected '{expected_value}', got '{actual_value}'")
                    all_passed = False
            except Exception as e:
                print(f"   ❌ {key}: Query failed - {e}")
                all_passed = False

        return all_passed
