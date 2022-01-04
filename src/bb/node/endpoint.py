from Pyro5 import api as papi

from bb.common.block import Block, Transaction

from .names import NODE_ENDPOINT


@papi.expose
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
    daemon = papi.Daemon()
    ns = papi.locate_ns()
    uri = daemon.register(Endpoint)
    ns.register(f"{NODE_ENDPOINT}.1", uri)

    print("Ready!")
    try:
        daemon.requestLoop()
    except Exception:
        pass
    finally:
        print("\nShutting down...")
        daemon.shutdown()
        ns.remove(name=f"{NODE_ENDPOINT}.1")
        print("Done.")
