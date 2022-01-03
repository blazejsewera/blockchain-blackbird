from bb.common.block import Block
from Pyro5 import api as papi


@papi.expose
class Node:
    def echo(self, s: str):
        return f"echo: {s}"

    def make_block(self):
        return Block().to_json()


def start():
    daemon = papi.Daemon()
    ns = papi.locate_ns()
    uri = daemon.register(Node)
    ns.register("node.node.1", uri)

    print("Ready!")
    daemon.requestLoop()
