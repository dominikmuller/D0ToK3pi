from analysis import add_variables
from k3pi_utilities import variables as vars
from k3pi_utilities import PlotConfig

from k3pi_config import config
from k3pi_utilities.buffer import buffer_load, remove_buffer_for_function
from k3pi_utilities.debugging import call_debug
import numpy as np
import sys


double_misid_pc = [
    PlotConfig(vars.m_SS, None, (100, 1810., 1920.)),
    PlotConfig(vars.dm_SS, None, (100, 140.5, 160.5)),
    PlotConfig(vars.m_OSH, None, (100, 1810., 1920.)),
    PlotConfig(vars.dm_OSH, None, (100, 140.5, 160.5)),
    PlotConfig(vars.m_OSL, None, (100, 1810., 1920.)),
    PlotConfig(vars.dm_OSL, None, (100, 140.5, 160.5)),
]


@buffer_load
@call_debug
def misid_cut():
    misid = add_variables.double_misid()
    # cut = (((misid.m_OSH-config.PDG_MASSES['D0'])/30.)**2 + ((misid.dm_OSH-config.PDG_MASSES['delta'])/2.)**2.)> 1.
    # cut &= (((misid.m_OSL-config.PDG_MASSES['D0'])/30.)**2 + ((misid.dm_OSL-config.PDG_MASSES['delta'])/2.)**2.)> 1.
    cut = ~((np.abs(misid.m_OSH-config.PDG_MASSES['D0'])<30.))  # & (np.abs(misid.dm_OSH-config.PDG_MASSES['delta'])<2.))
    cut &= ~((np.abs(misid.m_OSL-config.PDG_MASSES['D0'])<30.))  # & (np.abs(misid.dm_OSL-config.PDG_MASSES['delta'])<2.))
    return cut


if __name__ == '__main__':
    funcs = [
        'misid_cut',
    ]
    for sel in funcs:
        remove_buffer_for_function(getattr(sys.modules[__name__], sel))
