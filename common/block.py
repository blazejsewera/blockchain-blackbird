from typing import List, Literal
from datetime import datetime as Timestamp
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Data:
    TransactionType = Literal["register", "data", "revoke"]  # type
    T: TransactionType = "data"
    payload: str = ""
    """payload contains data payload (if T == 'data') or public key (otherwise)"""


@dataclass(frozen=True)
class Transaction:
    user_guid: str = ""
    fingerprint: str = ""
    data: Data = field(default_factory=Data)


@dataclass(frozen=False)
class Block:
    index: int = 0
    timestamp: str = Timestamp.now().isoformat(timespec="milliseconds")
    transactions: List[Transaction] = field(default_factory=list)
    prev_hash: str = ""
    proof: int = 0

    def get_timestamp(self):
        return Timestamp.fromisoformat(self.timestamp)

    def of(block_dict: dict):
        return Block(
            index=block_dict["index"],
            timestamp=block_dict["timestamp"],
            transactions=[
                Transaction(
                    user_guid=transaction["user_guid"],
                    fingerprint=transaction["fingerprint"],
                    data=Data(
                        T=transaction["data"]["T"],
                        payload=transaction["data"]["payload"],
                    ),
                )
                for transaction in block_dict["transactions"]
            ],
            prev_hash=block_dict["prev_hash"],
            proof=block_dict["proof"],
        )
