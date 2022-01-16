from queue import Queue
from threading import Thread
from typing import Literal

from bb.common import block
from bb.common.block import Block, Transaction
from bb.common.log import Logger
from bb.common.net.papi import Daemon, expose, get_all_uris, invoke, oneway, proxy_of
from bb.common.sec.asymmetric import RSAPublicKey, decode_public_key
from bb.common.sec.guid import generate_guid
from bb.node.names import NETWORK_NODE


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
    current_block: Block = Block()

    def __init__(self, network):
        self.log = Logger(self)
        self.network = network
        self.que = Queue()

        self.prev_hash = ""

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
            self.registered_users[_user_guid] = public_key
            return True

        user_guid = transaction.user_guid
        data = transaction.data
        if data.T == "register":
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
        transaction = Transaction.from_json(transaction_json)
        if self.__verify_transaction_and_perform_action(transaction):
            self.current_block.transactions.append(transaction)

    @oneway
    @expose
    def start_proofing(self):
        self.log.info("start proofing")

        proofing = Thread(
            target=lambda x, arg1: x.put(self.current_block.proof_of_work()),
            args=(self.que, "proof"),
        )
        proofing.start()
        proofing.join()

        while not self.que.empty():
            self.network.broadcast(
                "proof_found", self.que.get(), self.current_block.hash()
            )
            self.log.debug("this node found proof of work")

    @oneway
    @expose
    def proof_found(self, proof: int, hash: str):
        self.log.info(f"proof found, verifying ...")
        if Block.verify_hash(hash):
            self.log.info(f"stop proofing; proof: {proof}")
            self.que.get()

            self.network.broadcast("add_block", proof, hash)

    @oneway
    @expose
    def add_block(self, proof: int, hash: str):
        # if chain of blocks is empty we don't need to set index and prev_hash value -- we use default ones
        if not self.blocks:
            # self.current_block.timestamp = Timestamp.now().isoformat(timespec="milliseconds") -- is necessary?
            self.current_block.proof = proof
            self.blocks.append(self.current_block)
        else:
            self.current_block.index = len(self.blocks) + 1
            # self.current_block.timestamp = Timestamp.now().isoformat(timespec="milliseconds") -- is necessary?
            self.current_block.proof = proof
            self.current_block.prev_hash = self.prev_hash
            self.blocks.append(self.current_block)

        self.prev_hash = hash
        self.log.debug(
            self.blocks
        )  # TODO: every node adds the same block, idk how to prevent it, user seems to not be registered properly


class Network:
    node_uris: list[str] = []

    def __init__(self):
        self.log = Logger(self)

    def scan(self):
        self.node_uris = get_all_uris(NETWORK_NODE)
        self.log.info(f"discovered on network: {self.node_uris}")

    def broadcast(self, method_name: Node.SupportedMethod, *args, **kwargs):
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


def setup_network(daemon: Daemon):
    network = Network()
    node = Node(network)

    network_node_name = f"{NETWORK_NODE}.{generate_guid()}"
    daemon.register(node, network_node_name)

    network.scan()
