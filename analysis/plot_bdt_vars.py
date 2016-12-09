from k3pi_config import get_mode, config
import matplotlib.pyplot as plt
from k3pi_utilities import parser
from k3pi_utilities import variables as vars
from matplotlib.backends.backend_pdf import PdfPages
from analysis.mass_fitting import get_sweights
from analysis import add_variables
import numpy as np
from analysis import selection
from tqdm import tqdm


def plot_bdt_variables(mode):
    bdt_vars = mode.bdt_vars
    df = mode.get_data([v.var for v in bdt_vars])
    add_variables.append_angle(df, mode)
    sel = selection.pid_selection(mode)
    sel &= selection.pid_fiducial_selection(mode)
    sel &= selection.mass_fiducial_selection(mode)
    if mode.mode not in config.twotag_modes:
        sel &= selection.remove_secondary(mode)
    sel &= selection.slow_pion(mode)

    df = df[sel]
    sweights = get_sweights(mode)
    nbins = 40
    sig_wgt = sweights['sig']
    bkg_wgt = sweights['rnd'] + sweights['comb']
    outfile = mode.get_output_path('sweight_fit') + 'bdt_vars.pdf'
    with PdfPages(outfile) as pdf:
        for v in tqdm(bdt_vars, smoothing=0.3):
            fig, ax = plt.subplots(figsize=(10, 10))
            if v.convert is None:
                data = df[v.var]
            else:
                data = v.convert(df[v.var])

            nbins, xmin, xmax = v.binning

            h_sig, edges = np.histogram(
                data, bins=nbins, range=(xmin, xmax), weights=sig_wgt)
            h_bkg, _ = np.histogram(
                data, bins=nbins, range=(xmin, xmax), weights=bkg_wgt)
            err_sig, _ = np.histogram(
                data, bins=nbins, range=(xmin, xmax), weights=sig_wgt**2)
            err_bkg, _ = np.histogram(
                data, bins=nbins, range=(xmin, xmax), weights=bkg_wgt**2)
            x_ctr = (edges[1:] + edges[:-1])/2.
            width = (edges[1:] - edges[:-1])
            x_err = width/2.

            err_sig = np.sqrt(err_sig)
            err_bkg = np.sqrt(err_bkg)

            n_sig = h_sig.max()
            n_bkg = h_bkg.max()

            h_bkg = h_bkg*1./float(n_bkg)
            err_bkg /= float(n_bkg)

            h_sig = h_sig*1./float(n_sig)
            err_sig /= float(n_sig)

            ax.bar(x_ctr-x_err, h_bkg, width, color='#11073B', linewidth=0,
                   label='Background', edgecolor='#11073B', alpha=0.80)
            ax.bar(x_ctr-x_err, h_sig, width, color='#5F5293', linewidth=0,
                   label='Signal', edgecolor='#5F5293', alpha=0.80)

            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles[::-1], labels[::-1], loc='best')
            ax.set_xlabel(v.xlabel)
            ax.set_xlim((xmin, xmax))
            ax.set_ylim((0, 1.2))
            ax.yaxis.set_visible(False)

            pdf.savefig(fig)
            plt.close()



if __name__ == '__main__':
    args = parser.create_parser()
    mode = get_mode(args.polarity, args.year, args.mode)
    plot_bdt_variables(mode)
