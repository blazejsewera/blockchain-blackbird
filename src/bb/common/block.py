import json
from dataclasses import asdict, dataclass, field
from datetime import datetime as Timestamp
from typing import Literal

from bb.common.sec.hash import sha256


@dataclass(frozen=True)
class Data:
    TransactionType = Literal["register", "data", "revoke"]  # type
    T: TransactionType = "data"
    payload: str = ""
    """payload contains data payload (if T == 'data') or public key (otherwise)"""

    def to_json(self, indent=None):
        return json.dumps(asdict(self), indent=indent)

    @staticmethod
    def of(data_dict: dict):
        return Data(T=data_dict["T"], payload=data_dict["payload"])

    @staticmethod
    def from_json(serialized_data: str | dict):
        if isinstance(serialized_data, str):
            return Data.of(json.loads(serialized_data))
        return Data.of(serialized_data)


@dataclass(frozen=True)
class Transaction:
    user_guid: str = ""
    fingerprint: str = ""
    data: Data = field(default_factory=Data)

    def to_json(self, indent=None):
        return json.dumps(asdict(self), indent=indent)

    @staticmethod
    def of(transaction_dict: dict):
        return Transaction(
            user_guid=transaction_dict["user_guid"],
            fingerprint=transaction_dict["fingerprint"],
            data=Data.of(transaction_dict["data"]),
        )

    @staticmethod
    def from_json(serialized_transaction: str | dict):
        if isinstance(serialized_transaction, str):
            return Transaction.of(json.loads(serialized_transaction))
        return Transaction.of(serialized_transaction)


@dataclass(frozen=False)
class Block:
    index: int = 0
    timestamp: str = Timestamp.now().isoformat(timespec="milliseconds")
    transactions: list[Transaction] = field(default_factory=list)
    prev_hash: str = ""
    proof: int = 0

    def get_timestamp(self):
        return Timestamp.fromisoformat(self.timestamp)

    def to_json(self, indent=None):
        return json.dumps(asdict(self), indent=indent)

    @staticmethod
    def of(block_dict: dict):
        return Block(
            index=block_dict["index"],
            timestamp=block_dict["timestamp"],
            transactions=[
                Transaction.of(transaction)
                for transaction in block_dict["transactions"]
            ],
            prev_hash=block_dict["prev_hash"],
            proof=block_dict["proof"],
        )

    @staticmethod
    def from_json(serialized_block: str | dict):
        if isinstance(serialized_block, str):
            return Block.of(json.loads(serialized_block))
        return Block.of(serialized_block)

    def hash(self, to_bytes=False):
        return sha256(self.to_json())
