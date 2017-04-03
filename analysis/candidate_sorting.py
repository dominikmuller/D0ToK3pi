from k3pi_config.modes import MODE, gcm
from k3pi_utilities import parser
from matplotlib.backends.backend_pdf import PdfPages
from analysis import extended_selection, selection
from k3pi_utilities import variables as vars
from k3pi_utilities import selective_load, buffer
import matplotlib.pyplot as plt
import seaborn.apionly as sns
import numpy as np
import pandas as pd

from k3pi_config import config


@buffer.buffer_load
def remove_right_sign_candidates():
    """Remove wrong sign D0 candidates which are combined and end up
    in the signal window in the right sign sample"""
    # Get the necessary information from the current mode
    year = gcm().year
    polarity = gcm().polarity
    polarity = gcm().polarity
    if gcm().mode not in config.twotag_modes:
        rs, ws = 'RS', 'WS'
    else:
        rs, ws = '2tag_RS', '2tag_WS'
    with MODE(polarity, year, rs):
        RS = gcm().get_data([vars.evt_num(), vars.dtf_dm(), vars.pt(gcm().D0)])
        rs_sel = extended_selection.get_complete_selection(False)
    # RS modes should not be selected using this:
    if gcm().mode not in config.wrong_sign_modes:
        return pd.Series(True, RS.index)

    with MODE(polarity, year, ws):
        WS = gcm().get_data([vars.evt_num(), vars.dtf_dm(), vars.pt(gcm().D0),
                             vars.dtf_chi2(gcm().head)])

    OL = RS[rs_sel].merge(WS, on=['eventNumber'],
                          left_index=True, suffixes=['_RS', '_WS'])
    # OLS = OL.query('abs(delta_m_dtf_RS-145.)<3.')
    OLS = OL.query('abs(D0_PT_RS-D0_PT_WS)<1.')

    return pd.Series(~WS.index.isin(OLS.index), index=WS.index)


@buffer.buffer_load
def randomly_remove_candidates():
    """After applying the full selection, creates selection mask to reject
    multiple candidates randomly. Multiple candidates are defined as those
    having the same eventNumber and same D0 transverse momentum"""

    df = gcm().get_data([vars.evt_num(), vars.pt(gcm().D0)])
    fsel = extended_selection.get_complete_selection(True)
    passed = remove_right_sign_candidates()
    selected = df[fsel & passed]
    # select candidates randomly so shuffle
    selected = selected.reindex(np.random.permutation(selected.index))
    return ~selected.duplicated(['eventNumber', 'D0_PT'])


def overlap_plotting():
    df = gcm().get_data([vars.dtf_dm()])
    sel = extended_selection.get_complete_selection(True)
    passed = remove_right_sign_candidates()

    outfile = gcm().get_output_path('selection') + 'RS_candidates.pdf'
    with PdfPages(outfile) as pdf:
        nbins = 50
        xmin = min(df[sel][vars.dtf_dm()])
        xmax = max(df[sel][vars.dtf_dm()])

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.hist(df[sel & passed][vars.dtf_dm()], bins=nbins, range=(xmin, xmax))
        ax.set_xlabel(vars.dtf_dm.latex(with_unit=True))
        ax.yaxis.set_visible(False)
        pdf.savefig(fig)
        plt.clf()

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.hist(df[sel & ~passed][vars.dtf_dm()], bins=nbins, range=(xmin, xmax))
        ax.set_xlabel(vars.dtf_dm.latex(with_unit=True))
        ax.yaxis.set_visible(False)
        pdf.savefig(fig)
        plt.clf()

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.hist(df[sel & passed][vars.dtf_dm()], bins=nbins,
                range=(xmin, xmax), label='Kept')
        ax.hist(df[sel & ~passed][vars.dtf_dm()], bins=nbins,
                range=(xmin, xmax), label='Removed')
        ax.set_xlabel(vars.dtf_dm.latex(with_unit=True))
        ax.legend()
        ax.yaxis.set_visible(False)
        pdf.savefig(fig)
        plt.clf()


def multi_cand_plotting():
    df = gcm().get_data([vars.evt_num(), vars.pt(gcm().D0)])
    sel = extended_selection.get_complete_selection(True)
    passed = remove_right_sign_candidates()

    outfile = gcm().get_output_path('selection') + 'mult_candidates.pdf'
    with PdfPages(outfile) as pdf:
        candidates = df.groupby(['eventNumber']).size()
        fig, ax = plt.subplots(figsize=(10, 10))
        sns.countplot(candidates, palette='plasma')
        ax.set_xlabel('Number of candidates')
        ax.set_ylabel('Number of events')
        ax.set_yscale("log", nonposy='clip')
        pdf.savefig(fig)
        plt.clf()

        candidates = df[sel].groupby(['eventNumber']).size()
        fig, ax = plt.subplots(figsize=(10, 10))
        sns.countplot(candidates, palette='plasma')
        ax.set_xlabel('Number of candidates')
        ax.set_ylabel('Number of events')
        ax.set_yscale("log", nonposy='clip')
        pdf.savefig(fig)
        plt.clf()

        candidates = df.groupby(['eventNumber', 'D0_PT']).size()
        fig, ax = plt.subplots(figsize=(10, 10))
        sns.countplot(candidates, palette='plasma')
        ax.set_xlabel('Number of candidates')
        ax.set_ylabel('Number of events')
        ax.set_yscale("log", nonposy='clip')
        pdf.savefig(fig)
        plt.clf()

        candidates = df[sel].groupby(['eventNumber', 'D0_PT']).size()
        fig, ax = plt.subplots(figsize=(10, 10))
        sns.countplot(candidates, palette='plasma')
        ax.set_xlabel('Number of candidates')
        ax.set_ylabel('Number of events')
        ax.set_yscale("log", nonposy='clip')
        pdf.savefig(fig)
        plt.clf()

        candidates = df[sel & passed].groupby(['eventNumber']).size()
        fig, ax = plt.subplots(figsize=(10, 10))
        sns.countplot(candidates, palette='plasma')
        ax.set_xlabel('Number of candidates')
        ax.set_ylabel('Number of events')
        ax.set_yscale("log", nonposy='clip')
        pdf.savefig(fig)
        plt.clf()

        candidates = df[sel & passed].groupby(['eventNumber', 'D0_PT']).size()
        fig, ax = plt.subplots(figsize=(10, 10))
        sns.countplot(candidates, palette='plasma')
        ax.set_xlabel('Number of candidates')
        ax.set_ylabel('Number of events')
        ax.set_yscale("log", nonposy='clip')
        pdf.savefig(fig)
        plt.clf()


if __name__ == '__main__':
    args = parser.create_parser()
    with MODE(args.polarity, args.year, args.mode):
        remove_right_sign_candidates(use_buffered=False)
        multi_cand_plotting()
        overlap_plotting()
