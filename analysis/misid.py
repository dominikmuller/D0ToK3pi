from k3pi_config.modes import MODE, gcm
from k3pi_utilities import parser
from analysis import final_selection, add_variables
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from k3pi_utilities import variables as vars

from k3pi_config import config


def misid_plots():
    """Remove wrong sign D0 candidates which are combined and end up
    in the signal window in the right sign sample"""
    # Get the necessary information from the current mode
    mis_id = add_variables.double_misid_d0()
    if gcm().mode in config.wrong_sign_modes:
        wrong_spi = add_variables.other_slowpi_ws()
    else:
        wrong_spi = add_variables.other_slowpi()

    dst_mass = gcm().get_data([vars.m(gcm().head)])[vars.m(gcm().head)]
    sel = final_selection.get_final_selection()
    bins, xmin, xmax = gcm().mass_var.binning
    ybins, ymin, ymax = gcm().dmass_var.binning
    bins = 30

    outfile = gcm().get_output_path('misid') + 'misid.pdf'
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.hist(mis_id[sel], bins=bins, range=(xmin, xmax))
    ax.set_xlabel(gcm().mass_var.xlabel)
    ax.yaxis.set_visible(False)
    plt.savefig(outfile)
    plt.clf()

    outfile = gcm().get_output_path('misid') + 'wrong_spi.pdf'
    pdf = PdfPages(outfile)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.hist(wrong_spi[sel], bins=bins, range=(xmin, xmax))
    ax.set_xlabel(gcm().mass_var.xlabel)
    ax.yaxis.set_visible(False)
    pdf.savefig(fig)

    fig, ax = plt.subplots(figsize=(10, 10))

    ax.hist((dst_mass - wrong_spi)[sel], bins=ybins, range=(ymin, ymax))
    ax.set_xlabel(gcm().dmass_var.xlabel)
    ax.yaxis.set_visible(False)
    pdf.savefig(fig)
    plt.clf()
    plt.clf()

    # fig, ax = plt.subplots(figsize=(10, 10))
    # ax.hist2d(wrong_spi[sel], bins=bins, range=(xmin, xmax))
    # ax.set_xlabel(gcm().mass_var.xlabel)
    # ax.yaxis.set_visible(False)
    # pdf.savefig(fig)
    # plt.clf()

    pdf.close()


if __name__ == '__main__':
    args = parser.create_parser()
    with MODE(args.polarity, args.year, args.mode):
        misid_plots()
