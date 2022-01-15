import logging

from colorlog import ColoredFormatter


class Logger:
    def __init__(self, obj=None):
        self.classname = type(obj).__name__ if obj is not None else "Main"

    @classmethod
    def set_logger_params(cls):
        LOGFORMAT = "%(log_color)s%(levelname)-5s | %(log_color)s%(message)s%(reset)s"
        LOGLEVEL = logging.DEBUG
        logging.getLogger().setLevel(LOGLEVEL)
        formatter = ColoredFormatter(LOGFORMAT)
        stream = logging.StreamHandler()
        stream.setLevel(LOGLEVEL)
        stream.setFormatter(formatter)
        logging.getLogger().addHandler(stream)

    def debug(self, msg):
        logging.debug(f"{self.classname} | {msg}")

    def info(self, msg):
        logging.info(f"{self.classname} | {msg}")

    def warn(self, msg):
        logging.warning(f"{self.classname} | {msg}")

    def error(self, msg):
        logging.error(f"{self.classname} | {msg}")

    def critical(self, msg):
        logging.critical(f"{self.classname} | {msg}")
