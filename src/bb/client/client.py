from Pyro5 import api as papi
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from bb.node.names import NODE_ENDPOINT


def generate_pk():
    DEFAULT_RSA_PUBLIC_EXPONENT = 65537
    pk = rsa.generate_private_key(DEFAULT_RSA_PUBLIC_EXPONENT, 1024)
    print(pk.public_key().public_bytes(Encoding.OpenSSH, PublicFormat.OpenSSH))


def start():
    generate_pk()
    print("\nRemote object:")
    ns = papi.locate_ns()
    nodes = ns.list(NODE_ENDPOINT)
    node1_key = list(nodes.keys())[0]
    node1_uri = nodes[node1_key]
    node = papi.Proxy(node1_uri)
    print(node.echo("hello"))
    print(node.make_block())
