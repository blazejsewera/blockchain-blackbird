from bb.common.log import Logger
from bb.node.node import start

if __name__ == "__main__":
    log = Logger()
    log.set_logger_params()
    log.debug("starting node")
    start()
