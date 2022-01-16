from bb.common.block import Block
from bb.common.log import Logger
from bb.common.names import DB_ENDPOINT
from bb.common.net.papi import Daemon, expose


class DBBackend:
    def save(self):
        pass


class Database:
    saved_block_indexes: list[int] = []

    def __init__(self, db_backend):
        self.db_backend = db_backend
        self.log = Logger(self)

    @expose
    def save_block(self, block_json: str):
        block = Block.from_json(block_json)
        self.saved_block_indexes.append(block.index)
        self.db_backend.save(block_json)
        self.log.info(f"saved block: {block_json}")


def start():
    db_backend = DBBackend()
    db = Database(db_backend)
    daemon = Daemon()
    daemon.register(db, DB_ENDPOINT)
    daemon.start()
    daemon.shutdown_with_ns_cleanup()
