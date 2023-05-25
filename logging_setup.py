import logging
import sys


def logConfig(loggername):
    log = logging.getLogger(loggername)
    log.setLevel(logging.DEBUG)
    logformat = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(logging.DEBUG)  # CHANGE THIS BEFORE MERGE WITH MAIN
    log.addHandler(console_handler)
    file_handler = logging.FileHandler('rlpi.log', mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logformat)
    log.addHandler(file_handler)

    log.propagate = False

    return log


def logWipe():
    with open('rlpi.log', 'w') as wipe:
        pass


log = logConfig('rlpi_logger')
