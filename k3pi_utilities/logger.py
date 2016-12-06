import logging
logging.basicConfig()

__all__ = ['get_logger']
def get_logger(name, level = logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger
