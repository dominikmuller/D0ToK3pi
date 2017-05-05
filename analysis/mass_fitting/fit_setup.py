import ROOT
import ROOT.RooFit as RF
from . import shapes
from k3pi_config import modes, config
from k3pi_utilities.variables import dtf_dm, m
from . import fit_config


def setup_workspace():

    mode = modes.gcm()

    wsp = ROOT.RooWorkspace(mode.mode, mode.mode)
    fit_config.WS_DMASS_NAME = dtf_dm()
    fit_config.WS_MASS_NAME = m(mode.D0)

    d = config.PDG_MASSES[config.Dz] + 5.
    wsp.factory('{}[{},{}]'.format(m(mode.D0), 1810., 1920. ))
    wsp.factory('{}[{},{}]'.format(dtf_dm(), 140.5, 160.5 ))

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
    # bkg_m, vs = shapes.d0_bkg('', wsp, mode)
    # variables += [vs]

    # delta random slow
    slow_pi_dm, vs = BKG_DM('sp', wsp)
    variables += [vs]
    # bkg_dm, vs = BKG_DM('bkg', wsp)
    # variables += [vs]
    sig_dm, vs = SIG_DM('', wsp, mode)
    variables += [vs]
    # Signal 2D pdf
    wsp.factory("PROD::signal({}, {})".format(sig_m, sig_dm))
    wsp.factory("PROD::random({}, {})".format(sig_m, slow_pi_dm))
    # wsp.factory("PROD::combinatorial({}, {})".format(bkg_m, bkg_dm))

    wsp.factory(mode.get_rf_vars('NSig'))
    wsp.factory(mode.get_rf_vars('NSPi'))
    # wsp.factory(mode.get_rf_vars('NBkg'))

    # wsp.var('NBkg').setConstant()
    # wsp.var('a_dm_bkg').setConstant()

    variables += [[
        ('NSig', r'$N_{\text{Sig}}$'),
        ('NSPi', r'$N_{\text{Rnd}}$'),
        ('NBkg', r'$N_{\text{Cmb}}$'),
    ]]

    # Final model
    # wsp.factory("SUM::total(NSig*signal,NSPi*random,NBkg*combinatorial)")
    wsp.factory("SUM::total(NSig*signal,NSPi*random)")

    wsp.factory('set_up_done[1]')

    return variables
