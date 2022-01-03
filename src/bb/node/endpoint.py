from bb.common.block import Block
from Pyro5 import api as papi

from .names import NODE_ENDPOINT


@papi.expose
class Endpoint:
    def echo(self, s: str):
        return f"echo: {s}"

    def make_block(self):
        return Block().to_json()


def start():
    daemon = papi.Daemon()
    ns = papi.locate_ns()
    uri = daemon.register(Endpoint)
    ns.register(f"{NODE_ENDPOINT}.1", uri)

    print("Ready!")
    try:
        daemon.requestLoop()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        daemon.shutdown()
        ns.remove(name=f"{NODE_ENDPOINT}.1")
        print("Done.")
