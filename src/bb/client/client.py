from random import choice

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from bb.common.block import Data, Transaction
from bb.common.net.papi import get_all_uris, invoke, proxy_of
from bb.common.sec.asymmetric import encode_public_key, generate_private_key
from bb.common.sec.guid import generate_guid
from bb.node.names import NODE_ENDPOINT


def create_transaction(
    node,
    user_guid: str,
    private_key: rsa.RSAPrivateKey,
    transaction_type: Data.TransactionType,
    payload: str,
):
    transaction_data = Data(transaction_type, payload)
    transaction = Transaction(user_guid, "", transaction_data)
    transaction.sign(private_key)
    print(f"{payload}")
    invoke(node.add_transaction, transaction.to_json())


def start():
    user_guid = generate_guid()
    private_key = generate_private_key()
    public_key = encode_public_key(private_key.public_key())

    print("\nChoosing random node...")
    node_uri = choice(get_all_uris(NODE_ENDPOINT))
    node = proxy_of(node_uri)

    print("\nUser registration...")
    create_transaction(node, user_guid, private_key, "register", public_key)
    print("\nRegistration done")

    print(
        "\nEnter:\n"
        + '"data <your data>" to create transaction with payload,\n'
        + '"revoke" to revoke public key from network,\n'
        + '"commit" to freeze transactions list and inform nodes to start looking for proof of work.'
    )
    while True:
        client_input = input("\n>")
        operation_type = client_input.split()[0]

        if operation_type == "data":
            create_transaction(
                node,
                user_guid,
                private_key,
                operation_type,
                client_input.split(" ", 1)[1],
            )

        elif operation_type == "revoke":
            create_transaction(node, user_guid, private_key, operation_type, public_key)

        elif operation_type == "commit":
            invoke(node.commit)

        else:
            print(
                'Incorrect format. Enter "data <your data>" to create transaction with payload or "revoke" to revoke public key from network '
            )
