from k3pi_utilities import Particle
from k3pi_utilities import PlotConfig
from k3pi_utilities import variables as vars
import numpy as np
from math import pi
from k3pi_config import config
from .mode_base import mode_base
from .D0ToKpipipi_RS import D0ToKpipipi_RS


class D0ToKpipipi_WS(mode_base):
    shapes = ('JSU', 'JSU', 'DM1')
    mode_short = 'WS'
    mass_fit_pars = dict(
        # Dst - D0 mass fit
        mu_dm=145.5, error_2_mu_dm=2, limit_mu_dm=(140, 150),
        sigma_dm_L=0.2, error_sigma_dm_L=0.02, limit_sigma_dm_L=(0.0001, 1.),
        sigma_dm_R=0.2, error_sigma_dm_R=0.02, limit_sigma_dm_R=(0.0001, 1.),
        alpha_dm_L=0.2, error_alpha_dm_L=0.02, limit_alpha_dm_L=(0.0001, 1.),
        alpha_dm_R=0.2, error_alpha_dm_R=0.02, limit_alpha_dm_R=(0.0001, 1.),
        a_bkg=1.2, error_a_bkg=0.1, limit_a_bkg=(0.0001, 5.),
        p_bkg=-0.03, error_p_bkg=0.01, limit_p_bkg=(-0.5, 0.5),
        NSig=1500., error_NSig=50, limit_NSig=(100, 100000),
        NBkg=0, error_NBkg=50, limit_NBkg=(0, 600000),
        NSPi=40000, error_NSPi=50, limit_NSPi=(100, 600000),
        width_dm=0.4, error_width_dm=0.02, limit_width_dm=(0.0001, 1.5),
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
        width_m=12, error_width_m=0.12, limit_width_m=(0.0001, 15.),
        nu_m=0., error_nu_m=0.02,
        tau_m=1.0, error_tau_m=0.02, limit_tau_m=(0.0001, 5.),
        width_1_m=12, error_width_1_m=0.12, limit_width_1_m=(0.0001, 15.),
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

    def __init__(self, polarity=None, year=None, mc=None):
        super(D0ToKpipipi_WS, self).__init__(polarity, year, mc)

    mass_var = D0ToKpipipi_RS.mass_var
    ltime_var = D0ToKpipipi_RS.ltime_var
    dmass_var = D0ToKpipipi_RS.dmass_var
    phsp_vars = D0ToKpipipi_RS.phsp_vars

    bdt_vars = D0ToKpipipi_RS.bdt_vars
    rand_spi_bdt_vars = D0ToKpipipi_RS.rand_spi_bdt_vars
    comb_bkg_bdt_vars = D0ToKpipipi_RS.comb_bkg_bdt_vars

    spectator_vars = D0ToKpipipi_RS.spectator_vars

    just_plot = D0ToKpipipi_RS.just_plot


__all__ = ['D0ToKpipipi_WS']
