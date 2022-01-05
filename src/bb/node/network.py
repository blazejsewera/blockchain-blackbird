from typing import Literal

from bb.common.block import Block, Transaction
from bb.common.net.papi import Daemon, expose, get_all_uris, invoke, oneway, proxy_of
from bb.common.sec.guid import generate_guid
from bb.node.names import NETWORK_NODE


class Node:
    SupportedMethod = Literal[
        "add_transaction",
        "start_proofing",
        "proof_found",
    ]

    blocks: list[Block] = []

    current_block: Block = Block()
    current_transactions: list[Transaction] = []

    @oneway
    @expose
    def add_transaction(self, transaction_json: str):
        # TODO: verify transaction
        self.current_transactions.append(Transaction.from_json(transaction_json))

    @oneway
    @expose
    def start_proofing(self):
        # TODO: spawn a thread to calculate proof of work
        print(f"> start proofing")

    @oneway
    @expose
    def proof_found(self, proof: int):
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
