from bb.common.log import Logger
from bb.persistence.db import start

if __name__ == "__main__":
    log = Logger()
    log.set_logger_params()
    log.debug("starting db")
    start()
