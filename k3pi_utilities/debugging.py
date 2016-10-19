import logging as log


def call_debug(function):
    def wrapper(*args, **kwargs):
        log.debug('Calling {}.'.format(function.__name__))
        return function(*args, **kwargs)

    return wrapper
