from __future__ import print_function
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd

from k3pi_config.modes import gcm
from k3pi_config import config
from k3pi_utilities import tex_compile
from k3pi_utilities.variables import dtf_dm, m
from k3pi_utilities.buffer import buffer_load
from k3pi_utilities.debugging import call_debug
from k3pi_utilities import helpers, get_logger

from analysis import final_selection as selection
from analysis.mass_fitting.metrics import get_metric, _metric_base
from analysis.mass_fitting import shapes
log = get_logger('mass_fitting')


def run_spearmint_fit(spearmint_selection=None, metric='punzi'):
    """Runs the mass fit. Either nominal with making pretty plots or
    in spearmint mode which does not save the workspace and returns a
    metric."""
    from . import fit_config
    from ROOT import RooFit as RF
    shapes.load_shape_class('RooCruijff')
    shapes.load_shape_class('RooJohnsonSU')
    shapes.load_shape_class('RooBackground')
    mode = gcm()
    wsp = fit_config.load_workspace(mode)
    sel = selection.get_final_selection()

    # Get the data
    df = mode.get_data([dtf_dm(), m(mode.D0)])
    if spearmint_selection is not None:
        sel = sel & spearmint_selection
    df = df[sel]

    data = fit_config.pandas_to_roodataset(df, wsp.set('datavars'))
    model = wsp.pdf('total')

    metric = get_metric(metric)(wsp)

    if spearmint_selection is not None:
        result = model.fitTo(data, RF.NumCPU(4), RF.Save(True), RF.Strategy(2),
                             RF.Extended(True))

        if not helpers.check_fit_result(result, log):
            result = model.fitTo(data, RF.NumCPU(4), RF.Save(True),
                                 RF.Strategy(1), RF.Extended(True))

        if not helpers.check_fit_result(result, log):
            result = model.fitTo(data, RF.NumCPU(4), RF.Save(True),
                                 RF.Strategy(0), RF.Extended(True))

        if not helpers.check_fit_result(result, log):
            log.warn('Bad fit quality')
            return 0.0

    return metric()


def fit():
    """Runs the mass fit. Either nominal with making pretty plots or
    in spearmint mode which does not save the workspace and returns a
    metric."""
    # Get the data
    # TODO: rewrite selection to use gcm itself
    mode = gcm()
    sel = selection.get_final_selection()

    df = mode.get_data([dtf_dm(), m(mode.D0)])
    df = df[sel]

    from . import fit_config
    from ROOT import RooFit as RF
    from .fit_setup import setup_workspace

    wsp, _ = setup_workspace()
    data = fit_config.pandas_to_roodataset(df, wsp.set('datavars'))
    model = wsp.pdf('total')

    plot_fit('_start_values', wsp=wsp)
    result = model.fitTo(data, RF.NumCPU(4), RF.Save(True), RF.Strategy(2),
                         RF.Extended(True))

    if not helpers.check_fit_result(result, log):
        log.error('Bad fit quality')
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
    sel = selection.get_final_selection()

    df = mode.get_data([dtf_dm(), m(mode.D0)])
    df = df[sel]
    data = fit_config.pandas_to_roodataset(df, wsp.set('datavars'))
    fit_config.WS_DMASS_NAME = dtf_dm()
    fit_config.WS_MASS_NAME = m(mode.D0)

    outfile = mode.get_output_path('sweight_fit') + 'fits{}.pdf'.format(
        suffix if suffix is not None else '')
    with PdfPages(outfile) as pdf:
        for func in [m, dtf_dm]:
            roofit_to_matplotlib.plot_fit(
                mode.D0, wsp, func, data=data, pdf=pdf,
                do_comb_bkg=mode.mode in config.twotag_modes)
            roofit_to_matplotlib.plot_fit(
                mode.D0, wsp, func, data=data, pdf=pdf, do_pulls=False,
                do_comb_bkg=mode.mode in config.twotag_modes)


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
    row_template_const = r'{} & \multicolumn{{3}}{{c}}{{{}}} \\'

    fn = mode.get_output_path('sweight_fit') + 'parameters.tex'
    with open(fn, 'w') as f:
        print(r'\begin{tabular}{lr@{\hskip 0.1em}c@{\hskip 0.1em}l}', file=f)

        wsp = fit_config.load_workspace(mode)
        for pdf in vs:
            for vn, pn in pdf:
                var = wsp.var(vn)
                if var:
                    val, err = var.getVal(), var.getError()
                    if not var.isConstant():
                        rounding = [err]
                        val, prec = helpers.rounder(val, rounding, sig_prec=1)
                        err, _ = helpers.rounder(err, rounding,
                                                is_unc=True, sig_prec=1)
                        spec = '{{:.{}f}}'.format(prec)
                        print(
                            row_template.format(pn, spec.format(val),
                                                spec.format(err)), file=f)
                    else:
                        print(row_template_const.format(pn, val), file=f)
            print(r'\hline', file=f)
        print(r'\end{tabular}', file=f)
    tex_compile.convert_tex_to_pdf(fn)


