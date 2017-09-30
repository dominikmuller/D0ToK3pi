from k3pi_config.modes import MODE, gcm
from k3pi_config import config
from k3pi_utilities import parser
from matplotlib.backends.backend_pdf import PdfPages
from k3pi_plotting import utils as plot_utils
from analysis.final_selection import get_final_selection
from k3pi_utilities import variables as vars
import matplotlib.pyplot as plt
import numpy as np


def plot_mass_regions():
    sel = get_final_selection()
    df = gcm().get_data([vars.m(gcm().D0), vars.dtf_dm()])

    selected = df[sel]

    nbins = 100
    name = 'mass_regions'
    if config.optimised_selection:
        name += '_opt'
    if config.candidates_selection:
        name += '_cand'
    outfile = gcm().get_output_path('selection') + name + '.pdf'
    with PdfPages(outfile) as pdf:

        fig, ax = plt.subplots(figsize=(10, 10))

        # Doing D0 mass first
        xmin, xmax = 1810, 1920

        # Signal window boundaries
        sw_lo = config.PDG_MASSES['D0'] - 18.
        sw_hi = config.PDG_MASSES['D0'] + 18.
        # Lower sideband boundaries
        sb_lo_lo = xmin
        sb_lo_hi = config.PDG_MASSES['D0'] - 30.
        # Upper sideband boundaries
        sb_hi_lo = config.PDG_MASSES['D0'] + 30.
        sb_hi_hi = xmax

        bkg = np.array([(sb_lo_hi + sb_lo_lo)/2., (sb_hi_hi + sb_hi_lo)/2.])
        bkgw = np.array([(sb_lo_hi - sb_lo_lo), (sb_hi_hi - sb_hi_lo)])
        sig = np.array([(sw_lo + sw_hi)/2.])
        sigw = np.array([(sw_hi - sw_lo)])

        h_vals, edges = np.histogram(
            selected[vars.m(gcm().D0)], bins=nbins, range=(xmin, xmax))
        h_errorbars = np.sqrt(h_vals)

        x_ctr = (edges[1:] + edges[:-1])/2.
        width = (edges[1:] - edges[:-1])
        x_err = width/2.

        dt_options = dict(
            fmt='o', markersize=5, capthick=1, capsize=0, elinewidth=2,
            color='#000000', markeredgecolor='#000000')
        ax.errorbar(
            x_ctr, h_vals, xerr=x_err, yerr=h_errorbars, **dt_options)

        hmax = np.max(ax.lines[0].get_ydata())

        ax.bar(sig, 1.10*np.array(hmax), sigw, color='#D3EFFB',
               edgecolor='#D3EFFB', label='Signal', alpha=0.5)
        ax.bar(bkg, 1.10*np.ones(len(bkg))*hmax, bkgw, label='Background',
               color='#006EB6', edgecolor='#006EB6', alpha=0.5)
        ax.set_xlabel(vars.m.latex((gcm().D0), with_unit=True))

        unit = r'{} {}'.format((xmax-xmin)/nbins, vars.m.unit)
        ylabel = r'Candidates / ({0})'.format(unit)
        ax.set_ylabel(ylabel)
        ax.legend()
        ax.set_xlim(xmin, 0.9999*xmax)

        plot_utils.y_margin_scaler(ax, lf=0, la=True)
        pdf.savefig(fig)
        plt.clf()

        # Now delta mass
        fig, ax = plt.subplots(figsize=(10, 10))
        xmin, xmax = 140.5, 152.5

        # Signal window boundaries
        sw_lo = config.PDG_MASSES['delta'] - 0.5
        sw_hi = config.PDG_MASSES['delta'] + 0.5
        # Lower sideband boundaries
        sb_lo_lo = xmin
        sb_lo_hi = config.PDG_MASSES['delta'] - 2.3
        # Upper sideband boundaries
        sb_hi_lo = config.PDG_MASSES['delta'] + 2.3
        sb_hi_hi = xmax

        bkg = np.array([(sb_lo_hi + sb_lo_lo)/2., (sb_hi_hi + sb_hi_lo)/2.])
        bkgw = np.array([(sb_lo_hi - sb_lo_lo), (sb_hi_hi - sb_hi_lo)])
        sig = np.array([(sw_lo + sw_hi)/2.])
        sigw = np.array([(sw_hi - sw_lo)])

        h_vals, edges = np.histogram(
            selected[vars.dtf_dm()], bins=nbins, range=(xmin, xmax))
        h_errorbars = np.sqrt(h_vals)

        x_ctr = (edges[1:] + edges[:-1])/2.
        width = (edges[1:] - edges[:-1])
        x_err = width/2.

        ax.errorbar(
            x_ctr, h_vals, xerr=x_err, yerr=h_errorbars, **dt_options)

        hmax = np.max(ax.lines[0].get_ydata())

        ax.bar(sig, 1.10*np.array(hmax), sigw, color='#D3EFFB',
               edgecolor='#D3EFFB', label='Signal', alpha=0.5)
        ax.bar(bkg, 1.10*np.ones(len(bkg))*hmax, bkgw, label='Background',
               color='#006EB6', edgecolor='#006EB6', alpha=0.5)
        ax.set_xlabel(vars.dtf_dm.latex(with_unit=True))
        unit = r'{} {}'.format((xmax-xmin)/nbins, vars.dtf_dm.unit)
        ylabel = r'Candidates / ({0})'.format(unit)
        ax.set_ylabel(ylabel)
        ax.legend()
        ax.set_xlim(xmin, 0.9999*xmax)

        plot_utils.y_margin_scaler(ax, lf=0, la=True)
        pdf.savefig(fig)
        plt.clf()

if __name__ == '__main__':
    args = parser.create_parser()
    with MODE(args.polarity, args.year, args.mode):
        plot_mass_regions()
