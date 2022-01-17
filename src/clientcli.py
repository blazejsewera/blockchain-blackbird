import argparse
from typing import Optional

from bb.client.client import Client
from bb.common.log import Logger

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-u", "--user-guid", type=str, required=False, default=None)
    args = p.parse_args()
    user_guid: Optional[str] = args.user_guid
    log = Logger()
    log.set_logger_params()
    log.debug("starting client")
    Client().start(user_guid)
