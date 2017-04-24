# from analysis.mass_fitting import run_spearmint_fit, run_spearmint_sweights
from k3pi_utilities.helpers import quiet_mode
from analysis.bdt_studies import get_bdt_discriminant
from analysis import selection
from k3pi_config.modes import MODE
import numpy as np



def run_it(params):
    quiet_mode(True)
    # pid_cuts = ['min_pi_nnpi', 'max_pi_nnk', 'min_k_nnk', 'max_k_nnpi']
    spi_cuts = ['min_spi_nnpi', 'max_spi_nnk', 'max_spi_nnghost', 'max_spi_nnp']


    # pid_cut_values = {
        # n: params[n][0] for n in pid_cuts
    # }

    spi_cut_values = {
        n: params[n][0] for n in spi_cuts
    }

    # Get the signal stuff
    with MODE('MagBoth', 1516, 'RS'):
        signal = selection.mass_signal_region()
        bdt = get_bdt_discriminant()
        bdt_sel = bdt['comb_bkg_bdt'] > params['BDT_CUT'][0]
        bdt_sel &= bdt['rand_spi_bdt'] > params['BDT_CUT2'][0]
        spi = selection._apply_slow_pion_cut(**spi_cut_values)
        sel = selection.full_selection()
        supersel = bdt_sel & spi & sel
        sig0 = float(signal[sel].sum())/300.
        sig = float(signal[supersel].sum())/300.

    # Get the Background stuff
    with MODE('MagBoth', 1516, 'WS'):
        background = selection.mass_sideband_region()
        bdt = get_bdt_discriminant()
        bdt_sel = bdt['comb_bkg_bdt'] > params['BDT_CUT'][0]
        bdt_sel &= bdt['rand_spi_bdt'] > params['BDT_CUT2'][0]
        spi = selection._apply_slow_pion_cut(**spi_cut_values)
        sel = selection.full_selection()
        supersel = bdt_sel & spi & sel
        bkg = float(background[supersel].sum())/15.4

    print 'sig0 =', sig0
    print 'sig =', sig
    print 'bkg =', bkg

    ret = -(sig/sig0)/(0.5 + np.sqrt(bkg))
    return ret

    # return run_spearmint_fit(bdt & pid & spi)


def main(job_id, params):
    return run_it(params)

if __name__ == '__main__':
    params = {
        'max_spi_nnp': [0.5],
        'min_spi_nnpi': [0.300000],
        'max_spi_nnghost': [0.050000],
        'max_spi_nnk': [0.50000],
        'BDT_CUT': [0.2000],
        'BDT_CUT2': [0.4000],
    }
    print main(1, params)
