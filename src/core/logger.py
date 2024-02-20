import logging
import sys

NOCOLOR = "\033[0m"
RED = "\033[01;31m"
GREEN = "\033[01;32m"
ORANGE = "\033[01;33m"
BLUE = "\033[01;34m"
PURPLE = "\033[01;35m"
CYAN = "\033[01;36m"
LIGHTGRAY = "\033[01;37m"
DARKGRAY = "\033[1;30m"
LIGHTRED = "\033[1;31m"
LIGHTGREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
LIGHTBLUE = "\033[1;34m"
LIGHTPURPLE = "\033[1;35m"
LIGHTCYAN = "\033[1;36m"
WHITE = "\033[1;37m"


def create_logger(logger_name: str, log_level=logging.INFO) -> logging.Logger:
    log_format = (
        f"{PURPLE}%(asctime)s {WHITE}%(levelname)s "
        f'{YELLOW}"%(pathname)s" line %(lineno)d {LIGHTCYAN}%(message)s{NOCOLOR}'
    )
    logging.root.setLevel(log_level)
    formatter = logging.Formatter(log_format)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    logger.addHandler(handler)

    return logger
