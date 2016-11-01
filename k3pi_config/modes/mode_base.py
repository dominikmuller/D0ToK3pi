import operator
import os

from k3pi_config import filelists, config
from itertools import product
import pandas as pd


class ModeConfig(Exception):

    def __init__(self, message):
        super(ModeConfig, self).__init__(message)


class mode_base(object):
    """Class to hold the basic mode configuration.
    """

    def specific_selection(self):
        pass

    def __init__(self, polarity=None, year=None):
        self.polarity = polarity
        self.year = year
        self.files = []
        if polarity:
            pols = [polarity]
        else:
            pols = [config.magup, config.magdown]
        if year:
            years = [year]
        else:
            years = [2015, 2016]

        for p, y in product(pols, years):
            self.files += getattr(filelists, 'D0ToKpipipi_{}_{}'.format(
                p, y)).paths

        # Set the default output location
        self.output_path = os.path.join(config.output_prefix, self.mode,
                                        str(self.year), polarity)

        # Get list of mother and daughter branch name prefixes
        name_getter = operator.attrgetter('name')
        self.mother_prefixes = list(map(name_getter, self.head.all_mothers()))
        self.daughter_prefixes = map(name_getter, self.head.all_daughters())
        self.daughter_prefixes = list(self.daughter_prefixes)
        if hasattr(filelists, '{}_{}_{}'.format(self.mode, polarity, year)):
            self.files = getattr(filelists, '{}_{}_{}'.format(
                self.mode, polarity, year))

    def get_tree_name(self, mc=False):
        return config.ntuple_strip.format(self.mode)

    def get_store_name(self, mc=False, polarity=None):
        if self.polarity == config.magboth and polarity is None:
            raise ModeConfig('Cannot get store for MagBoth mode. Need to'
                             ' specify polarity as an argument')
        if polarity is None:
            polarity = self.polarity
        return config.store_name.format(self.mode, polarity)

    def get_data(self, columns,  mc=False):
        with pd.get_store(config.data_store) as store:
            if self.polarity == config.magboth:
                df = store.select(
                    self.get_store_name(mc, config.magup), columns=columns)
                df = df.append(store.select(
                    self.get_store_name(mc, config.magdown), columns=columns))
            else:
                df = store.select(
                    self.get_store_name(mc), columns=columns)
        return df
