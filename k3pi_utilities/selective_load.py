from collections import defaultdict
from k3pi_config import config
from k3pi_utilities import get_logger
from k3pi_config import modes, get_mode
from k3pi_config.modes import gcm
from itertools import product
import inspect


accumulated_per_mode = defaultdict(lambda: set())


class selective_load():
    """Decorator which converts removes the dataframe argument and loads the
    necessary data by dummy calling the function with a defaultdict. If the
    decorated function needs mode as argument it passes gcm() [Done for
    backwards compatibility] unless mode is supplied as argument."""
    def __init__(self, function, allow_for=None):
        if allow_for is not None:
            self.allow_for = allow_for
        else:
            self.allow_for = [None, 'mc', 'gen']
        self.requested_columns = {}
        self._wants_mode = 'mode' in inspect.getargspec(function).args
        self.log = get_logger(function.__name__)
        for m, mc in product(config.all_modes_short, self.allow_for):
            d = defaultdict(lambda: 1)
            # Dummy call the selection classes with the mode classes to get
            # the different variables needed.
            if self._wants_mode:
                mode_cls = get_mode('MagDown', 2015, m, mc)
                function(d, mode_cls)
            else:
                with modes.MODE('MagDown', 2015, m, mc):
                    function(d)
            look_up = m
            if mc is not None:
                look_up += mc
            self.requested_columns[look_up] = d.keys()
            [accumulated_per_mode[look_up].add(n) for n in d.keys()]
        self._wants_mode = 'mode' in inspect.getargspec(function).args
        self._func = function
        self._func_name = function.__name__
        self.__name__ = function.__name__
        self.__doc__ = function.__doc__

    def __call__(self, mode=None, *args, **kwargs):
        if mode is None:
            mode = gcm()
        if mode.mc not in self.allow_for:
            raise KeyError('Cannot call {} with {}'.format(
                self.__name__, mode.mc))
        look_up = mode.mode_short
        if mode.mc is not None:
            look_up += mode.mc

        self.log.debug(
            'Looked up {} -> loading [{}]'.format(
                look_up, ', '.join(
                    self.requested_columns[look_up])))
        df = mode.get_data(self.requested_columns[look_up])
        if self._wants_mode:
            ret = self._func(df, mode, *args, **kwargs)
        else:
            ret = self._func(df, *args, **kwargs)
        del df
        return ret
