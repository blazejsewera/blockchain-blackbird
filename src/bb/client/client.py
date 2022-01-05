from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from bb.common.net.papi import get_all_uris, invoke, proxy_of
from bb.node.names import NODE_ENDPOINT


def start():
    print("\nRemote object:")
    node1_uri = get_all_uris(NODE_ENDPOINT)[0]
    node = proxy_of(node1_uri)
    print(invoke(node.echo, "hello"))
    print(invoke(node.get_last_block))
