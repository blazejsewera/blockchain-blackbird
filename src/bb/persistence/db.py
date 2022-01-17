import os

from bb.common.block import Block
from bb.common.log import Logger
from bb.common.names import DB_ENDPOINT
from bb.common.net.papi import Daemon, expose


class DBBackend:
    def save_block(self, block_json: str):
        with open("data/blocks.txt", "a+") as blocks_file:
            blocks_file.write(f"{block_json}\n")

    def save_data(self, data: str):
        with open("data/data.txt", "a+") as data_file:
            data_file.write(f"{data}\n")

    def cleanup(self):
        if os.path.exists("data/blocks.txt"):
            os.remove("data/blocks.txt")
        if os.path.exists("data/data.txt"):
            os.remove("data/data.txt")


class Database:
    saved_block_indexes: list[int] = []

    def __init__(self, db_backend: DBBackend):
        self.db_backend = db_backend
        self.log = Logger(self)

    @expose
    def save_block(self, block_json: str):
        block = Block.from_json(block_json)
        if block.index in self.saved_block_indexes:
            self.log.debug("duplicate block arrived, skipping")
            return

        self.saved_block_indexes.append(block.index)
        self.db_backend.save_block(block_json)
        self.log.info(f"saved block: {block_json}")
        for transaction in block.transactions:
            if transaction.data.T == "data":
                self.db_backend.save_data(transaction.data.payload)
                self.log.info(f"saved data: {transaction.data.payload}")

    def cleanup(self):
        self.log.debug("cleaning up")
        self.db_backend.cleanup()


def start():
    db_backend = DBBackend()
    db = Database(db_backend)
    daemon = Daemon()
    daemon.register(db, DB_ENDPOINT)
    daemon.start()
    daemon.shutdown_with_ns_cleanup()
    db.cleanup()
