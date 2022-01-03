import json
from typing import Literal
from datetime import datetime as Timestamp
from dataclasses import asdict, dataclass, field
from cryptography.hazmat.primitives.hashes import Hash, SHA256


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
    transactions: list[Transaction] = field(default_factory=list)
    prev_hash: str = ""
    proof: int = 0

    def get_timestamp(self):
        return Timestamp.fromisoformat(self.timestamp)

    def to_json(self, indent=None):
        return json.dumps(asdict(self), indent=indent)

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

    def from_json(serialized_block: str | dict):
        if type(serialized_block) == str:
            return Block.of(json.loads(serialized_block))
        return Block.of(serialized_block)

    def hash(self, to_bytes=False):
        json_bytes = self.to_json().encode("utf-8")

        digest = Hash(SHA256())
        digest.update(json_bytes)
        hash_bytes = digest.finalize()

        if to_bytes:
            return hash_bytes
        return hash_bytes.hex()
