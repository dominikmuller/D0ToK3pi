from k3pi_config.modes import MODE, gcm
from k3pi_utilities import parser, logger
from matplotlib.backends.backend_pdf import PdfPages
from analysis import extended_selection, selection, misid_selection
from itertools import combinations
from k3pi_utilities import variables as vars
from k3pi_utilities import buffer
import matplotlib.pyplot as plt
from k3pi_cpp import compute_delta_angle
import seaborn.apionly as sns
from k3pi_utilities.helpers import add_separation_page
import numpy as np
import pandas as pd

from k3pi_config import config

log = logger.get_logger('candidate_sorting')


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
        RS = gcm().get_data(
            [vars.evt_num(), vars.run_num(), vars.dtf_dm(), vars.pt(gcm().D0)])
        rs_sel = extended_selection.get_complete_selection(True)
    # RS modes should not be selected using this:
    if gcm().mode not in config.wrong_sign_modes:
        return pd.Series(True, RS.index)

    with MODE(polarity, year, ws):
        WS = gcm().get_data([vars.evt_num(), vars.dtf_dm(), vars.pt(gcm().D0),
                             vars.dtf_chi2(gcm().head)])

    OL = RS[rs_sel].merge(WS, on=['eventNumber'],
                          left_index=True, suffixes=['_RS', '_WS'])
    dm_ref = config.PDG_MASSES['delta']
    OLS = OL.query('(abs(delta_m_dtf_RS-{})<1.) &'
                   '(abs(D0_PT_RS-D0_PT_WS)<1.)'.format(dm_ref))

    return pd.Series(~WS.index.isin(OLS.index), index=WS.index)


@buffer.buffer_load
def remove_clones():
    """Remove events with cloned tracks. Different treatment for RS and WS
    due to naming convention."""
    # Get the necessary information from the current mode
    ret = None
    sel = extended_selection.get_complete_selection(True)
    passed = remove_right_sign_candidates()
    masses = config.PDG_MASSES

    outfile = gcm().get_output_path('selection') + 'clones.pdf'
    pdf = PdfPages(outfile)
    for A, B in combinations(gcm().head.all_daughters(), 2):
        log.info('Checking angle between {} and {}'.format(A.name, B.name))
        df = gcm().get_data(
            [vars.phi(A), vars.pt(A), vars.eta(A),
             vars.phi(B), vars.pt(B), vars.eta(B)])
        angle = compute_delta_angle(
            df[vars.pt(A)], df[vars.eta(A)], df[vars.phi(A)], masses[A.pid],
            df[vars.pt(B)], df[vars.eta(B)], df[vars.phi(B)], masses[B.pid])
        angle = pd.Series(angle, index=df.index)

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.hist(angle[sel & passed], bins=50, range=(0, 0.01), color='#006EB6', edgecolor='#006EB6')
        ax.set_xlabel(r'$\angle({},{})$ [rad]'.format(
            A.title.replace('$', ''), B.title.replace('$', '')))
        ax.set_ylabel('Candidates')
        ax.set_xlim((0, 0.01))
        pdf.savefig(fig)
        plt.clf()

        if ret is None:
            ret = (angle > 0.0005)
        else:
            ret &= (angle > 0.0005)

    df = gcm().get_data([vars.dtf_dm()])
    xmin = min(df[sel & passed & ~ret][vars.dtf_dm()])
    xmax = max(df[sel & passed & ~ret][vars.dtf_dm()])

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.hist(df[sel & passed & ret][vars.dtf_dm()],
            bins=50, range=(xmin, xmax), label='Kept')
    ax.hist(df[sel & passed & ~ret][vars.dtf_dm()],
            bins=50, range=(xmin, xmax), label='Removed')
    ax.set_xlabel(vars.dtf_dm.latex(with_unit=True))
    ax.yaxis.set_visible(False)
    ax.legend()
    pdf.savefig(fig)
    plt.clf()

    pdf.close()

    return ret


def overlap_plotting():
    df = gcm().get_data([vars.dtf_dm()])
    sel = extended_selection.get_complete_selection(True)
    sel &= misid_selection.misid_cut()
    passed = remove_right_sign_candidates()

    outfile = gcm().get_output_path('selection') + 'RS_candidates.pdf'
    with PdfPages(outfile) as pdf:
        nbins = 50
        xmin = min(df[sel][vars.dtf_dm()])
        xmax = max(df[sel][vars.dtf_dm()])

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.hist(df[sel & passed][vars.dtf_dm()],
                bins=nbins, range=(xmin, xmax), color='#006EB6', edgecolor='#006EB6', label='Ghost')
        ax.set_xlabel(vars.dtf_dm.latex(with_unit=True))
        ax.set_xlim((xmin, xmax))
        ax.set_ylabel('Arbitrary units')
        pdf.savefig(fig)
        plt.clf()

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.hist(df[sel & ~passed][vars.dtf_dm()],
                bins=nbins, range=(xmin, xmax), color='#006EB6', edgecolor='#006EB6', label='Ghost')
        ax.set_xlim((xmin, xmax))
        ax.set_xlabel(vars.dtf_dm.latex(with_unit=True))
        ax.set_ylabel('Arbitrary units')
        pdf.savefig(fig)
        plt.clf()

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.hist(df[sel & passed][vars.dtf_dm()], bins=nbins, color='#D3EFFB',
                range=(xmin, xmax), label='Kept', edgecolor='#D3EFFB')
        ax.hist(df[sel & ~passed][vars.dtf_dm()], bins=nbins,
                range=(xmin, xmax), label='Removed', color='#006EB6', edgecolor='#006EB6')
        ax.set_xlim((xmin, xmax))
        ax.set_xlabel(vars.dtf_dm.latex(with_unit=True))
        ax.set_ylabel('Candidates')
        ax.legend()
        pdf.savefig(fig)
        plt.clf()


