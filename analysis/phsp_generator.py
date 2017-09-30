from k3pi_utilities.debugging import call_debug
from k3pi_cpp import t_gen_phasespaced
from k3pi_config import config
from k3pi_config.modes.D0ToKpipipi_RS import D0ToKpipipi_RS as mode_config
from k3pi_utilities import variables as vars
import pandas as pd
import numpy as np
import shutil
import bcolz

from k3pi_utilities import logger

log = logger.get_logger('phsp_generator')


@call_debug
def generate(nevents=10000000):
    """Generates and returns phase-space MC for a 4 body decay of K3pi.
    Decay is generated using TGenPhaseSpace and a decaytime is added
    from an exponential with lifetime 0.00040995 ns.

    Generated sample is cached based on the size and only redone if the number
    changes of no cached results are found.
    """

    bcolz_folder = config.bcolz_locations.format('generated_phasespace')
    try:
        bc = bcolz.open(bcolz_folder)
        if bc.size == nevents:
            log.info('Returning stored PHSP')
            return bc.todataframe()
        else:
            log.info('Removing stored PHSP')
            del bc
            shutil.rmtree(bcolz_folder)
    except IOError:
        log.info('No stored PHSP')
        pass

    vals = t_gen_phasespaced(nevents)
    df = pd.DataFrame({'m12': vals[0], 'm34': vals[1], 'cos1': vals[2],
                       'cos2': vals[3], 'phi1': vals[4]})
    df['D0_Loki_BPVLTIME'] = np.random.exponential(
        0.00040995, size=df.index.size)
    bcolz.ctable.fromdataframe(df, rootdir=bcolz_folder)

    return df


def two_parts_generate(turn=0.6, size=1):
    imp_samp_time=1.
    int_left = 0.5*np.exp(-turn/imp_samp_time)/turn*turn**2 - 0.5*np.exp(-turn/imp_samp_time)/turn*0.1725**2
    int_right = (-imp_samp_time*np.exp(-3.26/imp_samp_time)+imp_samp_time*np.exp(-turn/imp_samp_time))
    fl = int_left/(int_left+int_right)
    left = np.random.triangular(0, turn, turn, size=int(fl*size*3.0))
    left = left[left>0.1725][:int(fl*size)]
    right = np.random.exponential(imp_samp_time, size=int((size-int(fl*size))*1.4)) + turn
    return np.append(left, right[right<3.26][:size-int(fl*size)])


def phsp_goofit(flat_ltime=False):
    import root_pandas
    # path = 'root://eoslhcb.cern.ch//eos/lhcb/user/d/dmuller/K3Pi/RS_with_weight.root'
    path = 'root://eoslhcb.cern.ch//eos/lhcb/user/d/dmuller/K3Pi/phsp_mc.root'
    df = root_pandas.read_root(path, 'events', stop=15000000)
    df.rename(
        columns={'c12': vars.cos1(),
                 'c34': vars.cos2(),
                 'dtime': vars.ltime(mode_config.D0),
                 'phi': vars.phi1(),
                 'm12': vars.m12(),
                 'm34': vars.m34()},
        inplace=True)
    df[vars.m12()] = df[vars.m12()] * 1000.
    df[vars.m34()] = df[vars.m34()] * 1000.
    if flat_ltime:
        df['D0_Loki_BPVLTIME'] = np.random.uniform(
            0.0001725, 0.00326, size=df.index.size)
    else:
        df['D0_Loki_BPVLTIME'] = two_parts_generate(
            turn=0.55, size=df.index.size)/1000.

    return df


def phsp_goofit_alt():
    import root_pandas
    path = 'root://eoslhcb.cern.ch//eos/lhcb/user/d/dmuller/K3Pi/RS_with_weight_dtime.root'
    df = root_pandas.read_root(path, 'events')
    df.rename(
        columns={'c12': vars.cos1(),
                 'c34': vars.cos2(),
                 'dtime': vars.ltime(mode_config.D0),
                 'phi': vars.phi1(),
                 'm12': vars.m12(),
                 'm34': vars.m34()},
        inplace=True)
    df[vars.m12()] = df[vars.m12()] * 1000.
    df[vars.m34()] = df[vars.m34()] * 1000.
    df['D0_Loki_BPVLTIME'] = df['D0_Loki_BPVLTIME']/1000.

    return df
