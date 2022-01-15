from bb.client.client import start
from bb.common.log import Logger

if __name__ == "__main__":
    log = Logger()
    log.set_logger_params()
    log.debug("starting client")
    start()
