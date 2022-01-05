from typing import Literal

from bb.common.block import Block, Transaction
from bb.common.net.papi import Daemon, expose, get_all_uris, invoke, oneway, proxy_of
from bb.common.sec.asymmetric import RSAPublicKey, decode_public_key
from bb.common.sec.guid import generate_guid
from bb.node.names import NETWORK_NODE


class Node:
    SupportedMethod = Literal[
        "add_transaction",
        "start_proofing",
        "proof_found",
    ]

    registered_users: dict[str, RSAPublicKey] = {}
    """registered_users keeps track of public keys for certain user_guids
    {"<user_guid>": <public_key>}"""
    blocks: list[Block] = []

    current_block: Block = Block()

    def __verify_transaction_and_perform_action(self, transaction: Transaction) -> bool:
        def _register_user(_user_guid, _public_key_base64) -> bool:
            if user_guid in self.registered_users.keys():
                print("> user already registered, not verified")
                return False
            _public_key = decode_public_key(_public_key_base64)
            if not transaction.verify(_public_key):
                print(
                    "> transaction not verified, "
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
            print("> user not registered, data.T not register, not verified")
            return False

        public_key = self.registered_users[user_guid]
        if not transaction.verify(public_key):
            print("> transaction not verified, wrong signature for this public key")
            return False

        if data.T == "revoke":
            self.registered_users.pop(user_guid)

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
        # TODO: spawn a thread to calculate proof of work
        print(f"> start proofing")

    @oneway
    @expose
    def proof_found(self, proof: int, hash: str):
        # TODO: stop the proof of work thread if didn't stop already
        print(f"> proof: {proof}")


class Network:
    node_uris: list[str] = []

    def scan(self):
        self.node_uris = get_all_uris(NETWORK_NODE)

    def broadcast(self, method_name: Node.SupportedMethod, *args, **kwargs):
        unreachable_nodes: list[str] = []
        for node in self.node_uris:
            method = getattr(proxy_of(node), method_name)
            try:
                invoke(method, *args, **kwargs)
            except ConnectionError:
                unreachable_nodes.append(node)

        for unreachable_node in unreachable_nodes:
            self.node_uris.remove(unreachable_node)


def setup_network(daemon: Daemon):
    node = Node()
    network = Network()

    network_node_name = f"{NETWORK_NODE}.{generate_guid()}"
    daemon.register(node, network_node_name)

    network.scan()
