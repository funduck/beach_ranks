import sys
import logging

import os


def init_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if 'LOG_FILE' in os.environ:
        ch = logging.FileHandler(os.environ['LOG_FILE'])
    else:
        ch = logging.StreamHandler(sys.stdout)

    ch.setLevel(0)
    formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s  %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def get_logger(name):
    return logging.getLogger(name)
