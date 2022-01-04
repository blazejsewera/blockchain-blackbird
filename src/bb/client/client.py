from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from Pyro5.client import _RemoteMethod as RemoteMethod

from bb.common.net.papi import get_all_uris, invoke, proxy_of
from bb.node.names import NODE_ENDPOINT


def generate_pk():
    DEFAULT_RSA_PUBLIC_EXPONENT = 65537
    pk = rsa.generate_private_key(DEFAULT_RSA_PUBLIC_EXPONENT, 1024)
    print(pk.public_key().public_bytes(Encoding.OpenSSH, PublicFormat.OpenSSH))


def start():
    generate_pk()
    print("\nRemote object:")
    node1_uri = get_all_uris(NODE_ENDPOINT)[0]
    node = proxy_of(node1_uri)
    print(invoke(node.echo, "hello"))
    if isinstance(node.get_last_block, RemoteMethod):
        print(node.get_last_block())
