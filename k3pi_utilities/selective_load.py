from collections import defaultdict
import logging as log
import root_pandas

accumulated = set()

class selective_load():
    def __init__(self, function):
        d = defaultdict(lambda: 1)
        function(d)
        self.requested_columns = d.keys()
        [accumulated.add(n) for n in d.keys()]
        self._func = function

    def __call__(self, files, key):
        log.debug('Loading {} from {} with columns {}'.format(
            key, files, self.requested_columns
        ))
        df = root_pandas.read_root(files, key,
                                   columns=self.requested_columns)
        ret = self._func(df)
        # del df
        return ret
