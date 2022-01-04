from bb.common.block import Block, Transaction
from bb.common.net.papi import Daemon, expose

from .names import NODE_ENDPOINT


@expose
class Endpoint:
    transactions: list[Transaction] = []

    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)

    def commit(self):
        """
        commit synchronizes all the nodes, freezes the transaction list
        in the block, and informs all the nodes to start working for proof
        """
        pass

    def get_last_block(self) -> str:
        return Block().to_json()

    def echo(self, s: str):
        return f"echo: {s}"


def start():
    daemon = Daemon()
    daemon.register(Endpoint, f"{NODE_ENDPOINT}.1")

    daemon.start()
