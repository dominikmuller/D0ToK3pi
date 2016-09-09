from k3pi_utilities import Particle
from k3pi_config import config, mode_base


class D0ToKpipipi_RS(mode_base):
    mode = config.D0ToKpipipi_RS
    tpl = config.ntuple_strip.format(mode)

    Kminus = Particle('Kminus', r'K^{-}', pid=config.kaon)
    Piminus = Particle('Piminus', r'\pi^{-}', pid=config.pion)
    Piplus1 = Particle('Piplus1', r'\pi^{+}', pid=config.pion)
    Piplus2 = Particle('Piplus2', r'\pi^{+}', pid=config.pion)

    D0 = Particle('D0', 'D^{0}', [
        Kminus, Piminus, Piplus1, Piplus2
    ])

    Pislow = Particle('Pislow', 'r\pi_{\text{s}}^{+}', pid=config.slowpion)
    Dst = Particle('Dstp', r'D^{*+}', [
        D0, Pislow
    ])

    def __init__(self, polarity, year):
        super(D0ToKpipipi_RS, self).__init__(polarity, year)
