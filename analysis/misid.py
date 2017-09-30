from k3pi_config.modes import MODE, gcm
from k3pi_utilities import parser
from analysis import final_selection, add_variables
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from k3pi_utilities import variables as vars
from k3pi_utilities import PlotConfig

from k3pi_config import config

from analysis import misid_selection


double_misid_pc = [
    PlotConfig(vars.m_C, None, (40, 1810., 1920.)),
    PlotConfig(vars.dm_C, None, (40, 140.5, 160.5)),
    PlotConfig(vars.m_SS, None, (40, 1810., 1920.)),
    PlotConfig(vars.dm_SS, None, (40, 140.5, 160.5)),
    PlotConfig(vars.m_OSH, None, (40, 1810., 1920.)),
    PlotConfig(vars.dm_OSH, None, (40, 140.5, 160.5)),
    PlotConfig(vars.m_OSL, None, (40, 1810., 1920.)),
    PlotConfig(vars.dm_OSL, None, (40, 140.5, 160.5)),
]


def misid_plots():
    """Remove wrong sign D0 candidates which are combined and end up
    in the signal window in the right sign sample"""
    # Get the necessary information from the current mode
    if gcm().mode in config.wrong_sign_modes:
        wrong_spi = add_variables.other_slowpi_ws()
    else:
        wrong_spi = add_variables.other_slowpi()

    dst_mass = gcm().get_data([vars.m(gcm().head)])[vars.m(gcm().head)]
    sel = final_selection.get_final_selection()
    bins, xmin, xmax = gcm().mass_var.binning
    ybins, ymin, ymax = gcm().dmass_var.binning
    bins = 30

    df_sel = final_selection.get_final_selection()
    misid = add_variables.double_misid()
    data = gcm().get_data([vars.dtf_dm(), vars.m(gcm().D0)])
    outfile = gcm().get_output_path('misid') + 'overview.pdf'
    with PdfPages(outfile) as pdf:
        for i, pc in enumerate(double_misid_pc):
            fig, ax = plt.subplots(figsize=(10, 10))
            nbins, xmin, xmax = pc.binning
            ax.hist(misid[df_sel][pc.var], bins=nbins, range=(xmin, xmax))
            ax.set_xlabel(pc.xlabel)
            ax.set_ylabel('Candidates')
            ax.set_xlim((xmin, xmax))
            pdf.savefig(fig)
            plt.close()
            if i % 2 == 0:
                fig, ax = plt.subplots(figsize=(10, 10))
                nbins, xmin, xmax = pc.binning
                cutvar = double_misid_pc[i+1].var
                narrow = misid[cutvar] < 147.5
                ax.hist(misid[df_sel&narrow][pc.var], bins=nbins, range=(xmin, xmax))  # NOQA
                ax.set_xlabel(pc.xlabel)
                ax.set_ylabel(r'Candidates with $\Delta m <147.5$')
                ax.set_xlim((xmin, xmax))
                pdf.savefig(fig)
                plt.close()


        cut = misid_selection.misid_cut()
        dm = gcm().dmass_var
        nbins, xmin, xmax = dm.binning

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.hist(data[dm.var][sel & cut], bins=nbins, color='#D3EFFB',  # NOQA
                range=(xmin, xmax), label='Kept', edgecolor='#D3EFFB')
        ax.hist(data[dm.var][sel & ~cut], bins=nbins,
                range=(xmin, xmax), label='Removed', color='#006EB6', edgecolor='#006EB6')  # NOQA
        ax.set_xlim((xmin, xmax))
        ax.set_xlabel(dm.xlabel)
        ax.set_ylabel('Candidates')
        ax.legend()
        pdf.savefig(fig)
        plt.clf()

    outfile = gcm().get_output_path('misid') + 'wrong_spi.pdf'
    pdf = PdfPages(outfile)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.hist(wrong_spi[sel], bins=bins, range=(xmin, xmax), normed=True, color='#006EB6', edgecolor='#006EB6')  # NOQA
    ax.set_xlabel(gcm().mass_var.xlabel)
    ax.set_xlim((xmin, xmax))
    ax.set_ylabel('Arbitrary units')
    pdf.savefig(fig)

    fig, ax = plt.subplots(figsize=(10, 10))

    ax.hist((dst_mass - wrong_spi)[sel], bins=ybins, range=(ymin, ymax), color='#006EB6', edgecolor='#006EB6')  # NOQA
    ax.set_xlabel(gcm().dmass_var.xlabel)
    ax.set_xlim((xmin, xmax))
    pdf.savefig(fig)
    plt.clf()
    plt.clf()

    pdf.close()


if __name__ == '__main__':
    args = parser.create_parser()
    with MODE(args.polarity, args.year, args.mode):
        misid_plots()
