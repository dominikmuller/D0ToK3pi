from k3pi_utilities import Particle
import numpy as np
from math import pi
from k3pi_utilities import PlotConfig
from k3pi_utilities import variables as vars
from k3pi_config import config
from .mode_base import mode_base


class D0ToKpipipi_RS(mode_base):
    mode = config.D0ToKpipipi_RS
    mode_short = 'RS'
    tpl = config.ntuple_strip.format(mode)
    shapes = ('CRU', 'DJSU', 'PID')
    mass_fit_pars = dict(
        # Dst - D0 mass fit
        mu_dm=145.5, error_mu_dm=2, limit_mu_dm=(140, 150),
        sigma_dm_L=0.4, error_sigma_dm_L=0.02, limit_sigma_dm_L=(0.0001, 1.),
        sigma_dm_R=0.4, error_sigma_dm_R=0.02, limit_sigma_dm_R=(0.0001, 1.),
        alpha_dm_L=0.02, error_alpha_dm_L=0.002, limit_alpha_dm_L=(0.0001, 0.05),
        alpha_dm_R=0.02, error_alpha_dm_R=0.002, limit_alpha_dm_R=(0.0001, 0.05),
        a_bkg=1.2, error_a_bkg=0.1, limit_a_bkg=(0.0001, 5.),
        p_bkg=-0.03, error_p_bkg=0.01, limit_p_bkg=(-0.5, 0.5),
        NSig=400000, error_NSig=10000, limit_NSig=(100000, 600000),
        NBkg=40000, error_NBkg=5000, limit_NBkg=(1000, 600000),
        NSPi=40000, error_NSPi=5000, limit_NSPi=(1000, 600000),
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
        nu_m=1., error_nu_m=0.02, limit_nu_m=(0.0000001, 5.),
        tau_m=1.0, error_tau_m=0.02, limit_tau_m=(0.0001, 5.),
        width_1_m=5, error_width_1_m=0.12, limit_width_1_m=(0.0001, 15.),
        nu_1_m=1., error_nu_1_m=0.02, limit_nu_1_m=(0.0000001, 5.),
        tau_1_m=1.0, error_tau_1_m=0.02, limit_tau_1_m=(0.0001, 5.),
        width_2_m=5, error_width_2_m=0.12, limit_width_2_m=(0.0001, 15.),
        nu_2_m=1., error_nu_2_m=0.02, limit_nu_2_m=(0.0000001, 5.),
        tau_2_m=1.0, error_tau_2_m=0.02, limit_tau_2_m=(0.0001, 5.),
        c = 0, error_c = 0.1, limit_c=(-0.5, 0.5)
    )

    K = Particle('K', r'$K^{-}$', pid=config.kaon)
    Pi_SS = Particle('Pi_SS', r'$\pi^{-}$', pid=config.pion)
    Pi_OS1 = Particle('Pi_OS1', r'$\pi^{+}$', pid=config.pion)
    Pi_OS2 = Particle('Pi_OS2', r'$\pi^{+}$', pid=config.pion)

    D0 = Particle('D0', r'$D^{0}$', [
        K, Pi_SS, Pi_OS1, Pi_OS2
    ])

    Pislow = Particle('Pislow', r'$\pi_{\text{s}}^{+}$', pid=config.slowpion)
    Dstp = Particle('Dstp', r'$D^{*+}$', [
        D0, Pislow
    ])
    head = Dstp

    def __init__(self, polarity=None, year=None, mc=None):
        super(D0ToKpipipi_RS, self).__init__(polarity, year, mc)

    bdt_vars = [
        PlotConfig(vars.pt, D0, (50, 0, 15000)),
        PlotConfig(vars.ipchi2, D0, (50, -7, 2.), np.log, r'$\ln(\text{{{}}})$'),
        PlotConfig(vars.vdchi2, D0, (50, 0, 10), np.log, r'$\ln(\text{{{}}})$'),
        PlotConfig(vars.maxdoca, D0, (50, 0, 0.5)),
        PlotConfig(vars.vchi2, head, (50, 0, 20)),
        PlotConfig(vars.vchi2, D0, (50, 0, 20)),
        # PlotConfig(vars.probnnghost, Pislow, (50, 0., 0.3)),
        # PlotConfig(vars.angle, None, (50, 0, 0.03))
        # PlotConfig(vars.dtf_chi2, Dstp, (100, 0, 100)),
    ]
    for d in [4]:
        bdt_vars += [
            PlotConfig(getattr(vars, 'ipchi2{}'.format(d)), None, (50, -2, 10.), np.log, r'$\ln(\text{{{}}})$'),  # NOQA
        ]
    for d in [Pislow]:
        bdt_vars += [
            PlotConfig(vars.pt, d, (50, 0, 3000)),
            PlotConfig(vars.ipchi2, d, (50, -2, 10.), np.log, r'$\ln(\text{{{}}})$'),
        ]
    spectator_vars = [
        PlotConfig(vars.ltime, D0, (50, 0, 0.001)),
        PlotConfig(vars.m12, None, (100, 0, 1600.)),
        PlotConfig(vars.m34, None, (100, 0, 1400.)),
        PlotConfig(vars.cos1, None, (50, -1, 1)),
        PlotConfig(vars.cos2, None, (50, -1, 1)),
        PlotConfig(vars.phi1, None, (50, -pi, pi)),
        PlotConfig(vars.dtf_dm, None, (100, 140.5, 160.5)),
    ]
    just_plot = [
        PlotConfig(vars.probnnp, Pislow, (50, 0., 0.3)),
        PlotConfig(vars.probnne, Pislow, (50, 0., 0.3)),
        PlotConfig(vars.probnnmu, Pislow, (50, 0., 0.3)),
        PlotConfig(vars.m, D0, (100, 1810., 1920.)),
        PlotConfig(vars.dtf_chi2, Dstp, (100, 0, 100)),
    ]
    for d in D0.all_daughters():
        just_plot += [
            PlotConfig(vars.probnnghost, d, (50, 0., 1.)),
            PlotConfig(vars.probnnp, d, (50, 0., 1.)),
            PlotConfig(vars.probnne, d, (50, 0., 1.)),
            PlotConfig(vars.probnnmu, d, (50, 0., 1.)),
        ]

__all__ = ['D0ToKpipipi_RS']
