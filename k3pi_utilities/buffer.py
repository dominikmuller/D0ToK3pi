from collections import defaultdict
import logging as log
from k3pi_config import config
import pandas as pd

accumulated_per_mode = defaultdict(lambda: set())


class buffer_load():
    def __init__(self, function):
        self._func = function
        self._func_name = function.__name__
        self.__name__ = function.__name__
        self.__doc__ = function.__doc__

    def __call__(self, mode, use_buffered=True):
        buffer_name = 'Cached/' + self._func_name + mode.mode + \
            mode.polarity + str(mode.year)
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
        ret = self._func(mode)
        ret.to_hdf(config.data_store, buffer_name)
        return ret
