from k3pi_utilities.variables import eta, probnnk, probnnpi, p, m, dm, dtf_dm
from k3pi_utilities.variables import ipchi2, probnnghost
from k3pi_utilities.selective_load import selective_load
from k3pi_utilities.buffer import buffer_load
from k3pi_utilities.debugging import call_debug
from k3pi_utilities import parser
from k3pi_config import config, get_mode
import numpy as np


@buffer_load
@selective_load
@call_debug
def pid_selection(df, mode):
    ret = True
    for kaon in mode.head.all_pid(config.kaon):
        ret &= (df[probnnk(kaon)] > 0.3) & (df[probnnpi(kaon)] < 0.7)
    for pion in mode.head.all_pid(config.pion):
        ret &= (df[probnnpi(pion)] > 0.3) & (df[probnnk(pion)] < 0.7)
    return ret


@buffer_load
@selective_load
@call_debug
def pid_fiducial_selection(df, mode):
    ret = True
    for part in mode.D0.all_daughters():
        ret &= (df[p(part)] >= 3000.)
        ret &= (df[p(part)] < 100000.)
        ret &= (df[eta(part)] >= 2.)
        ret &= (df[eta(part)] < 5.)

    return ret


@buffer_load
@selective_load
@call_debug
def mass_fiducial_selection(df, mode):
    ret = True
    ret &= (np.abs(df[m(mode.D0)] - config.PDG_MASSES[config.Dz] - 5.) < 60)
    ret &= (df[dtf_dm()] >= 140.5)
    ret &= (df[dtf_dm()] < 160.5)

    return ret


@buffer_load
@selective_load
@call_debug
def remove_secondary(df, mode):
    return np.log(df[ipchi2(mode.D0)]) < 2.


@buffer_load
@selective_load
@call_debug
def slow_pion(df, mode):
    ret = (df[probnnghost(mode.Pislow)] < 0.3)
    ret &= (df[probnnpi(mode.Pislow)] > 0.3)
    ret &= (df[probnnk(mode.Pislow)] < 0.7)

    return ret


@buffer_load
@call_debug
def full_selection(mode):
    sel = pid_selection(mode)
    sel &= pid_fiducial_selection(mode)
    sel &= mass_fiducial_selection(mode)
    if mode.mode not in config.twotag_modes:
        sel &= remove_secondary(mode)
    sel &= slow_pion(mode)
    return sel


if __name__ == '__main__':
    import sys
    args = parser.create_parser()
    mode = get_mode(args.polarity, args.year, args.mode)

    if args.selections is None:
        sels = [
            'pid_selection',
            'pid_fiducial_selection',
            'mass_fiducial_selection',
            'remove_secondary',
            'slow_pion'
        ]
    else:
        sels = args.selections

    for sel in sels:
        getattr(sys.modules[__name__], sel)(mode, False)
