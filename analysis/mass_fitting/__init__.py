from matplotlib.backends.backend_pdf import PdfPages
from .fit_setup import setup_pdf
import matplotlib.pyplot as plt
from . import fit_config
import ROOT
import ROOT.RooFit as RF
from . import shapes
from. import roofit_to_matplotlib

from k3pi_utilities.variables import dtf_dm, m
from .. import selection


def fit(mode):
    # Get the data
    sel = selection.pid_selection(mode)
    sel &= selection.pid_fiducial_selection(mode)
    sel &= selection.mass_fiducial_selection(mode)
    sel &= selection.remove_secondary(mode)
    sel &= selection.slow_pion(mode)

    df = mode.get_data([dtf_dm(), m(mode.D0)])
    df = df[sel]

    fit_config.WS_DMASS_NAME = dtf_dm()
    fit_config.WS_MASS_NAME = m(mode.D0)
    wsp = ROOT.RooWorkspace(mode.mode, mode.mode)

    wsp.factory('{}[{},{}]'.format(m(mode.D0), df[m(mode.D0)].min(), df[m(mode.D0)].max()))
    wsp.factory('{}[139.57,160]'.format(dtf_dm()))

    wsp.defineSet('datavars', '{},{}'.format(dtf_dm(), m(mode.D0)))

    setup_pdf(wsp, mode)

    data = fit_config.pandas_to_roodataset(df, wsp.set('datavars'))
    model = wsp.pdf('total')

    model.fitTo(data, RF.NumCPU(4), RF.Save(True), RF.Strategy(2), RF.Extended(True))

    fit_config.dump_workspace(mode, wsp)


def plot_fit(mode):
    shapes.load_shape_class('RooCruijff')
    wsp = fit_config.load_workspace(mode)
    sel = selection.pid_selection(mode)
    sel &= selection.pid_fiducial_selection(mode)
    sel &= selection.mass_fiducial_selection(mode)
    sel &= selection.remove_secondary(mode)
    sel &= selection.slow_pion(mode)

    df = mode.get_data([dtf_dm(), m(mode.D0)])
    df = df[sel]
    data = fit_config.pandas_to_roodataset(df, wsp.set('datavars'))
    fit_config.WS_DMASS_NAME = dtf_dm()
    fit_config.WS_MASS_NAME = m(mode.D0)

    outfile = mode.get_output_path('sweight_fit') + 'fits.pdf'
    with PdfPages(outfile) as pdf:
        for func in [m, dtf_dm]:
            roofit_to_matplotlib.plot_fit(mode.D0, wsp, func, data=data, pdf=pdf)

