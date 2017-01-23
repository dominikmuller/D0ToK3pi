from k3pi_utilities.variables import (eta, probnnk, probnnpi, p, m, dtf_dm,
                                      probnnmu, dtf_chi2)
from k3pi_utilities.variables import ipchi2, probnnghost
from k3pi_utilities.selective_load import selective_load
from k3pi_utilities.buffer import buffer_load
from k3pi_utilities.debugging import call_debug
from k3pi_utilities import parser
from k3pi_config.modes import gcm, MODE
from k3pi_config import config
import numpy as np


@buffer_load
@selective_load
@call_debug
def pid_selection(df):
    ret = True
    for kaon in gcm().head.all_pid(config.kaon):
        ret &= (df[probnnk(kaon)] > 0.3) & (df[probnnpi(kaon)] < 0.7)
    for pion in gcm().head.all_pid(config.pion):
        ret &= (df[probnnpi(pion)] > 0.3) & (df[probnnk(pion)] < 0.7)
    return ret


@buffer_load
@selective_load
@call_debug
def pid_fiducial_selection(df):
    ret = True
    for part in gcm().D0.all_daughters():
        ret &= (df[p(part)] >= 3000.)
        ret &= (df[p(part)] < 100000.)
        ret &= (df[eta(part)] >= 2.)
        ret &= (df[eta(part)] < 5.)

    return ret


@buffer_load
@selective_load
@call_debug
def mass_fiducial_selection(df):
    ret = True
    ret &= (df[m(gcm().D0)] >= 1810.)
    ret &= (df[m(gcm().D0)] < 1920.)
    ret &= (df[dtf_dm()] >= 140.5)
    ret &= (df[dtf_dm()] < 160.5)

    return ret


@buffer_load
@selective_load
@call_debug
def remove_secondary(df):
    return np.log(df[ipchi2(gcm().D0)]) < 1.


@buffer_load
@selective_load
@call_debug
def slow_pion(df):
    ret = (df[probnnghost(gcm().Pislow)] < 0.3)
    ret &= (df[probnnpi(gcm().Pislow)] > 0.3)
    ret &= (df[probnnk(gcm().Pislow)] < 0.7)
    ret &= (df[probnnmu(gcm().Pislow)] < 0.1)

    return ret


@buffer_load
@selective_load
@call_debug
def dtf_cuts(df):
    ret = (df[dtf_chi2(gcm().head)] < 60.)
    return ret


@buffer_load
@call_debug
def full_selection():
    sel = pid_selection()
    sel &= pid_fiducial_selection()
    sel &= mass_fiducial_selection()
    if gcm().mode not in config.twotag_modes:
        sel &= remove_secondary()
    sel &= slow_pion()
    sel &= dtf_cuts()
    return sel


@buffer_load
@selective_load
@call_debug
def mass_signal_region(df):
    ret = True
    ret &= np.abs(df[m(gcm().D0)] - config.PDG_MASSES['D0']) < 20.
    ret &= np.abs(df[dtf_dm()] - config.PDG_MASSES['delta']) < 0.5
    return ret


@buffer_load
@selective_load
@call_debug
def mass_sideband_region(df):
    ret = True
    ret &= np.abs(df[m(gcm().D0)] - config.PDG_MASSES['D0']) > 30.
    ret &= np.abs(df[dtf_dm()] - config.PDG_MASSES['delta']) > 2.0
    return ret


if __name__ == '__main__':
    import sys
    args = parser.create_parser()

    if args.selections is None:
        sels = [
            'pid_selection',
            'pid_fiducial_selection',
            'mass_fiducial_selection',
            'remove_secondary',
            'slow_pion',
            'full_selection',
            'mass_signal_region',
            'mass_sideband_region',
            'dtf_cuts'
        ]
    else:
        sels = args.selections

    with MODE(args.polarity, args.year, args.mode):
        for sel in sels:
            getattr(sys.modules[__name__], sel)(use_buffered=False)
