import matplotlib.pyplot as plt
import palettable
from k3pi_utilities import parser
from analysis import bdt_data
from matplotlib.backends.backend_pdf import PdfPages
from analysis.mass_fitting import get_sweights
import numpy as np
from k3pi_config.modes import gcm, MODE
from tqdm import tqdm


def sig_bkg_normed(v, sig_df, bkg_df, sig_wgt=1., bkg_wgt=1.):
    fig, ax = plt.subplots(figsize=(10, 10))
    sig_data = sig_df[v.var]
    bkg_data = bkg_df[v.var]

    nbins, xmin, xmax = v.binning

    h_sig, edges = np.histogram(
        sig_data, bins=nbins, range=(xmin, xmax), weights=sig_wgt)
    h_bkg, _ = np.histogram(
        bkg_data, bins=nbins, range=(xmin, xmax), weights=bkg_wgt)
    err_sig, _ = np.histogram(
        sig_data, bins=nbins, range=(xmin, xmax), weights=sig_wgt**2)
    err_bkg, _ = np.histogram(
        bkg_data, bins=nbins, range=(xmin, xmax), weights=bkg_wgt**2)
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

    ax.bar(x_ctr-x_err, h_bkg, width, color='#11073B',
           label='Background', edgecolor='#11073B', alpha=0.80)
    ax.bar(x_ctr-x_err, h_sig, width, color='#5F5293',
           label='Signal', edgecolor='#5F5293', alpha=0.80)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc='best')
    ax.set_xlabel(v.xlabel)
    ax.set_xlim((xmin, xmax))
    ax.set_ylim((0, 1.2))
    ax.yaxis.set_visible(False)

    return fig


def sig_sec_comb_stack(v, df):
    sweights = get_sweights(gcm())
    sig_wgt = sweights['sig']
    rpi_wgt = sweights['rnd']
    comb_wgt = sweights['comb']
    fig, ax = plt.subplots(figsize=(10, 10))
    if v.convert is None:
        data = df[v.var]
    else:
        data = v.convert(df[v.var])

    nbins, xmin, xmax = v.binning

    h_sig, edges = np.histogram(
        data, bins=nbins, range=(xmin, xmax), weights=sig_wgt)
    h_rpi, _ = np.histogram(
        data, bins=nbins, range=(xmin, xmax), weights=rpi_wgt)
    h_comb, _ = np.histogram(
        data, bins=nbins, range=(xmin, xmax), weights=comb_wgt)
    x_ctr = (edges[1:] + edges[:-1])/2.
    width = (edges[1:] - edges[:-1])
    x_err = width/2.

    colours = palettable.tableau.TableauMedium_10.hex_colors[:3]
    csig, crpi, ccomb = colours

    ax.bar(x_ctr-x_err, h_comb, width, color=ccomb,
           label='Combinatorial', edgecolor=ccomb)
    ax.bar(x_ctr-x_err, h_rpi, width, color=crpi, bottom=h_comb,
           label='Random $\pi_s$', edgecolor=crpi)
    ax.bar(x_ctr-x_err, h_sig, width, color=csig, bottom=h_comb+h_rpi,
           label='Signal', edgecolor=csig)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc='best')
    ax.set_xlabel(v.xlabel)
    ax.set_xlim((xmin, xmax))
    ax.yaxis.set_visible(False)

    return fig


def plot_bdt_variables(sw=False):
    sig_df, bkg_df, sig_wgt, bkg_wgt = bdt_data.get_bdt_data(sklearn=False)
    bdt_vars = gcm().bdt_vars + gcm().spectator_vars + gcm().just_plot

    outfile = gcm().get_output_path('sweight_fit') + 'bdt_vars.pdf'
    with PdfPages(outfile) as pdf:
        for v in tqdm(bdt_vars, smoothing=0.3):
            fig = sig_bkg_normed(v, sig_df, bkg_df, sig_wgt, bkg_wgt)
            pdf.savefig(fig)
            plt.close()
            # fig = sig_sec_comb_stack(v, df)
            # pdf.savefig(fig)
            # plt.close()


if __name__ == '__main__':
    args = parser.create_parser()
    with MODE(args.polarity, args.year, args.mode):
        plot_bdt_variables(args.sweight)
