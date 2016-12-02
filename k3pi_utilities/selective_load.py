from collections import defaultdict
import logging as log
from k3pi_config import config
import pandas as pd
from k3pi_config import modes

accumulated_per_mode = defaultdict(lambda: set())


class selective_load():
    def __init__(self, function):
        self.requested_columns = {}
        for m in config.all_modes:
            d = defaultdict(lambda: 1)
            # Dummy call the selection classes with the mode classes to get
            # the different variables needed.
            mode_cls = getattr(modes, m)
            function(d, mode_cls)
            self.requested_columns[m] = d.keys()
            [accumulated_per_mode[m].add(n) for n in d.keys()]
        self._func = function
        self._func_name = function.__name__

    def __call__(self, mode, use_buffered=True):
        buffer_name = 'Cached/' + self._func_name + mode.mode + \
            mode.polarity + str(mode.year)
        log.debug('Loading {} from {} with columns {}'.format(
            buffer_name, config.data_store, self.requested_columns[mode.mode]
        ))
        with pd.get_store(config.data_store) as store:
            if use_buffered:
                try:
                    return store.select(buffer_name)
                except KeyError:
                    pass
        log.debug('Caching into {}'.format(buffer_name))
        df = mode.get_data(self.requested_columns[mode.mode])
        ret = self._func(df, mode)
        del df
        ret.to_hdf(config.data_store, buffer_name)
        return ret
