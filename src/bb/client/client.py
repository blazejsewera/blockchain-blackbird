import argparse
from random import choice
from typing import Optional

from cryptography.hazmat.primitives.asymmetric import rsa

from bb.common.block import Data, Transaction
from bb.common.log import Logger
from bb.common.names import NODE_ENDPOINT
from bb.common.net.papi import CommunicationError, Proxy, get_all_uris, invoke, proxy_of
from bb.common.sec.asymmetric import encode_public_key, generate_private_key
from bb.common.sec.guid import generate_guid


class Client:
    def __init__(self):
        self.log = Logger(self)
        self.choose_random_node()

    def choose_random_node(self):
        self.log.debug("choosing random node")
        try:
            node_uri = choice(get_all_uris(NODE_ENDPOINT))
        except IndexError:
            self.log.critical("no nodes are on the network")
            exit(1)
        self.node = proxy_of(node_uri)

    def create_transaction(
        self,
        user_guid: str,
        private_key: rsa.RSAPrivateKey,
        transaction_type: Data.TransactionType,
        payload: str,
    ):
        transaction_data = Data(T=transaction_type, payload=payload)
        transaction = Transaction(user_guid=user_guid, data=transaction_data)
        transaction.sign(private_key)
        self.log.debug(f"{payload}")
        try:
            invoke(self.node.upload_transaction, transaction.to_json())
        except CommunicationError:
            self.log.warn("connection with node lost")
            self.choose_random_node()

    def start(self, initial_user_guid: Optional[str] = None):
        user_guid = (
            initial_user_guid if initial_user_guid is not None else generate_guid()
        )
        self.log.info(f"user id: {user_guid}")
        private_key = generate_private_key()
        public_key = encode_public_key(private_key.public_key())

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
                    self.log.info("user registration...")
                    self.create_transaction(
                        user_guid, private_key, operation_type, public_key
                    )
                    self.log.info("registration done")

                elif operation_type == "data":
                    self.create_transaction(
                        user_guid,
                        private_key,
                        operation_type,
                        client_input.split(" ", 1)[1],
                    )

                elif operation_type == "revoke":
                    self.log.info("revoking public key...")
                    self.create_transaction(
                        user_guid, private_key, operation_type, public_key
                    )
                    self.log.info("revoking done")

                elif operation_type == "commit":
                    try:
                        invoke(self.node.commit)
                    except CommunicationError:
                        self.log.warn("connection with node lost")
                        self.choose_random_node()

                else:
                    print(
                        "Incorrect format. Enter 'data <your data>' to create transaction with payload\n"
                        "or 'revoke' to revoke public key from network"
                    )

        try:
            _input_loop()
        except KeyboardInterrupt:
            self.log.info("exiting")
            exit(0)
