import ROOT
import ROOT.RooFit as RF  # NOQA
from . import shapes
from k3pi_config import modes, config
from k3pi_utilities.variables import dtf_dm, m
from . import fit_config


def setup_workspace():

    mode = modes.gcm()

    wsp = ROOT.RooWorkspace(mode.mode, mode.mode)
    fit_config.WS_DMASS_NAME = dtf_dm()
    fit_config.WS_MASS_NAME = m(mode.D0)

    wsp.factory('{}[{},{}]'.format(m(mode.D0), 1810., 1920.))
    wsp.factory('{}[{},{}]'.format(dtf_dm(), 140.5, 160.5))
    wsp.var(dtf_dm()).setRange('plotting', 140.5, 152.5)
    wsp.var(m(mode.D0)).setRange('plotting', 1820, 1910)

    wsp.defineSet('datavars', '{},{}'.format(dtf_dm(), m(mode.D0)))

    vs = setup_pdf(wsp)

    return wsp, vs


def setup_pdf(wsp):
    # Only call this function once on a workspace
    if wsp.var('set_up_done'):
        return
    mode = modes.gcm()
    # ROOT.RooMsgService.instance().setGlobalKillBelow(RF.WARNING)
    # ROOT.RooMsgService.instance().setSilentMode(True)
    SIG_M, SIG_DM, BKG_DM = mode.shapes

    variables = []

    SIG_M = shapes.d0_shapes[SIG_M]
    SIG_DM = shapes.dst_d0_shapes[SIG_DM]
    BKG_DM = shapes.dst_d0_shapes[BKG_DM]

    # Variables for the signal pdf
    sig_m, vs = SIG_M('', wsp, mode)
    variables += [vs]
    if mode.mode in config.twotag_modes:
        bkg_m, vs = shapes.d0_bkg('', wsp, mode)
        variables += [vs]

    # delta random slow
    slow_pi_dm, vs = BKG_DM('sp', wsp)
    variables += [vs]
    if mode.mode in config.twotag_modes:
        bkg_dm, vs = BKG_DM('bkg', wsp)
        variables += [vs]
    sig_dm, vs = SIG_DM('', wsp, mode)
    variables += [vs]
    # Signal 2D pdf
    wsp.factory("PROD::signal({}, {})".format(sig_m, sig_dm))
    wsp.factory("PROD::random({}, {})".format(sig_m, slow_pi_dm))
    if mode.mode in config.twotag_modes:
        wsp.factory("PROD::combinatorial({}, {})".format(bkg_m, bkg_dm))

    wsp.factory(mode.get_rf_vars('NSig'))
    wsp.factory(mode.get_rf_vars('NSPi'))
    if mode.mode in config.twotag_modes:
        wsp.factory(mode.get_rf_vars('NBkg'))

    # wsp.var('NBkg').setConstant()
    # wsp.var('a_dm_bkg').setConstant()

    variables += [[
        ('NSig', r'$N_{\text{Sig}}$'),
        ('NSPi', r'$N_{\text{Rnd}}$'),
        ('NBkg', r'$N_{\text{Cmb}}$'),
    ]]

    # Final model
    if mode.mode in config.twotag_modes:
        wsp.factory("SUM::total(NSig*signal,NSPi*random,NBkg*combinatorial)")
    else:
        wsp.factory("SUM::total(NSig*signal,NSPi*random)")

    wsp.factory('set_up_done[1]')

    return variables