def multi_cand_plotting():
    df = gcm().get_data([vars.run_num(), vars.evt_num(), vars.pt(gcm().D0)])
    sel = extended_selection.get_complete_selection(True)
    sel &= selection.delta_mass_wide_signal_region()
    passed = remove_right_sign_candidates()
    passed &= remove_clones()

    outfile = gcm().get_output_path('selection') + 'mult_candidates.pdf'
    with PdfPages(outfile) as pdf:
        add_separation_page(
            pdf, 'Matched on eventNumber and runNumber')
        candidates = df.groupby(
            ['eventNumber', 'runNumber']).size()
        fig, ax = plt.subplots(figsize=(10, 10))
        sns.countplot(candidates, palette='plasma')
        ax.set_xlabel('Number of candidates')
        ax.set_ylabel('Number of events')
        ax.set_yscale("log", nonposy='clip')
        pdf.savefig(fig)
        plt.clf()

        add_separation_page(
            pdf, 'matched on eventnumber and runNumber. '
                 'full selection + signal window')
        candidates = df[sel].groupby(
            ['eventNumber', 'runNumber']).size()
        fig, ax = plt.subplots(figsize=(10, 10))
        sns.countplot(candidates, palette='plasma')
        ax.set_xlabel('Number of candidates')
        ax.set_ylabel('Number of events')
        ax.set_yscale("log", nonposy='clip')
        pdf.savefig(fig)
        plt.clf()

        add_separation_page(
            pdf, 'Matched on eventNumber, runNumber and D0 PT')
        candidates = df.groupby(
            ['eventNumber', 'runNumber', 'D0_PT']).size()
        fig, ax = plt.subplots(figsize=(10, 10))
        sns.countplot(candidates, palette='plasma')
        ax.set_xlabel('Number of candidates')
        ax.set_ylabel('Number of events')
        ax.set_yscale("log", nonposy='clip')
        pdf.savefig(fig)
        plt.clf()

        add_separation_page(
            pdf, 'Matched on eventNumber, runNumber and D0 PT'
                 'full selection + signal window')
        candidates = df[sel].groupby(
            ['eventNumber', 'runNumber', 'D0_PT']).size()
        fig, ax = plt.subplots(figsize=(10, 10))
        sns.countplot(candidates, palette='plasma')
        ax.set_xlabel('Number of candidates')
        ax.set_ylabel('Number of events')
        ax.set_yscale("log", nonposy='clip')
        pdf.savefig(fig)
        plt.clf()

        add_separation_page(
            pdf, 'Matched on eventNumber and runNumber'
                 'full selection + signal window + clones + RS matching')
        candidates = df[sel & passed].groupby(
            ['eventNumber', 'runNumber']).size()
        fig, ax = plt.subplots(figsize=(10, 10))
        sns.countplot(candidates, palette='plasma')
        ax.set_xlabel('Number of candidates')
        ax.set_ylabel('Number of events')
        ax.set_yscale("log", nonposy='clip')
        pdf.savefig(fig)
        plt.clf()

        add_separation_page(
            pdf, 'Matched on eventNumber, runNumber and D0 PT'
                 'full selection + signal window + clones + RS matching')
        candidates = df[sel & passed].groupby(
            ['eventNumber', 'runNumber', 'D0_PT']).size()
        fig, ax = plt.subplots(figsize=(10, 10))
        sns.countplot(candidates, palette='plasma')
        ax.set_xlabel('Number of candidates')
        ax.set_ylabel('Number of events')
        ax.set_yscale("log", nonposy='clip')
        pdf.savefig(fig)
        plt.clf()


@buffer.buffer_load
def randomly_remove_candidates():
    """After applying the full selection, creates selection mask to reject
    multiple candidates randomly. Multiple candidates are defined as those
    having the same eventNumber and same D0 transverse momentum"""

    df = gcm().get_data([vars.evt_num(), vars.pt(gcm().D0)])
    fsel = extended_selection.get_complete_selection(True)
    passed = remove_right_sign_candidates()
    passed &= remove_clones()
    selected = df[fsel & passed]
    # select candidates randomly so shuffle
    selected = selected.reindex(np.random.permutation(selected.index))
    return ~selected.duplicated(['eventNumber', 'D0_PT'])


if __name__ == '__main__':
    args = parser.create_parser()
    with MODE(args.polarity, args.year, args.mode):
        remove_right_sign_candidates(use_buffered=False)
        randomly_remove_candidates(use_buffered=False)
        remove_clones(use_buffered=False)
        multi_cand_plotting()
        overlap_plotting()
