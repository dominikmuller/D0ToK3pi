import ROOT
import ROOT.RooFit as RF
from . import shapes


def setup_pdf(wsp, mode):
    # Only call this function once on a workspace
    if wsp.var('set_up_done'):
        return
    # ROOT.RooMsgService.instance().setGlobalKillBelow(RF.WARNING)
    # ROOT.RooMsgService.instance().setSilentMode(True)

    # Variables for the signal pdf
    sig_m = shapes.d0_cruijff('', wsp, mode)
    bkg_m = shapes.d0_bkg('', wsp, mode)

    # delta random slow
    slow_pi_dm = shapes.dst_d0_delta_mass_bkg('sp', wsp)
    bkg_dm = shapes.dst_d0_delta_mass_bkg('bkg', wsp)
    sig_dm = shapes.dst_d0_johnsonsu('', wsp, mode)
    # Signal 2D pdf
    wsp.factory("PROD::signal({}, {})".format(sig_m, sig_dm))
    wsp.factory("PROD::random({}, {})".format(sig_m, slow_pi_dm))
    wsp.factory("PROD::combinatorial({}, {})".format(bkg_m, bkg_dm))

    wsp.factory(mode.get_rf_vars('NSig'))
    wsp.factory(mode.get_rf_vars('NSPi'))
    wsp.factory(mode.get_rf_vars('NBkg'))

    # Final model
    wsp.factory("SUM::total(NSig*signal,NSPi*random,NBkg*combinatorial)")

    wsp.factory('set_up_done[1]')
