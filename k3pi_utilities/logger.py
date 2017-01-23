import logging
logging.basicConfig()

__all__ = ['get_logger', 'update_level']
__loggers__ = []

__default_level__ = logging.INFO


def get_logger(name, level=__default_level__):
    logger = logging.getLogger(name)
    __loggers__.append(name)
    logger.setLevel(level)
    return logger


def update_level(level):
    global __default_level__
    for name in __loggers__:
        logger = logging.getLogger(name)
        logger.setLevel(level)
    __default_level__ = level
