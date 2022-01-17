from dataclasses import replace
from datetime import datetime as Timestamp
from queue import Queue
from threading import Thread
from typing import Literal, Optional

from bb.common.block import Block, Transaction
from bb.common.log import Logger
from bb.common.names import DB_ENDPOINT, NETWORK_NODE
from bb.common.net.papi import Proxy, expose, get_all_uris, invoke, oneway, proxy_of
from bb.common.sec.asymmetric import RSAPublicKey, decode_public_key


class Node:
    SupportedMethod = Literal[
        "add_block",
        "add_transaction",
        "start_proofing",
        "proof_found",
    ]

    registered_users: dict[str, RSAPublicKey] = {}
    """registered_users keeps track of public keys for certain user_guids
    {"<user_guid>": <public_key>}"""
    blocks: list[Block] = []
    current_block: Optional[Block] = Block()
    is_proof_found: bool = False
    last_transaction_json = ""

    def __init__(self, network: "Network"):
        self.log = Logger(self)
        self.network = network

        self.que = Queue()

        self.prev_hash = ""

    def __locate_db(self) -> Proxy:
        db_uris = get_all_uris(DB_ENDPOINT)
        if len(db_uris) != 1:
            self.log.critical("DB not running or multiple instances running")
            exit(127)
        return proxy_of(db_uris[0])

    def __verify_transaction_and_perform_action(self, transaction: Transaction) -> bool:
        def _register_user(_user_guid, _public_key_base64) -> bool:
            if user_guid in self.registered_users.keys():
                self.log.error("user already registered, not verified")
                return False
            _public_key = decode_public_key(_public_key_base64)
            if not transaction.verify(_public_key):
                self.log.error(
                    "transaction not verified, "
                    "wrong signature for the public key in payload"
                )
                return False
            self.registered_users.update({_user_guid: _public_key})
            self.log.debug(f"registered users: {list(self.registered_users.keys())}")
            return True

        user_guid = transaction.user_guid
        data = transaction.data
        if data.T == "register":
            self.log.info(f"registering user: {user_guid} with pubkey: {data.payload}")
            return _register_user(user_guid, data.payload)

        if user_guid not in self.registered_users.keys():
            self.log.error("user not registered, data.T not register, not verified")
            return False

        public_key = self.registered_users[user_guid]
        if not transaction.verify(public_key):
            self.log.error(
                "transaction not verified, wrong signature for this public key"
            )
            return False

        if data.T == "revoke":
            self.registered_users.pop(user_guid)

        self.log.info("transaction verified")
        return True

    @oneway
    @expose
    def add_transaction(self, transaction_json: str):
        def _add_new_block_if_current_empty():
            if not self.blocks:
                index = 0
                prev_hash = ""
            else:
                index = len(self.blocks)
                prev_hash = self.blocks[-1].hash()
            self.current_block = Block(index=index, prev_hash=prev_hash)

        self.log.debug(f"transaction received: {transaction_json}")
        if transaction_json == self.last_transaction_json:
            return
        transaction = Transaction.from_json(transaction_json)
        if self.__verify_transaction_and_perform_action(transaction):
            if self.current_block is None:
                _add_new_block_if_current_empty()
            self.current_block.transactions.append(transaction)  # type: ignore (doesn't see block adding)

    @oneway
    @expose
    def start_proofing(self):
        if self.current_block is None:
            self.log.warn("no block for proofing, aborting")
            return

        timestamp = Timestamp.now().isoformat(timespec="milliseconds")

        self.current_block.timestamp = timestamp
        block = self.current_block

        self.log.info("start proofing")

        proofing = Thread(
            target=lambda x, _: x.put(block.proof_of_work()),
            args=(self.que, "proof"),
        )
        proofing.start()
        proofing.join()

        while not self.que.empty():
            self.network.broadcast(
                "proof_found", self.que.get(), block.hash(), timestamp
            )
            self.log.debug("this node found proof of work")

    @oneway
    @expose
    def proof_found(self, proof: int, hash: str, timestamp: str):
        if self.is_proof_found or self.current_block is None:
            self.log.debug("proof found earlier, skipping")
            return
        self.log.info(f"proof found, verifying ...")
        block = replace(self.current_block)
        block.proof = proof
        block.timestamp = timestamp
        if block.verify_hash(hash):
            self.log.info(f"stop proofing; proof: {proof}")
            self.is_proof_found = True
            self.current_block.proof = proof
            self.current_block.timestamp = timestamp
            if self.que.full():
                self.que.get(timeout=1)

            self.network.broadcast("add_block", proof, hash)
        else:
            self.log.warn("hashes don't match")

    @oneway
    @expose
    def add_block(self, proof: int, hash: str):
        if self.current_block is None:
            self.log.debug("current block already added, no new transactions, skipping")
            return

        self.current_block.proof = proof
        if self.current_block.index in [b.index for b in self.blocks]:
            self.log.debug("block already added, skipping")
            return

        self.blocks.append(self.current_block)
        self.log.debug(f"appended block: {self.current_block.to_json()}")
        db = self.__locate_db()
        invoke(db.save_block, self.current_block.to_json())
        self.log.debug("sent block to db")

        self.current_block = None
        self.is_proof_found = False


class Network:
    node_uris: list[str] = []

    def __init__(self):
        self.log = Logger(self)

    def scan(self):
        self.node_uris = get_all_uris(NETWORK_NODE)
        self.log.debug(f"discovered on network: {self.node_uris}")

    def broadcast(self, method_name: Node.SupportedMethod, *args, **kwargs):
        self.scan()
        unreachable_nodes: list[str] = []
        for node in self.node_uris:
            method = getattr(proxy_of(node), method_name)
            try:
                invoke(method, *args, **kwargs)
                self.log.info(f"broadcasted {method_name} to {node}")
            except ConnectionError:
                unreachable_nodes.append(node)
                self.log.warn(f"unreachable node: {node}")

        for unreachable_node in unreachable_nodes:
            self.node_uris.remove(unreachable_node)
            self.log.debug(f"removing node: {unreachable_node} from network map")
