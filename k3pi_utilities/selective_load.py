from collections import defaultdict
import logging as log
import pandas as pd
from k3pi_config import config

accumulated = set()


class selective_load():
    def __init__(self, function):
        d = defaultdict(lambda: 1)
        function(d)
        self.requested_columns = d.keys()
        [accumulated.add(n) for n in d.keys()]
        self._func = function

    def __call__(self, mode):
        log.debug('Loading {} from {} with columns {}'.format(
            mode.get_tree_name, config.data_store, self.requested_columns
        ))
        with pd.get_store(config.data_store) as store:
            df = store.select(mode.get_tree_name(),
                              columns=self.requested_columns)
            ret = self._func(df)
        return ret
