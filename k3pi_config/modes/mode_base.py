import operator
import os

from k3pi_config import filelists, config
from itertools import product
import pandas as pd
from k3pi_utilities import helpers


class ModeConfig(Exception):

    def __init__(self, message):
        super(ModeConfig, self).__init__(message)


class mode_base(object):

    """Class to hold the basic mode configuration.
    """

    def specific_selection(self):
        pass

    def __init__(self, polarity, year):
        self.polarity = polarity
        self.year = year
        self.files = []
        if polarity == config.magboth:
            pols = [config.magup, config.magdown]
        else:
            pols = [polarity]
        if year:
            years = [year]
        else:
            years = [2015, 2016]

        if self.mode in config.twotag_modes:
            _fl_template = 'D0ToKpipipi_2tag_{}_{}'
        else:
            _fl_template = 'D0ToKpipipi_{}_{}'

        for p, y in product(pols, years):
            self.files += getattr(filelists, _fl_template.format(
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
                    self.get_store_name(mc, config.magdown), columns=columns),
                    ignore_index=True
                )
            else:
                df = store.select(
                    self.get_store_name(mc), columns=columns)
        return df

    def get_output_path(self, extra=None):
        path = config.output_mode.format(self.mode, self.year, self.polarity)
        if extra is not None:
            path += extra
        if path[-1] != '/':
            path += '/'
        helpers.ensure_directory_exists(path)
        return path

    def get_rf_vars(self, identifier):
        if identifier not in self.mass_fit_pars:
            raise ModeConfig('No information on parameter given.')
        val = self.mass_fit_pars[identifier]
        if 'fix_' + identifier in self.mass_fit_pars and \
                self.mass_fit_pars['fix_' + identifier]:
            return val
        if 'limit_' + identifier in self.mass_fit_pars:
            low, high = self.mass_fit_pars['limit_' + identifier]
            return identifier + '[{}, {}, {}]'.format(val, low, high)
        return identifier + '[{}]'.format(val)
