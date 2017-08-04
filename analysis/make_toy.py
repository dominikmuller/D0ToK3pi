from __future__ import print_function
import root_pandas
import numpy as np

"""
This script creates a toy sample from previously prepared large samples
of signal and background events which already have the respective efficiencies
computed.
"""

sig_file_name = 'root://eoslhcb.cern.ch//eos/lhcb/user/d/dmuller/K3Pi/signal_toy_data.root'  # NOQA
bkg_file_name = 'root://eoslhcb.cern.ch//eos/lhcb/user/d/dmuller/K3Pi/background_toy_data.root'  # NOQA
toy_file_name = 'toy_data.root'

np.random.seed()

nSignal = 110000
nBackground = 105000

# Generate the actual number of signal events for the two toys
iSignal = np.random.poisson(nSignal)
iBackground = np.random.poisson(nBackground)
print(
    'Toy will be generated with {} signal and {} background events'.format(
        iSignal,
        iBackground))

# Getting the data files

SIG = root_pandas.read_root(sig_file_name)
BKG = root_pandas.read_root(bkg_file_name)

print(
    'Loaded {} raw signal and {} row background events'.format(
        SIG.index.size,
        BKG.index.size))

# Creating the toy sample
print('Creating the toy data')
sample = SIG.sample(iSignal, replace=True, weights='eff')
sample = sample.append(
    BKG.sample(
        iBackground,
        replace=True,
        weights='eff'),
    ignore_index=True)

sample.to_root(toy_file_name)
