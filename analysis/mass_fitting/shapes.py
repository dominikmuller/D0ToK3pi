import os

import logging as log

from .fit_config import get_delta_mass_var, get_mass_var


def load_shape_class(name):
    import ROOT
    """Load the shape class corresponding to name.

    First an attempt is made to load a compiled shared library name.so, if this
    is not found the file name.cxx is loaded dynamically.
    Compiling the class in to a shared library via rootcint dictionaries is
    more robust, as dynamically loaded .cxx files cannot be persisted in .root
    files.
    """
    # See if the class is already loaded
    try:
        getattr(ROOT, name)
    except AttributeError:
        # Find the path of *this* file, the one you're looking at

        # Build the path to the shape class directory
        base = os.environ['SHAPECLASSES']

        # Try to load the shared library, falling back to the .cxx file
        so = os.path.join(base, '{0}.so'.format(name))
        if os.path.exists(so) and ROOT.gSystem.Load(so) == 0:
            log.info('Loaded shape class shared library {0}.so'.format(name))
        else:
            log.warning((
                'Could not find shared library {0}.so, '
                'consider compiling the class {0} to allow persistency'
            ).format(name))
            cxx = os.path.join(base, '{0}.cxx'.format(name))
            ROOT.gROOT.ProcessLine('#include "{0}"'.format(cxx))


def dst_d0_delta_mass_bkg(species, workspace):
    """Add empirical D*-D0 delta mass background shape PDF to workspace.

    RooDstD0BG has parameters dm, dm0, a, b, c.
    They are passed in order (dm, dm0, c, a, b).
    The functional form is
        y = (1 - exp((dm0-dm)/c))*(dm/dm0)^a + b*(dm/dm0 - 1)
    """
    dmass_var = get_delta_mass_var(workspace).GetName()
    # Threshold at the charged pion mass
    workspace.factory('threshold_dm_{0}[139.57]'.format(species))
    workspace.factory('a_dm_{0}[-1, -10, 10]'.format(species))
    workspace.factory('b_dm_{0}[0]'.format(species))
    workspace.factory('c_dm_{0}[0.5, -2., 4.]'.format(species))
    workspace.factory((
        'RooDstD0BG::pdf_dm_{0}('
        '{1}, threshold_dm_{0}, c_dm_{0}, a_dm_{0}, b_dm_{0}'
        ')'
    ).format(species, dmass_var))
    vs = [
        ('threshold_dm_{0}'.format(species), r'$\Delta m^0_{{{}}}$'.format(species)),  # NOQA
        ('a_dm_{0}'.format(species), r'$a_{{\Delta m, {}}}$'.format(species)),
        ('b_dm_{0}'.format(species), r'$a_{{\Delta m, {}}}$'.format(species)),
        ('c_dm_{0}'.format(species), r'$a_{{\Delta m, {}}}$'.format(species)),
    ]
    return 'pdf_dm_{0}'.format(species), vs


def dst_d0_pid_bkg(species, workspace):
    """Add v2 of empirical D*-D0 delta mass background shape PDF to workspace.

    Expression used has parameters dm, dm0, a, b, and the functional form is
        y = (dm - dm0)^A * exp(B*dm)
    Taken from LHCb-ANA-2014-016.
    """
    load_shape_class('RooBackground')
    dmass_var = get_delta_mass_var(workspace).GetName()
    # Threshold at the charged pion mass
    workspace.factory('a_dm_{0}[-2, -30, 30]'.format(species))
    workspace.factory((
        'RooBackground::pdf_dm_{0}('
        '{1}, a_dm_{0}'
        ')'
    ).format(species, dmass_var))
    vs = [
        ('a_dm_{0}'.format(species), r'$a_{{\Delta m, {}}}$'.format(species)),
    ]
    return 'pdf_dm_{0}'.format(species), vs


