from k3pi_utilities import Particle
from k3pi_utilities import PlotConfig
from k3pi_utilities import variables as vars
import numpy as np
from k3pi_config import config
from .mode_base import mode_base


class D0ToKpipipi_WS(mode_base):
    shapes = ('CRU', 'JSU', 'PID')
    mass_fit_pars = dict(
        # Dst - D0 mass fit
        mu_dm=145.5, error_2_mu_dm=2, limit_mu_dm=(140, 150),
        sigma_dm_L=0.2, error_sigma_dm_L=0.02, limit_sigma_dm_L=(0.0001, 1.),
        sigma_dm_R=0.2, error_sigma_dm_R=0.02, limit_sigma_dm_R=(0.0001, 1.),
        alpha_dm_L=0.2, error_alpha_dm_L=0.02, limit_alpha_dm_L=(0.0001, 1.),
        alpha_dm_R=0.2, error_alpha_dm_R=0.02, limit_alpha_dm_R=(0.0001, 1.),
        a_bkg=1.2, error_a_bkg=0.1, limit_a_bkg=(0.0001, 5.),
        p_bkg=-0.03, error_p_bkg=0.01, limit_p_bkg=(-0.5, 0.5),
        NSig=10000, error_NSig=10000, limit_NSig=(100, 100000),
        NBkg=20000, error_NBkg=5000, limit_NBkg=(100, 600000),
        NSPi=20000, error_NSPi=5000, limit_NSPi=(100, 600000),
        width_dm=0.4, error_width_dm=0.02, limit_width_dm=(0.0001, 1.),
        nu_dm=1.0, error_nu_dm=0.02, limit_nu_dm=(0.0001, 5.),
        tau_dm=1.0, error_tau_dm=0.02, limit_tau_dm=(0.0001, 5.),
        width_1_dm=0.4, error_width_1_dm=0.02, limit_width_1_dm=(0.0001, 1.),
        nu_1_dm=1.0, error_nu_1_dm=0.02, limit_nu_1_dm=(0.0001, 5.),
        tau_1_dm=1.0, error_tau_1_dm=0.02, limit_tau_1_dm=(0.0001, 5.),
        width_2_dm=0.4, error_width_2_dm=0.02, limit_width_2_dm=(0.0001, 1.),
        nu_2_dm=1.0, error_nu_2_dm=0.02, limit_nu_2_dm=(0.0001, 5.),
        tau_2_dm=1.0, error_tau_2_dm=0.02, limit_tau_2_dm=(0.0001, 5.),
        # D0 mass fit
        mu_m=1865., error_mu_m=0.2, limit_mu_m=(1855., 1875.),
        sigma_m_L=5, error_sigma_m_L=0.1, limit_sigma_m_L=(0.001, 15.),
        sigma_m_R=5, error_sigma_m_R=0.1, limit_sigma_m_R=(0.001, 15.),
        alpha_m_L=0.2, error_alpha_m_L=0.001, limit_alpha_m_L=(0.001, 1.),
        alpha_m_R=0.2, error_alpha_m_R=0.001, limit_alpha_m_R=(0.001, 1.),
        width_m=5, error_width_m=0.12, limit_width_m=(0.0001, 15.),
        nu_m=0., error_nu_m=0.02,
        tau_m=1.0, error_tau_m=0.02, limit_tau_m=(0.0001, 5.),
        width_1_m=5, error_width_1_m=0.12, limit_width_1_m=(0.0001, 15.),
        nu_1_m=0., error_nu_1_m=0.02,
        tau_1_m=1.0, error_tau_1_m=0.02, limit_tau_1_m=(0.0001, 5.),
        width_2_m=5, error_width_2_m=0.12, limit_width_2_m=(0.0001, 15.),
        nu_2_m=0., error_nu_2_m=0.02,
        tau_2_m=1.0, error_tau_2_m=0.02, limit_tau_2_m=(0.0001, 5.),
        c = 0, error_c = 0.1, limit_c=(-0.5, 0.5)
    )
    mode = config.D0ToKpipipi_WS
    tpl = config.ntuple_strip.format(mode)

    K = Particle('K', r'$K^{+}$', pid=config.kaon)
    Pi_SS = Particle('Pi_SS', r'$\pi^{+}$', pid=config.pion)
    Pi_OS1 = Particle('Pi_OS1', r'$\pi^{-}$', pid=config.pion)
    Pi_OS2 = Particle('Pi_OS2', r'$\pi^{-}$', pid=config.pion)

    D0 = Particle('D0', '$D^{0}$', [
        K, Pi_SS, Pi_OS1, Pi_OS2
    ])

    Pislow = Particle('Pislow', r'$\pi_{\text{s}}^{+}$', pid=config.slowpion)
    Dstp = Particle('Dstp', r'$D^{*+}$', [
        D0, Pislow
    ])
    head = Dstp

    def __init__(self, polarity=None, year=None):
        super(D0ToKpipipi_WS, self).__init__(polarity, year)

    bdt_vars = [
        PlotConfig(vars.pt, D0, (50, 0, 15000)),
        PlotConfig(vars.ipchi2, D0, (50, -7, 2.), np.log, r'$\ln(\text{{{}}})$'),
        PlotConfig(vars.dira, D0, (50, 0.9998, 1)),
        PlotConfig(vars.vdchi2, D0, (50, 0, 10), np.log, r'$\ln(\text{{{}}})$'),
        PlotConfig(vars.mindoca, D0, (50, 0, 0.1)),
        PlotConfig(vars.maxdoca, D0, (50, 0, 0.5)),
        PlotConfig(vars.dtf_chi2, head, (50, 0, 60)),
        # PlotConfig(vars.angle, None, (50, 0, 0.03))
    ]
    for d in Dstp.all_daughters():
        bdt_vars += [
            PlotConfig(vars.ipchi2, d, (50, -2, 10.), np.log, r'$\ln(\text{{{}}})$'),
        ]
    for d in [Pislow]:
        bdt_vars += [
            PlotConfig(vars.pt, d, (50, 0, 8000)),
            PlotConfig(vars.probnnghost, d, (50, 0., 0.3)),
            PlotConfig(vars.probnnp, d, (50, 0., 1.0)),
            PlotConfig(vars.probnne, d, (50, 0., 1.0)),
            PlotConfig(vars.probnnmu, d, (50, 0., 1.0)),
        ]
    spectator_vars = [
        PlotConfig(vars.pt, d, (50, 0, 8000)),
        PlotConfig(vars.ltime, D0, (50, 0, 0.001)),
    ]


__all__ = ['D0ToKpipipi_WS']
