"""
Recall client and wrapper contract interactions
"""

from typing import Any, TypeVar, cast

import requests
from eth_account.account import LocalAccount
from eth_typing import ChecksumAddress
from eth_utils import currency, to_checksum_address
from web3 import Account, Web3
from web3._utils.events import EventLogErrorFlags
from web3.contract import Contract
from web3.exceptions import ContractLogicError
from web3.types import HexBytes, Nonce, TxReceipt

from .constants import (
    BLOB_MANAGER_ABI,
    BLOB_MANAGER_ADDRESS,
    BUCKET_MANAGER_ABI,
    BUCKET_MANAGER_ADDRESS,
    CREDIT_MANAGER_ABI,
    CREDIT_MANAGER_ADDRESS,
    IMACHINE_FACADE_ABI,
    RPC_TIMEOUT,
    TESTNET_CHAIN_ID,
    get_evm_rpc_url,
    get_object_api_url,
)
from .exceptions import ContractError, ObjectNotFoundError, UnexpectedError
from .types import CreatedBucketResponse, EventLog

T = TypeVar("T")


class Client:
    """
    Recall client and wrapper contract interactions
    """

    w3: Web3
    signer: LocalAccount
    evm_rpc_url: str
    object_api_url: str
    blob_manager: Contract
    bucket_manager: Contract
    credit_manager: Contract

    def __init__(
        self,
        private_key: str,
        chain_id: int = TESTNET_CHAIN_ID,
        evm_rpc_url: str | None = None,
        object_api_url: str | None = None,
    ):
        # Set up web3 instance, signer, and objects API
        if evm_rpc_url is None:
            evm_rpc_url = get_evm_rpc_url(chain_id)
        if object_api_url is None:
            object_api_url = get_object_api_url(chain_id)
        w3 = Web3(Web3.HTTPProvider(evm_rpc_url))
        self.w3 = w3
        self.signer = Account.from_key(private_key)
        self.object_api_url = object_api_url

        # Set up Recall contracts
        chain_id = self.get_chain_id()
        blob_manager_addr = BLOB_MANAGER_ADDRESS[chain_id]
        bucket_manager_addr = BUCKET_MANAGER_ADDRESS[chain_id]
        credit_manager_addr = CREDIT_MANAGER_ADDRESS[chain_id]
        self.blob_manager = self.w3.eth.contract(address=to_checksum_address(blob_manager_addr), abi=BLOB_MANAGER_ABI)
        self.bucket_manager = self.w3.eth.contract(
            address=to_checksum_address(bucket_manager_addr), abi=BUCKET_MANAGER_ABI
        )
        self.credit_manager = self.w3.eth.contract(
            address=to_checksum_address(credit_manager_addr), abi=CREDIT_MANAGER_ABI
        )

    def get_chain_id(self) -> int:
        """Get the chain ID for the current network"""
        return self.w3.eth.chain_id

    def get_signer_address(self) -> ChecksumAddress:
        """Get the connected signer's address"""
        return self.signer.address

    def get_nonce(self) -> Nonce:
        """Get the nonce for the connected signer"""
        return self.w3.eth.get_transaction_count(self.signer.address)

    def wait_for_tx_receipt(self, tx_hash: HexBytes | HexBytes) -> TxReceipt:
        """Wait for a transaction receipt to be returned"""
        return self.w3.eth.wait_for_transaction_receipt(tx_hash)

    def parse_tx_receipt(self, contract: Contract, tx_receipt: TxReceipt, event_type: str) -> list[EventLog]:
        """Parse a transaction receipt for a given event type"""
        event = getattr(contract.events, event_type)()
        return event.process_receipt(tx_receipt, errors=EventLogErrorFlags.Discard)

    def _handle_bucket_creation_failure(self) -> None:
        """Handle bucket creation failure by raising an appropriate error."""
        raise UnexpectedError(UnexpectedError.BUCKET_CREATION_FAILED)

    def create_bucket(self, owner: str | None = None, metadata: dict | None = None) -> CreatedBucketResponse | None:
        """Create a bucket for a given owner or default to the signer's address"""
        try:
            # Function arguments
            metadata = metadata or {}
            metadata_list = [(key, str(value)) for key, value in metadata.items()]
            owner = owner if owner is not None else self.get_signer_address()

            # Build tx with custom gas params
            gas = self.bucket_manager.functions.createBucket(
                owner,
                metadata_list,
            ).estimate_gas()
            tx = self.bucket_manager.functions.createBucket(
                owner,
                metadata_list,
            ).build_transaction({
                "from": self.get_signer_address(),
                "gas": gas,
                "maxFeePerGas": currency.to_wei(100, "wei"),
                "maxPriorityFeePerGas": currency.to_wei(1, "wei"),
                "nonce": self.get_nonce(),
            })
            typed_tx = cast(dict[str, Any], tx)
            # Sign and send the transaction
            signed_tx = self.signer.sign_transaction(typed_tx)
            tx_hash = self.w3.eth.send_raw_transaction(HexBytes(signed_tx["raw_transaction"]))

            # Parse tx receipt
            machine_facade_contract = self.w3.eth.contract(
                address=to_checksum_address(BUCKET_MANAGER_ADDRESS[self.get_chain_id()]), abi=IMACHINE_FACADE_ABI
            )
            rec = self.wait_for_tx_receipt(tx_hash)
            log = self.parse_tx_receipt(machine_facade_contract, rec, "MachineInitialized")
            args = log[0]["args"] if len(log) > 0 else None
            if args is None:
                self._handle_bucket_creation_failure()
            return CreatedBucketResponse(bucket=args["machineAddress"], kind=args["kind"])
        except ContractLogicError as e:
            raise ContractError(str(e)) from e
        except Exception as e:
            raise UnexpectedError(str(e)) from e

    def list_buckets(self, owner: str | None = None) -> Any:
        """List buckets for a given owner or default to the signer's address"""
        try:
            return self.bucket_manager.functions.listBuckets(
                owner if owner is not None else self.get_signer_address(),
            ).call()
        except ContractLogicError as e:
            raise ContractError(str(e)) from e
        except Exception as e:
            raise UnexpectedError(str(e)) from e

    def get_object_state(self, bucket: str, key: str) -> Any | None:
        """Get an object's state (without downloading the object)"""
        try:
            bucket_addr = to_checksum_address(bucket)
            return self.bucket_manager.functions.getObject(bucket_addr, key).call()
        except ContractLogicError as e:
            raise ContractError(str(e)) from e
        except Exception as e:
            raise UnexpectedError(str(e)) from e

    def _ensure_object_exists(self, bucket: str, key: str, obj: dict | None) -> None:
        """Helper function to check if object exists and raise if not."""
        if obj is None:
            raise ObjectNotFoundError(bucket, key)

    def get_object(self, bucket: str, key: str) -> bytes:
        """Get an object's data"""
        try:
            obj = self.get_object_state(bucket, key)
            self._ensure_object_exists(bucket, key, obj)
            # Bucket addrs are in the format `0xff00...<id>`, but we need to convert to its ID address
            hex_str = bucket[2:]  # Remove '0x'
            id_start = hex_str.find("ff") + 2  # Skip past 'ff'
            hex_id = hex_str[id_start:].lstrip("0")  # Remove leading zeros
            actor_id = int(hex_id, 16)
            bucket_id_addr = "t0" + str(actor_id)
            response = requests.get(
                f"{self.object_api_url}/v1/objects/{bucket_id_addr}/{key}",
                timeout=RPC_TIMEOUT,
            )
            if response.content:
                return response.content
            else:
                return b""
        except ContractLogicError as e:
            raise ContractError(str(e)) from e
        except Exception as e:
            raise UnexpectedError(str(e)) from e


if __name__ == "__main__":  # pragma: no cover
    pass
