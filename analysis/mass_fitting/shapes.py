import ROOT
import os

import logging as log

from .fit_config import get_delta_mass_var, get_mass_var


def load_shape_class(name):
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
    return 'pdf_dm_{0}'.format(species)


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
    return 'pdf_dm_{0}'.format(species)


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
    return 'pdf_dm_{0}'.format(species)


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
    return 'pdf_dm_{0}'.format(species)


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
    return 'pdf_dm_sig{0}'.format(species)


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
    return 'pdf_dm_{0}'.format(species)


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
    return 'pdf_m_sig{0}'.format(species)


def d0_bkg(species, workspace, mode):
    mass_var = get_mass_var(workspace).GetName()
    workspace.factory(mode.get_rf_vars('c{}'.format(species)))
    workspace.factory("Chebychev::m_bkg{0}({1},c{0})".format(species, mass_var))
    return 'm_bkg{}'.format(species)
