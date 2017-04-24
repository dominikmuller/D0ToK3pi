import logging

import colorlog

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)s:%(name)s:%(message)s'))

__all__ = ['get_logger', 'update_level']
__loggers__ = {}

__default_level__ = logging.INFO


def get_logger(name, level=__default_level__):
    if name in __loggers__:
        return __loggers__[name]
    logger = logging.getLogger(name)
    logger.propagate = False
    __loggers__[name] = logger
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


def update_level(level):
    global __default_level__
    for logger in __loggers__.values():
        logger.setLevel(level)
    __default_level__ = level
