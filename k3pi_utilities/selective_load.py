from collections import defaultdict
from k3pi_config import config
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
        self.__name__ = function.__name__
        self.__doc__ = function.__doc__

    def __call__(self, mode):
        df = mode.get_data(self.requested_columns[mode.mode])
        ret = self._func(df, mode)
        del df
        return ret
