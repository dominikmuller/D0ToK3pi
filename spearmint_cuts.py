# from analysis.mass_fitting import run_spearmint_fit, run_spearmint_sweights
from k3pi_utilities.helpers import quiet_mode
from analysis.bdt_studies import get_bdt_discriminant
from analysis import selection
from k3pi_config.modes import MODE
import numpy as np



def run_it(params):
    quiet_mode(True)
    pid_cuts = ['min_pi_nnpi', 'max_pi_nnk', 'min_k_nnk', 'max_k_nnpi']
    spi_cuts = ['min_spi_nnpi', 'max_spi_nnk', 'max_spi_nnghost', 'max_spi_nnp']

    bdt = get_bdt_discriminant() > params['BDT_CUT'][0]

    pid_cut_values = {
        n: params[n][0] for n in pid_cuts
    }

    spi_cut_values = {
        n: params[n][0] for n in spi_cuts
    }

    pid = selection._apply_pid_cut(**pid_cut_values)
    spi = selection._apply_slow_pion_cut(**spi_cut_values)
    print 'Global efficiency', float(np.sum(bdt & pid & spi))/bdt.index.size
    supersel = bdt & pid & spi
    signal = selection.mass_signal_region()
    background = selection.mass_sideband_region()
    sig0 = float(signal.sum())
    sig = float(signal[supersel].sum())
    bkg = float(background[supersel].sum())
    print 'sig0 =', sig0
    print 'sig =', sig
    print 'bkg =', bkg

    ret = -(sig/sig0)/(0.5 + np.sqrt(bkg))
    return ret

    # return run_spearmint_fit(bdt & pid & spi)


def main(job_id, params):
    with MODE('MagBoth', 2015, 'WS'):
        return run_it(params)

if __name__ == '__main__':
    params = {
        'max_k_nnpi': [0.050000],
        'max_spi_nnp': [0.05],
        'min_pi_nnpi': [0.300000],
        'min_spi_nnpi': [0.300000],
        'min_k_nnk': [0.300000],
        'max_spi_nnghost': [0.050000],
        'max_pi_nnk': [0.050000],
        'max_spi_nnk': [0.050000],
        'BDT_CUT': [0.6000],
    }
    print main(1, params)
