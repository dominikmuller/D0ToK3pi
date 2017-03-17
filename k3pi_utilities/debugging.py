from decorator import decorate
from k3pi_utilities.logger import get_logger
log = get_logger('call_debug')

def call_debug(function):
    def wrapper(f, *args, **kwargs):
        log.debug('Calling {}.'.format(function.__name__))
        return f(*args, **kwargs)

    return decorate(function, wrapper)
