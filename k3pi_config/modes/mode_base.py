import operator
import os

from k3pi_config import filelists, config


class mode_base(object):
    """Class to hold the basic mode configuration.
    """

    def specific_selection(self):
        pass

    def __init__(self, polarity, year):
        self.polarity = polarity
        self.year = year

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