def dst_d0_delta_mass_bkg_two(species, workspace):
    """Add v2 of empirical D*-D0 delta mass background shape PDF to workspace.

    Expression used has parameters dm, dm0, a, b, and the functional form is
        y = (dm - dm0)^A * exp(B*dm)
    Taken from LHCb-ANA-2014-016.
    """
    dmass_var = get_delta_mass_var(workspace).GetName()
    # Threshold at the charged pion mass
    workspace.factory('threshold_dm_{0}[139.57]'.format(species))
    workspace.factory('a_dm_{0}[0.5, 0.1, 1]'.format(species))
    workspace.factory('b_dm_{0}[0]'.format(species))
    workspace.factory((
        'EXPR::pdf_dm_{0}('
        "'((@0 - @1)^@2)*exp(@3*@0)',"
        '{{{1}, threshold_dm_{0}, a_dm_{0}, b_dm_{0}}}'
        ')'
    ).format(species, dmass_var))
    vs = [
        ('threshold_dm_{0}'.format(species), r'$\Delta m^0_{{{}}}$'.format(species)),  # NOQA
        ('a_dm_{0}'.format(species), r'$a_{{\Delta m, {}}}$'.format(species)),
        ('b_dm_{0}'.format(species), r'$a_{{\Delta m, {}}}$'.format(species)),
    ]
    return 'pdf_dm_{0}'.format(species), vs


def dst_d0_power_bkg(species, workspace):
    """Add empirical power law D*-D0 delta mass background PDF to workspace.

    Given a list of coefficients c_{i}, this shape is formally defined by the
    sum
        f(x) = \sum_{i} c_i*(dm-dm0)^(i - 1/2).
    """
    load_shape_class('RooDstD0PowerBG')
    dmass_var = get_delta_mass_var(workspace).GetName()
    # Threshold at the charged pion mass
    workspace.factory('threshold_dm_{0}[139.57]'.format(species))
    workspace.factory('a_dm_{0}[0.2, 0, 0.5]'.format(species))
    workspace.factory('b_dm_{0}[0, -0.001, 0.001]'.format(species))
    workspace.factory('c_dm_{0}[0, -0.001, 0.001]'.format(species))
    workspace.factory((
        'RooDstD0PowerBG::pdf_dm_{0}('
        '{1}, threshold_dm_{0}, a_dm_{0}, b_dm_{0}, c_dm_{0}'
        ')'
    ).format(species, dmass_var))
    vs = [
        ('threshold_dm_{0}'.format(species), r'$\Delta m^0_{{{}}}$'.format(species)),  # NOQA
        ('a_dm_{0}'.format(species), r'$a_{{\Delta m, {}}}$'.format(species)),
        ('b_dm_{0}'.format(species), r'$a_{{\Delta m, {}}}$'.format(species)),
        ('c_dm_{0}'.format(species), r'$a_{{\Delta m, {}}}$'.format(species)),
    ]
    return 'pdf_dm_{0}'.format(species), vs


def dst_d0_cruijff(species, workspace, mode):
    """Add empirical power law D*-D0 delta mass background PDF to workspace.

    Given a list of coefficients c_{i}, this shape is formally defined by the
    sum
        f(x) = \sum_{i} c_i*(dm-dm0)^(i - 1/2).
    """
    load_shape_class('RooCruijff')
    dmass_var = get_delta_mass_var(workspace).GetName()
    workspace.factory(mode.get_rf_vars('mu_dm{0}'.format(species)))
    workspace.factory(mode.get_rf_vars('sigma_dm_L{0}'.format(species)))
    workspace.factory(mode.get_rf_vars('sigma_dm_R{0}'.format(species)))
    workspace.factory(mode.get_rf_vars('alpha_dm_L{0}'.format(species)))
    workspace.factory(mode.get_rf_vars('alpha_dm_R{0}'.format(species)))
    workspace.factory((
        'RooCruijff::pdf_dm_sig{0}({1}, mu_dm{0}, sigma_dm_L{0},'
        ' sigma_dm_R{0}, alpha_dm_L{0}, alpha_dm_R{0})'
    ).format(species, dmass_var))
    vs = [
        ('mu_dm{0}'.format(species), r'$\mu_{\Delta m}$'),
        ('sigma_dm_L{0}'.format(species), r'$\sigma^L_{\Delta m}$'),
        ('sigma_dm_R{0}'.format(species), r'$\sigma^R_{\Delta m}$'),
        ('alpha_dm_L{0}'.format(species), r'$\alpha^L_{\Delta m}$'),
        ('alpha_dm_R{0}'.format(species), r'$\alpha^R_{\Delta m}$'),
    ]
    return 'pdf_dm_sig{0}'.format(species), vs


