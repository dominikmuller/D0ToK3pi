from k3pi_config import config
import numpy as np
from k3pi_utilities import logger
log = logger.get_logger('metrics')


class _metric_base(object):
    def __init__(self, wsp):
        self.wsp = wsp
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

    def _get_number_of_signal(self):
        import ROOT.RooFit as RF
        _isig = self._signal.createIntegral(
            self.wsp.set('datavars'), RF.NormSet(self.wsp.set('datavars')),
            RF.Range("signal"))
        log.info('Signal yield: {}'.format(self._nsig.getVal()))
        log.info('Signal integral: {}'.format(_isig.getVal()))
        return self._nsig.getVal() * _isig.getVal()

    def _get_number_of_background(self):
        import ROOT.RooFit as RF
        _icmb = self._comb.createIntegral(
            self.wsp.set('datavars'), RF.NormSet(self.wsp.set('datavars')),
            RF.Range("signal"))
        log.info('Combinatorial yield: {}'.format(self._ncmb.getVal()))
        log.info('Combinatorial integral: {}'.format(_icmb.getVal()))
        _irnd = self._random.createIntegral(
            self.wsp.set('datavars'), RF.NormSet(self.wsp.set('datavars')),
            RF.Range("signal"))
        log.info('Random pion yield: {}'.format(self._nrnd.getVal()))
        log.info('Random pion integral: {}'.format(_irnd.getVal()))
        rnd = self._nrnd.getVal() * _irnd.getVal()
        comb = self._ncmb.getVal() * _icmb.getVal()
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
            return 0
        ret = -(sig/self.sig0)/(0.5 + np.sqrt(bkg))
        log.info('Punzi: {}'.format(ret))
        return ret

_metrics = {
    'punzi': _punzi
}


def get_metric(name):
    return _metrics[name]
