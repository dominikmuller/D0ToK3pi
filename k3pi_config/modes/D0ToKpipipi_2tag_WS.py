from k3pi_utilities import Particle
from k3pi_config import config
from .mode_base import mode_base


class D0ToKpipipi_2tag_WS(mode_base):
    shapes = ('DJSU', 'JSU', 'PID')
    mass_fit_pars = dict(
        # Dst - D0 mass fit
        mu_dm=145.5, error_2_mu_dm=2, limit_mu_dm=(140, 150),
        sigma_dm_L=0.2, error_sigma_dm_L=0.02, limit_sigma_dm_L=(0.0001, 1.),
        sigma_dm_R=0.2, error_sigma_dm_R=0.02, limit_sigma_dm_R=(0.0001, 1.),
        alpha_dm_L=0.2, error_alpha_dm_L=0.02, limit_alpha_dm_L=(0.0001, 1.),
        alpha_dm_R=0.2, error_alpha_dm_R=0.02, limit_alpha_dm_R=(0.0001, 1.),
        a_bkg=1.2, error_a_bkg=0.1, limit_a_bkg=(0.0001, 5.),
        p_bkg=-0.03, error_p_bkg=0.01, limit_p_bkg=(-0.5, 0.5),
        NSig=4000, error_NSig=10, limit_NSig=(3000, 10000),
        NBkg=40000, error_NBkg=5, limit_NBkg=(30000, 50000),
        NSPi=100, error_NSPi=5, limit_NSPi=(1, 600000),
        width_dm=0.7, error_width_dm=0.02, limit_width_dm=(0.0001, 1.),
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
        width_m=9, error_width_m=0.12, limit_width_m=(0.0001, 15.),
        nu_m=0., error_nu_m=0.02, # limit_nu_m=(0.0000001, 5.),
        tau_m=1.0, error_tau_m=0.02, limit_tau_m=(0.0001, 5.),
        width_1_m=5, error_width_1_m=0.12, limit_width_1_m=(0.0001, 15.),
        nu_1_m=0., error_nu_1_m=0.02, # limit_nu_1_m=(0.0000001, 5.),
        tau_1_m=1.0, error_tau_1_m=0.02, limit_tau_1_m=(0.0001, 5.),
        width_2_m=5, error_width_2_m=0.12, limit_width_2_m=(0.0001, 15.),
        nu_2_m=0., error_nu_2_m=0.02, # limit_nu_2_m=(0.0000001, 5.),
        tau_2_m=1.0, error_tau_2_m=0.02, limit_tau_2_m=(0.0001, 5.),
        c = 0, error_c = 0.1, limit_c=(-0.5, 0.5)
    )
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

    Dstp = Particle('Dstp', r'$D^{*+}$', [
        D0, Pislow
    ])
    B0 = Particle('B0', r'$B$', [
        Dstp, Mu
    ])
    head = B0

    def __init__(self, polarity=None, year=None):
        super(D0ToKpipipi_2tag_WS, self).__init__(polarity, year)

__all__ = ['D0ToKpipipi_2tag_WS']
