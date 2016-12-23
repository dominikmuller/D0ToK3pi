from __future__ import print_function
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
from k3pi_config import config
from . import shapes
from k3pi_utilities.buffer import buffer_load
from k3pi_utilities.debugging import call_debug
from k3pi_utilities import helpers
from k3pi_config.modes import gcm

from k3pi_utilities import tex_compile
from k3pi_utilities.variables import dtf_dm, m
from .. import selection


def fit():
    from . import fit_config
    from ROOT import RooFit as RF
    from .fit_setup import setup_workspace
    # Get the data
    # TODO: rewrite selection to use gcm itself
    mode = gcm()
    sel = selection.pid_selection(mode)
    sel &= selection.pid_fiducial_selection(mode)
    sel &= selection.mass_fiducial_selection(mode)
    if mode.mode not in config.twotag_modes:
        sel &= selection.remove_secondary(mode)
    sel &= selection.slow_pion(mode)

    df = mode.get_data([dtf_dm(), m(mode.D0)])
    df = df[sel]

    wsp, _ = setup_workspace()

    data = fit_config.pandas_to_roodataset(df, wsp.set('datavars'))
    model = wsp.pdf('total')

    plot_fit('_start_values', wsp=wsp)
    model.fitTo(data, RF.NumCPU(4), RF.Save(True), RF.Strategy(2),
                RF.Extended(True))

    fit_config.dump_workspace(mode, wsp)


def plot_fit(suffix=None, wsp=None):
    from . import roofit_to_matplotlib
    from . import fit_config
    shapes.load_shape_class('RooCruijff')
    shapes.load_shape_class('RooJohnsonSU')
    shapes.load_shape_class('RooBackground')
    mode = gcm()
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


def fit_parameters():
    from . import fit_config
    shapes.load_shape_class('RooCruijff')
    shapes.load_shape_class('RooJohnsonSU')
    shapes.load_shape_class('RooBackground')
    helpers.ensure_directory_exists
    from .fit_setup import setup_workspace
    mode = gcm()
    _, vs = setup_workspace()
    row_template = r'{} & {} & \pm & {} \\'

    fn = mode.get_output_path('sweight_fit') + 'parameters.tex'
    with open(fn, 'w') as f:
        print(r'\begin{tabular}{l|r@{\hskip 0.1em}c@{\hskip 0.1em}l}', file=f)

        wsp = fit_config.load_workspace(mode)
        for pdf in vs:
            for vn, pn in pdf:
                var = wsp.var(vn)
                if var:
                    val, err = var.getVal(), var.getError()
                    rounding = [err]
                    val, prec = helpers.rounder(val, rounding, sig_prec=1)
                    err, _ = helpers.rounder(err, rounding,
                                             is_unc=True, sig_prec=1)
                    spec = '{{:.{}f}}'.format(prec)
                    print(
                        row_template.format(pn, spec.format(val),
                                            spec.format(err)),
                        file=f)
            print(r'\hline', file=f)
        print(r'\end{tabular}', file=f)
    tex_compile.convert_tex_to_pdf(fn)


@np.vectorize
def call_after_set(pdf, wsp, **kwargs):
    for var, val in kwargs.iteritems():
        fnd = wsp.var(var)
        if fnd:
            fnd.setVal(val)
    return pdf.getVal(wsp.set('datavars'))


@buffer_load
@call_debug
def get_sweights():
    df = gcm().get_data([m(gcm().D0), dtf_dm()])
    from . import fit_config
    from hep_ml import splot
    shapes.load_shape_class('RooCruijff')
    shapes.load_shape_class('RooJohnsonSU')
    shapes.load_shape_class('RooBackground')
    wsp = fit_config.load_workspace(gcm())

    sel = selection.full_selection()

    df = df[sel]

    sig_pdf = wsp.pdf('signal')
    rnd_pdf = wsp.pdf('random')
    comb_pdf = wsp.pdf('combinatorial')

    sig_prob = call_after_set(sig_pdf, wsp, **df)
    rnd_prob = call_after_set(rnd_pdf, wsp, **df)
    comb_prob = call_after_set(comb_pdf, wsp, **df)

    probs = pd.DataFrame(dict(sig=sig_prob*wsp.var('NSig').getVal(),
                              rnd=rnd_prob*wsp.var('NSPi').getVal(),
                              comb=comb_prob*wsp.var('NBkg').getVal()),
                         index=df.index)
    probs = probs.div(probs.sum(axis=1), axis=0)

    return splot.compute_sweights(probs)
