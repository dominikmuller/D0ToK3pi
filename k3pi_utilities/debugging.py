import logging as log
from decorator import decorate


def call_debug(function):
    def wrapper(f, *args, **kwargs):
        log.debug('Calling {}.'.format(function.__name__))
        return f(*args, **kwargs)

    return decorate(function, wrapper)
