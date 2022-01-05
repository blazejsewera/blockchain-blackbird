from bb.common.block import Block, Transaction
from bb.common.net.papi import Daemon, expose, oneway
from bb.common.sec.guid import generate_guid

from .names import NODE_ENDPOINT


class Endpoint:
    transactions: list[Transaction] = []

    @oneway
    @expose
    def add_transaction(self, transaction_json: str):
        self.transactions.append(Transaction.from_json(transaction_json))

    @oneway
    @expose
    def commit(self):
        """
        commit synchronizes all the nodes, freezes the transaction list
        in the block, and informs all the nodes to start working for proof
        """
        pass

    @expose
    def get_last_block(self) -> str:
        return Block().to_json()

    @expose
    def echo(self, s: str) -> str:
        # FIXME: remove this method after testing is done
        return f"echo: {s}"


def setup_endpoint(daemon: Daemon):
    endpoint = Endpoint()
    endpoint_name = f"{NODE_ENDPOINT}.{generate_guid()}"
    daemon.register(endpoint, endpoint_name)