def dst_d0_johnsonsu(species, workspace, mode):
    """Add v2 of empirical D*-D0 delta mass background shape PDF to workspace.

    Expression used has parameters dm, dm0, a, b, and the functional form is
        y = (dm - dm0)^A * exp(B*dm)
    Taken from LHCb-ANA-2014-016.
    """
    load_shape_class('RooJohnsonSU')
    dmass_var = get_delta_mass_var(workspace).GetName()
    workspace.factory(mode.get_rf_vars('mu_dm{0}'.format(species)))
    workspace.factory(mode.get_rf_vars('width_dm{0}'.format(species)))
    workspace.factory(mode.get_rf_vars('nu_dm{0}'.format(species)))
    workspace.factory(mode.get_rf_vars('tau_dm{0}'.format(species)))
    # Threshold at the charged pion mass
    workspace.factory((
        'RooJohnsonSU::pdf_dm_{0}('
        '{1},mu_dm{0},width_dm{0},nu_dm{0},tau_dm{0}'
        ')'
    ).format(species, dmass_var))
    vs = [
        ('mu_dm{0}'.format(species), r'$\mu_{\Delta m}$'),
        ('width_dm{0}'.format(species), r'$\sigma_{\Delta m}$'),
        ('nu_dm{0}'.format(species), r'$\nu_{\Delta m}$'),
        ('tau_dm{0}'.format(species), r'$\tau_{\Delta m}$'),
    ]
    return 'pdf_dm_{0}'.format(species), vs


def d0_johnsonsu(species, workspace, mode):
    """Add v2 of empirical D*-D0 delta mass background shape PDF to workspace.

    Expression used has parameters dm, dm0, a, b, and the functional form is
        y = (dm - dm0)^A * exp(B*dm)
    Taken from LHCb-ANA-2014-016.
    """
    load_shape_class('RooJohnsonSU')
    mass_var = get_mass_var(workspace).GetName()
    workspace.factory(mode.get_rf_vars('mu_m{0}'.format(species)))
    workspace.factory(mode.get_rf_vars('width_m{0}'.format(species)))
    workspace.factory(mode.get_rf_vars('nu_m{0}'.format(species)))
    workspace.factory(mode.get_rf_vars('tau_m{0}'.format(species)))
    # Threshold at the charged pion mass
    workspace.factory((
        'RooJohnsonSU::pdf_m_{0}('
        '{1},mu_m{0},width_m{0},nu_m{0},tau_m{0}'
        ')'
    ).format(species, mass_var))
    vs = {
        ('mu_m{0}'.format(species), r'$\mu_{m}$'),
        ('width_m{0}'.format(species), r'$\sigma_{m}$'),
        ('nu_m{0}'.format(species), r'$\nu_{m}$'),
        ('tau_m{0}'.format(species), r'$\tau_{m}$'),
    }
    return 'pdf_m_{0}'.format(species), vs


def d0_double_johnsonsu(species, workspace, mode):
    mass_var = get_mass_var(workspace).GetName()
    vs = [
        ('mu_m'.format(species), r'$\mu_{m}$'),
        ('width_1_m'.format(species), r'$\sigma_{m,1}$'),
        ('nu_1_m'.format(species), r'$\nu_{m,1}$'),
        ('tau_1_m'.format(species), r'$\tau_{m,1}$'),
        ('width_2_m'.format(species), r'$\sigma_{m,2}$'),
        ('nu_2_m'.format(species), r'$\nu_{m,2}$'),
        ('tau_2_m'.format(species), r'$\tau_{m,2}$'),
        ('ds_fraction_m'.format(species), r'$f_{m}$'),
    ]
    return double_johnsonsu('m', workspace, mode, mass_var), vs


def dst_d0_double_johnsonsu(species, workspace, mode):
    dmass_var = get_delta_mass_var(workspace).GetName()
    vs = [
        ('mu_dm'.format(species), r'$\mu_{\Delta m}$'),
        ('width_1_dm'.format(species), r'$\sigma_{\Delta m,1}$'),
        ('nu_1_dm'.format(species), r'$\nu_{\Delta m,1}$'),
        ('tau_1_dm'.format(species), r'$\tau_{\Delta m,1}$'),
        ('width_2_dm'.format(species), r'$\sigma_{\Delta m,2}$'),
        ('nu_2_dm'.format(species), r'$\nu_{\Delta m,2}$'),
        ('tau_2_dm'.format(species), r'$\tau_{\Delta m,2}$'),
        ('ds_fraction_dm'.format(species), r'$f_{\Delta m}$'),
    ]
    return double_johnsonsu('dm', workspace, mode, dmass_var), vs


