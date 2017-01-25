from k3pi_config import config
import numpy as np


class _metric_base(object):
    def __init__(self, wsp):
        import ROOT.RooFit as RF
        wsp.var('D0_M').setRange(
            'signal', config.PDG_MASSES['D0'] - 20.,
            config.PDG_MASSES['D0'] + 20.)
        wsp.var('delta_m_dtf').setRange(
            'signal',
            config.PDG_MASSES['Dst'] - config.PDG_MASSES['D0'] - 0.8,
            config.PDG_MASSES['Dst'] - config.PDG_MASSES['D0'] + 0.8)
        self._comb = wsp.pdf('combinatorial')
        self._signal = wsp.pdf('signal')
        self._random = wsp.pdf('random')
        self._nsig = wsp.var('NSig')
        self._nrnd = wsp.var('NSPi')
        self._ncmb = wsp.var('NBkg')

        self._isig = self._signal.createIntegral(
            wsp.set('datavars'), RF.NormSet(wsp.set('datavars')),
            RF.Range("signal"))
        self._icmb = self._comb.createIntegral(
            wsp.set('datavars'), RF.NormSet(wsp.set('datavars')),
            RF.Range("signal"))
        self._irnd = self._random.createIntegral(
            wsp.set('datavars'), RF.NormSet(wsp.set('datavars')),
            RF.Range("signal"))

    def _get_number_of_signal(self):
        return self._nsig.getVal() + self._isig.getVal()

    def _get_number_of_background(self):
        rnd = self._nrnd.getVal() + self._irnd.getVal()
        comb = self._ncmb.getVal() + self._icmb.getVal()
        return rnd + comb


class _punzi(_metric_base):
    def __init__(self, wsp):
        self.name = 'punzi'
        super(_punzi, self).__init__(wsp)
        self.sig0 = self._get_number_of_signal()

    def __call__(self):
        sig = self._get_number_of_signal()
        bkg = self._get_number_of_background()
        if self.sig0 <= 0 or sig <= 0 or bkg <= 0:
            return np.nan
        return -(sig/self.sig0)/(0.5 + np.sqrt(bkg))

_metrics = {
    'punzi': _punzi
}


def get_metric(name):
    return _metrics[name]
