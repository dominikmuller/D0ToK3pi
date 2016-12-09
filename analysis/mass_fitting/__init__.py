from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
from k3pi_config import config
import collections
from . import shapes
from k3pi_utilities.buffer import buffer_load
from k3pi_utilities.debugging import call_debug

from k3pi_utilities.variables import dtf_dm, m
from .. import selection


def fit(mode):
    from . import fit_config
    import ROOT
    import ROOT.RooFit as RF
    from .fit_setup import setup_pdf
    # Get the data
    sel = selection.pid_selection(mode)
    sel &= selection.pid_fiducial_selection(mode)
    sel &= selection.mass_fiducial_selection(mode)
    if mode.mode not in config.twotag_modes:
        sel &= selection.remove_secondary(mode)
    sel &= selection.slow_pion(mode)

    df = mode.get_data([dtf_dm(), m(mode.D0)])
    df = df[sel]

    fit_config.WS_DMASS_NAME = dtf_dm()
    fit_config.WS_MASS_NAME = m(mode.D0)
    wsp = ROOT.RooWorkspace(mode.mode, mode.mode)

    wsp.factory('{}[{},{}]'.format(m(mode.D0), df[m(mode.D0)].min(),
                                   df[m(mode.D0)].max()))
    wsp.factory('{}[{},{}]'.format(dtf_dm(), df[dtf_dm()].min(),
                                   df[dtf_dm()].max()))

    wsp.defineSet('datavars', '{},{}'.format(dtf_dm(), m(mode.D0)))

    setup_pdf(wsp, mode)

    data = fit_config.pandas_to_roodataset(df, wsp.set('datavars'))
    model = wsp.pdf('total')

    plot_fit(mode, 'starting', wsp=wsp)
    model.fitTo(data, RF.NumCPU(4), RF.Save(True), RF.Strategy(2),
                RF.Extended(True))

    fit_config.dump_workspace(mode, wsp)


def plot_fit(mode, suffix=None, wsp=None):
    from . import roofit_to_matplotlib
    from . import fit_config
    shapes.load_shape_class('RooCruijff')
    shapes.load_shape_class('RooJohnsonSU')
    shapes.load_shape_class('RooBackground')
    if wsp is None:
        wsp = fit_config.load_workspace(mode)
    sel = selection.pid_selection(mode)
    sel &= selection.pid_fiducial_selection(mode)
    sel &= selection.mass_fiducial_selection(mode)
    if mode.mode not in config.twotag_modes:
        sel &= selection.remove_secondary(mode)
    sel &= selection.slow_pion(mode)

    df = mode.get_data([dtf_dm(), m(mode.D0)])
    df = df[sel]
    data = fit_config.pandas_to_roodataset(df, wsp.set('datavars'))
    fit_config.WS_DMASS_NAME = dtf_dm()
    fit_config.WS_MASS_NAME = m(mode.D0)

    outfile = mode.get_output_path('sweight_fit') + 'fits{}.pdf'.format(
        suffix if suffix is not None else '')
    with PdfPages(outfile) as pdf:
        for func in [m, dtf_dm]:
            roofit_to_matplotlib.plot_fit(mode.D0, wsp, func,
                                          data=data, pdf=pdf)


@np.vectorize
def call_after_set(pdf, wsp, **kwargs):
    for var, val in kwargs.iteritems():
        fnd = wsp.var(var)
        if fnd:
            fnd.setVal(val)
    return pdf.getVal()


@buffer_load
@call_debug
def get_sweights(mode):
    # I really don't want stupid ROOT here so if we do the dummy call to get
    # the variables needed, just skip.
    df = mode.get_data([m(mode.D0), dtf_dm()])
    from . import fit_config
    from hep_ml import splot
    shapes.load_shape_class('RooCruijff')
    shapes.load_shape_class('RooJohnsonSU')
    shapes.load_shape_class('RooBackground')
    wsp = fit_config.load_workspace(mode)

    sel = selection.full_selection(mode)

    df = df[sel]

    sig_pdf = wsp.pdf('signal')
    rnd_pdf = wsp.pdf('random')
    comb_pdf = wsp.pdf('combinatorial')

    sig_prob = call_after_set(sig_pdf, wsp, **df)
    rnd_prob = call_after_set(rnd_pdf, wsp, **df)
    comb_prob = call_after_set(comb_pdf, wsp, **df)

    probs = pd.DataFrame(dict(sig=sig_prob,
                              rnd=rnd_prob,
                              comb=comb_prob))
    probs = probs.div(probs.sum(axis=1), axis=0)

    return splot.compute_sweights(probs)
