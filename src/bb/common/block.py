import json
from dataclasses import asdict, dataclass, field, replace
from datetime import datetime as Timestamp
from typing import Literal

from bb.common.sec.asymmetric import (
    RSAPrivateKey,
    RSAPublicKey,
    sign_rsa_base64,
    verify_rsa,
)
from bb.common.sec.hash import hash_hex


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


@dataclass(frozen=False)
class Transaction:
    user_guid: str = ""
    fingerprint: str = ""
    data: Data = field(default_factory=Data)

    def to_json(self, indent=None):
        return json.dumps(asdict(self), indent=indent)

    def __transaction_without_fingerprint_json(self):
        transaction_without_fingerprint = replace(self, fingerprint="")
        return transaction_without_fingerprint.to_json()

    def sign(self, private_key: RSAPrivateKey):
        twf = self.__transaction_without_fingerprint_json()
        signature = sign_rsa_base64(twf, private_key)
        self.fingerprint = signature

    def verify(self, public_key: RSAPublicKey) -> bool:
        twf = self.__transaction_without_fingerprint_json()
        signature = self.fingerprint
        return verify_rsa(twf, signature, public_key)

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

    def hash(self):
        return hash_hex(self.to_json())

    def proof_of_work(self, difficulty: int = 4):
        found = False
        while not found:
            print(self.hash())
            print(list(self.hash()[0:difficulty]))
            print(["0"] * difficulty)
            if list(self.hash()[0:difficulty]) == ["0"] * difficulty:
                found = True
                return self.proof
            self.proof += 1

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
