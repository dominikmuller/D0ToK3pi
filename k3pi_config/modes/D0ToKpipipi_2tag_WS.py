from k3pi_utilities import Particle
from k3pi_config import config
from .mode_base import mode_base


class D0ToKpipipi_2tag_WS(mode_base):
    mode = config.D0ToKpipipi_2tag_WS
    tpl = config.ntuple_strip.format(mode)

    K = Particle('K', r'$K^{+}$', pid=config.kaon)
    Pi_SS = Particle('Pi_SS', r'$\pi^{+}$', pid=config.pion)
    Pi_OS1 = Particle('Pi_OS1', r'$\pi^{-}$', pid=config.pion)
    Pi_OS2 = Particle('Pi_OS2', r'$\pi^{-}$', pid=config.pion)
    Mu = Particle('mu', r'$\mu^-$', pid=config.muon)
    Pislow = Particle('Pislow', r'$\pi_{\text{s}}^{+}$', pid=config.slowpion)

    D0 = Particle('D0', r'$D^{0}$', [
        K, Pi_SS, Pi_OS1, Pi_OS2
    ])

    Dst = Particle('Dstp', r'$D^{*+}$', [
        D0, Pislow
    ])
    head = Particle('B0', r'$B$', [
        Dst, Mu
    ])

    def __init__(self, polarity=None, year=None):
        super(D0ToKpipipi_2tag_WS, self).__init__(polarity, year)

__all__ = ['D0ToKpipipi_2tag_WS']
