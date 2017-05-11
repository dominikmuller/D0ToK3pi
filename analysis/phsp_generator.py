from k3pi_utilities.debugging import call_debug
from k3pi_cpp import t_gen_phasespaced
from k3pi_config import config
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
