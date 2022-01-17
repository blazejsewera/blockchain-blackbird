from random import choice

from cryptography.hazmat.primitives.asymmetric import rsa

from bb.common.block import Data, Transaction
from bb.common.log import Logger
from bb.common.names import NODE_ENDPOINT
from bb.common.net.papi import Proxy, get_all_uris, invoke, proxy_of
from bb.common.sec.asymmetric import encode_public_key, generate_private_key
from bb.common.sec.guid import generate_guid

log = Logger()


def create_transaction(
    node: Proxy,
    user_guid: str,
    private_key: rsa.RSAPrivateKey,
    transaction_type: Data.TransactionType,
    payload: str,
):
    transaction_data = Data(T=transaction_type, payload=payload)
    transaction = Transaction(user_guid=user_guid, data=transaction_data)
    transaction.sign(private_key)
    log.debug(f"{payload}")
    invoke(node.upload_transaction, transaction.to_json())


def start():
    user_guid = generate_guid()
    log.info(f"user id: {user_guid}")
    private_key = generate_private_key()
    public_key = encode_public_key(private_key.public_key())

    log.debug("choosing random node...")
    node_uri = ""
    try:
        node_uri = choice(get_all_uris(NODE_ENDPOINT))
    except IndexError:
        log.critical("no nodes are on the network")
        exit(1)
    log.debug(f"node {node_uri} chosen")
    node = proxy_of(node_uri)

    print(
        "\nEnter:\n"
        + '"register" to register user in the system,\n'
        + '"data <your data>" to create transaction with payload,\n'
        + '"revoke" to revoke public key from network,\n'
        + '"commit" to freeze transactions list and inform nodes to start looking for proof of work.'
    )

    def _input_loop():
        while True:
            client_input = input("\n> ")
            operation_type = client_input.split()[0]

            if operation_type == "register":
                log.info("user registration...")
                create_transaction(
                    node, user_guid, private_key, operation_type, public_key
                )
                log.info("registration done")

            elif operation_type == "data":
                create_transaction(
                    node,
                    user_guid,
                    private_key,
                    operation_type,
                    client_input.split(" ", 1)[1],
                )

            elif operation_type == "revoke":
                log.info("revoking public key...")
                create_transaction(
                    node, user_guid, private_key, operation_type, public_key
                )
                log.info("revoking done")

            elif operation_type == "commit":
                invoke(node.commit)

            else:
                print(
                    "Incorrect format. Enter 'data <your data>' to create transaction with payload\n"
                    "or 'revoke' to revoke public key from network"
                )

    try:
        _input_loop()
    except KeyboardInterrupt:
        log.info("exiting")
        exit(0)
