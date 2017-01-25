from collections import defaultdict
from k3pi_config import config, modes
from k3pi_utilities.logger import get_logger
from inspect import getargspec
import pandas as pd

log = get_logger('buffer_load')

accumulated_per_mode = defaultdict(lambda: set())


def remove_buffer_for_function(func):
    """This will trigger the deletion of buffered values matching the function
    so they are automatically refreshed when needed."""
    with pd.get_store(config.data_store) as store:
        for a in store:
            if 'Cached' not in a:
                continue
            if func.__name__ in a:
                log.info('Removing {} from store'.format(a))
                store.remove(a)


def remove_buffer_for_mode(modename):
    """Cleans out the cache for everything belonging to a certain mode."""
    with pd.get_store(config.data_store) as store:
        for a in store:
            if 'Cached' not in a:
                continue
            if modename not in a:
                continue
            log.info('Removing {} from store'.format(a))
            store.remove(a)


class buffer_load():
    def __init__(self, function):
        try:
            self._wants_mode = 'mode' in getargspec(function).args
        except TypeError:
            self._wants_mode = 'mode' in getargspec(function.__call__).args
        self._func = function
        self._func_name = function.__name__
        self.__name__ = function.__name__
        self.__doc__ = function.__doc__

    def __call__(self, mode=None, use_buffered=True):
        if mode is None:
            mode = modes.gcm()
        # Build a string unique by combining function name, mode, polarity
        # year and whether it is mc, gen or nominal (data)
        buffer_name = 'Cached/' + self._func_name + mode.mode + \
            mode.polarity + str(mode.year)
        if mode.mc is not None:
            buffer_name += mode.mc
        log.info('Loading {} from {}'.format(
            buffer_name, config.data_store
        ))
        with pd.get_store(config.data_store) as store:
            if use_buffered:
                try:
                    return store.select(buffer_name)
                except KeyError:
                    pass
        log.info('Caching into {}'.format(buffer_name))
        if self._wants_mode:
            ret = self._func(mode)
        else:
            ret = self._func()
        ret.to_hdf(config.data_store, buffer_name)
        return ret
