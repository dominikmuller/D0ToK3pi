from collections import defaultdict
import logging as log
from k3pi_config import config, modes
from inspect import getargspec
import pandas as pd

accumulated_per_mode = defaultdict(lambda: set())


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
        log.debug('Loading {} from {}'.format(
            buffer_name, config.data_store
        ))
        with pd.get_store(config.data_store) as store:
            if use_buffered:
                try:
                    return store.select(buffer_name)
                except KeyError:
                    pass
        log.debug('Caching into {}'.format(buffer_name))
        if self._wants_mode:
            ret = self._func(mode)
        else:
            ret = self._func()
        ret.to_hdf(config.data_store, buffer_name)
        return ret
