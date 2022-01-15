from bb.common.block import Block, Transaction
from bb.common.net.papi import Daemon, expose, get_all_uris, oneway, proxy_of
from bb.common.sec.guid import generate_guid
from bb.node.network import Network

from .names import NETWORK_NODE, NODE_ENDPOINT


class Endpoint:
    transactions: list[Transaction] = []

    def __init__(self, network: Network):
        self.network = network

    @oneway
    @expose
    def add_transaction(self, transaction_json: str):
        print(f"Adding transaction: {transaction_json}")
        self.transactions.append(Transaction.from_json(transaction_json))

    @oneway
    @expose
    def commit(self, last_block: Block):
        """
        commit synchronizes all the nodes, freezes the transaction list
        in the block, and informs all the nodes to start working for proof
        """
        print("Commit invoked")
        print(last_block.index + 1)
        print(self.transactions)
        print(last_block.hash())
        block = Block(
            index=last_block.index + 1,
            transactions=self.transactions,
            prev_hash=last_block.hash(),
        )
        print(f"Block created: {block.to_json()}")
        self.network.broadcast("start_proofing", block)

    @expose
    def get_last_block(self) -> str:
        return Block().to_json()

    @expose
    def echo(self, s: str) -> str:
        # FIXME: remove this method after testing is done
        return f"echo: {s}"


def setup_endpoint(network: Network, daemon: Daemon):
    endpoint = Endpoint(network)
    endpoint_name = f"{NODE_ENDPOINT}.{generate_guid()}"
    daemon.register(endpoint, endpoint_name)