def double_johnsonsu(species, workspace, mode, var):
    """Add v2 of empirical D*-D0 delta mass background shape PDF to workspace.

    Expression used has parameters dm, dm0, a, b, and the functional form is
        y = (dm - dm0)^A * exp(B*dm)
    Taken from LHCb-ANA-2014-016.
    """
    load_shape_class('RooJohnsonSU')
    workspace.factory(mode.get_rf_vars('mu_{0}'.format(species)))
    workspace.factory(mode.get_rf_vars('width_1_{0}'.format(species)))
    workspace.factory(mode.get_rf_vars('nu_1_{0}'.format(species)))
    workspace.factory(mode.get_rf_vars('tau_1_{0}'.format(species)))
    workspace.factory(mode.get_rf_vars('width_2_{0}'.format(species)))
    workspace.factory(mode.get_rf_vars('nu_2_{0}'.format(species)))
    workspace.factory(mode.get_rf_vars('tau_2_{0}'.format(species)))
    workspace.factory('ds_fraction_{0}[0.5,0,1]'.format(species))
    # Threshold at the charged pion mass
    workspace.factory((
        'RooJohnsonSU::pdf_1_{0}('
        '{1},mu_{0},width_1_{0},nu_1_{0},tau_1_{0}'
        ')'
    ).format(species, var))
    workspace.factory((
        'RooJohnsonSU::pdf_2_{0}('
        '{1},mu_{0},width_2_{0},nu_2_{0},tau_2_{0}'
        ')'
    ).format(species, var))
    workspace.factory((
        'SUM::pdf_{0}('
        'ds_fraction_{0}*pdf_1_{0},pdf_2_{0}'
        ')'
    ).format(species))
    return 'pdf_{0}'.format(species)


def d0_cruijff(species, workspace, mode):
    """Add empirical power law D*-D0 delta mass background PDF to workspace.

    Given a list of coefficients c_{i}, this shape is formally defined by the
    sum
        f(x) = \sum_{i} c_i*(dm-dm0)^(i - 1/2).
    """
    load_shape_class('RooCruijff')
    mass_var = get_mass_var(workspace).GetName()
    workspace.factory(mode.get_rf_vars('mu_m{0}'.format(species)))
    workspace.factory(mode.get_rf_vars('sigma_m_L{0}'.format(species)))
    workspace.factory(mode.get_rf_vars('sigma_m_R{0}'.format(species)))
    workspace.factory(mode.get_rf_vars('alpha_m_L{0}'.format(species)))
    workspace.factory(mode.get_rf_vars('alpha_m_R{0}'.format(species)))
    workspace.factory((
        'RooCruijff::pdf_m_sig{0}({1}, mu_m{0}, sigma_m_L{0},'
        ' sigma_m_R{0}, alpha_m_L{0}, alpha_m_R{0})'
    ).format(species, mass_var))
    vs = [
        ('mu_m{0}'.format(species), r'$\mu_{m}$'),
        ('sigma_m_L{0}'.format(species), r'$\sigma^L_{m}$'),
        ('sigma_m_R{0}'.format(species), r'$\sigma^R_{m}$'),
        ('alpha_m_L{0}'.format(species), r'$\alpha^L_{m}$'),
        ('alpha_m_R{0}'.format(species), r'$\alpha^R_{m}$'),
    ]
    return 'pdf_m_sig{0}'.format(species), vs


def d0_bkg(species, workspace, mode):
    mass_var = get_mass_var(workspace).GetName()
    workspace.factory(mode.get_rf_vars('c{}'.format(species)))
    workspace.factory("Chebychev::m_bkg{0}({1},c{0})".format(species, mass_var))
    vs = [
        ('c{0}'.format(species), r'$c_{m}$')
    ]
    workspace.var('c{0}'.format(species)).setConstant()
    return 'm_bkg{}'.format(species), vs


dst_d0_shapes = {
    'CRU': dst_d0_cruijff,
    'JSU': dst_d0_johnsonsu,
    'DJSU': dst_d0_double_johnsonsu,
    'PID': dst_d0_pid_bkg,
    'DM1': dst_d0_delta_mass_bkg,
    'DM2': dst_d0_delta_mass_bkg_two
}

d0_shapes = {
    'CRU': d0_cruijff,
    'JSU': d0_johnsonsu,
    'DJSU': d0_double_johnsonsu,
}
