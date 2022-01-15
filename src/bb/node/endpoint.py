from bb.common.block import Block, Transaction
from bb.common.net.papi import Daemon, expose, get_all_uris, oneway, proxy_of
from bb.common.sec.guid import generate_guid
from bb.node.network import Network

from .names import NODE_ENDPOINT


class Endpoint:
    def __init__(self, network: Network):
        self.network = network

    @oneway
    @expose
    def add_transaction(self, transaction_json: str):
        self.network.broadcast("add_transaction", transaction_json)

    @oneway
    @expose
    def commit(self):
        """
        commit synchronizes all the nodes, freezes the transaction list
        in the block, and informs all the nodes to start working for proof
        """
        self.network.broadcast("start_proofing")

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