@np.vectorize
def call_after_set(pdf, wsp, **kwargs):
    for var, val in kwargs.items():
        fnd = wsp.var(var)
        if fnd:
            fnd.setVal(val)
    return pdf.getVal(wsp.set('datavars'))


@buffer_load
@call_debug
def get_sweights(do_comb_bkg=False):
    helpers.allow_root()
    df = gcm().get_data([m(gcm().D0), dtf_dm()])
    from . import fit_config
    from hep_ml import splot
    shapes.load_shape_class('RooCruijff')
    shapes.load_shape_class('RooJohnsonSU')
    shapes.load_shape_class('RooBackground')
    wsp = fit_config.load_workspace(gcm())

    sel = selection.get_final_selection()
    do_comb_bkg = gcm().mode in config.twotag_modes

    df = df[sel]

    sig_pdf = wsp.pdf('signal')
    rnd_pdf = wsp.pdf('random')
    comb_pdf = wsp.pdf('combinatorial')

    sig_prob = call_after_set(sig_pdf, wsp, **df)
    rnd_prob = call_after_set(rnd_pdf, wsp, **df)
    if do_comb_bkg:
        comb_prob = call_after_set(comb_pdf, wsp, **df)

    if do_comb_bkg:
        probs = pd.DataFrame(dict(sig=sig_prob*wsp.var('NSig').getVal(),
                                  rnd=rnd_prob*wsp.var('NSPi').getVal(),
                                  comb=comb_prob*wsp.var('NBkg').getVal()),
                             index=df.index)
    else:
        probs = pd.DataFrame(dict(sig=sig_prob*wsp.var('NSig').getVal(),
                                  rnd=rnd_prob*wsp.var('NSPi').getVal()),
                             index=df.index)
    probs = probs.div(probs.sum(axis=1), axis=0)

    sweights = splot.compute_sweights(probs)
    sweights.index = probs.index
    if not do_comb_bkg:
        sweights['comb'] = 0.0

    return sweights


def run_spearmint_sweights(spearmint_selection=None):
    """Runs the mass fit. Either nominal with making pretty plots or
    in spearmint mode which does not save the workspace and returns a
    metric."""
    sel = selection.get_final_selection()

    sweights = get_sweights(gcm())

    sweights['bkg'] = sweights.rnd + sweights.comb

    df = sweights[sel.reindex(sweights.index)]
    sig0 = np.sum(df.sig)

    if spearmint_selection is not None:
        sel = sel & spearmint_selection
    df = sweights[sel.reindex(sweights.index)]
    sig = np.sum(df.sig)
    bkg = np.sum(df.bkg)
    log.info('sig={}, bkg={}, sig0={}'.format(sig, bkg, sig0))
    if bkg < 0:
        bkg = 0

    return -(sig/sig0)/(0.5 + np.sqrt(bkg))


def get_yields(comb_bkg=False):
    helpers.allow_root()
    from . import fit_config
    import ROOT
    from ROOT import RooFit as RF
    shapes.load_shape_class('RooCruijff')
    shapes.load_shape_class('RooJohnsonSU')
    shapes.load_shape_class('RooBackground')

    wsp = fit_config.load_workspace(gcm())

    calculator = _metric_base(wsp, comb_bkg)
    sig = calculator._get_number_of_signal()
    bkg = calculator._get_number_of_background()
    return sig, bkg
