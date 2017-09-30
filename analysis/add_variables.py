from k3pi_utilities import variables as vars
from k3pi_utilities.selective_load import selective_load, is_dummy_run
from k3pi_utilities.decorator_utils import pop_arg
from k3pi_utilities.buffer import buffer_load, remove_buffer_for_function
from k3pi_utilities import parser
from k3pi_utilities.debugging import call_debug
from k3pi_config.modes import gcm
from k3pi_cpp import (compute_delta_angle, vec_phsp_variables,
                      double_misid_d0_mass, change_slowpi_d0,
                      change_slowpi_d0_ws, vec_compute_four_delta_mass)
from k3pi_config import config
import pandas as pd


def append_angle(df):
    extra = _dstp_slowpi_angle()
    df[extra.name] = extra


def append_ltime_ratio(df):
    extra = _ltime_ratio()
    df[extra.name] = extra


def append_phsp(df):
    extra = phsp_variables()
    for c in extra.columns:
        df[c] = extra[c]


def append_dtf_ip_diff(df):
    extra = _dtf_ip_diff()
    df['dtf_ip_diff'] = extra


@buffer_load
@pop_arg(selective_load, allow_for=[None, 'mc'])
@call_debug
def _dstp_slowpi_angle(df):

    mode = gcm()
    ret = compute_delta_angle(
        df[vars.pt(mode.D0)], df[vars.eta(mode.D0)], df[vars.phi(mode.D0)],
        df[vars.m(mode.D0)],
        df[vars.pt(mode.Pislow)], df[vars.eta(mode.Pislow)],
        df[vars.phi(mode.Pislow)],
        config.PDG_MASSES[config.pion],
    )
    if is_dummy_run(df):
        return 1
    return pd.Series(ret, name='dstp_slowpi_angle', index=df.index)


@buffer_load
@pop_arg(selective_load, allow_for=[None, 'mc'])
@call_debug
def _ltime_ratio(df):

    mode = gcm()
    ret = df[vars.ltime(mode.D0)] / config.Dz_ltime
    if is_dummy_run(df):
        return 1
    return pd.Series(ret, name='ltime_ratio', index=df.index)


@buffer_load
@selective_load
@call_debug
def phsp_variables(df):
    """Returns m12, m34, cos1, cos2, phi1"""
    mode = gcm()

    # implementation using pybind11::array requires some special treatment
    # here, otherwise the passed arrays are of non-matching type.
    if not is_dummy_run(df):
        vals = vec_phsp_variables(
            df[vars.dtf_pt(mode.Pi_OS1)], df[vars.dtf_eta(mode.Pi_OS1)],
            df[vars.dtf_phi(mode.Pi_OS1)], config.PDG_MASSES['Pi'],
            df[vars.dtf_pt(mode.Pi_SS)], df[vars.dtf_eta(mode.Pi_SS)],
            df[vars.dtf_phi(mode.Pi_SS)], config.PDG_MASSES['Pi'],
            df[vars.dtf_pt(mode.K)], df[vars.dtf_eta(mode.K)],
            df[vars.dtf_phi(mode.K)], config.PDG_MASSES['K'],
            df[vars.dtf_pt(mode.Pi_OS2)], df[vars.dtf_eta(mode.Pi_OS2)],
            df[vars.dtf_phi(mode.Pi_OS2)], config.PDG_MASSES['Pi']
        )
        return pd.DataFrame({'m12': vals[0],
                             'm34': vals[1],
                             'cos1': vals[2],
                             'cos2': vals[3],
                             'phi1': vals[4]},
                            index=df.index)
    else:
        vals = (
            df[vars.dtf_pt(mode.K)], df[vars.dtf_eta(mode.K)],
            df[vars.dtf_phi(mode.K)], config.PDG_MASSES['K'],
            df[vars.dtf_pt(mode.Pi_OS1)], df[vars.dtf_eta(mode.Pi_OS1)],
            df[vars.dtf_phi(mode.Pi_OS1)], config.PDG_MASSES['Pi'],
            df[vars.dtf_pt(mode.Pi_SS)], df[vars.dtf_eta(mode.Pi_SS)],
            df[vars.dtf_phi(mode.Pi_SS)], config.PDG_MASSES['Pi'],
            df[vars.dtf_pt(mode.Pi_OS2)], df[vars.dtf_eta(mode.Pi_OS2)],
            df[vars.dtf_phi(mode.Pi_OS2)], config.PDG_MASSES['Pi'])
        return 1.


@buffer_load
@pop_arg(selective_load, allow_for=[None, 'mc'])
@call_debug
def double_misid_d0(df):
    """Returns d0 mass with changed kaon and ss pion mass hypthesis"""
    mode = gcm()

    val = double_misid_d0_mass(
        df[vars.dtf_pt(mode.K)], df[vars.dtf_eta(mode.K)],
        df[vars.dtf_phi(mode.K)], config.PDG_MASSES['Pi'],
        df[vars.dtf_pt(mode.Pi_SS)], df[vars.dtf_eta(mode.Pi_SS)],
        df[vars.dtf_phi(mode.Pi_SS)], config.PDG_MASSES['K'],
        df[vars.dtf_pt(mode.Pi_OS1)], df[vars.dtf_eta(mode.Pi_OS1)],
        df[vars.dtf_phi(mode.Pi_OS1)], config.PDG_MASSES['Pi'],
        df[vars.dtf_pt(mode.Pi_OS2)], df[vars.dtf_eta(mode.Pi_OS2)],
        df[vars.dtf_phi(mode.Pi_OS2)], config.PDG_MASSES['Pi'])
    if not is_dummy_run(df):
        return pd.Series(val, name=vars.m(gcm().D0), index=df.index)
    return 1


@buffer_load
@pop_arg(selective_load, allow_for=[None, 'mc'])
@call_debug
def double_misid(df):
    """Constructs dataframe of all double misid masses to play about"""
    mode = gcm()
    if is_dummy_run(df):
        valSS = (
            df[vars.pt(mode.K)], df[vars.eta(mode.K)],
            df[vars.phi(mode.K)], config.PDG_MASSES['Pi'],
            df[vars.pt(mode.Pi_SS)], df[vars.eta(mode.Pi_SS)],
            df[vars.phi(mode.Pi_SS)], config.PDG_MASSES['K'],
            df[vars.pt(mode.Pi_OS1)], df[vars.eta(mode.Pi_OS1)],
            df[vars.phi(mode.Pi_OS1)], config.PDG_MASSES['Pi'],
            df[vars.pt(mode.Pi_OS2)], df[vars.eta(mode.Pi_OS2)],
            df[vars.phi(mode.Pi_OS2)], config.PDG_MASSES['Pi'],
            df[vars.pt(mode.Pislow)], df[vars.eta(mode.Pislow)],
            df[vars.phi(mode.Pislow)], config.PDG_MASSES['Pi']
        )
        return 1.

    # First some sortingbdtdata
    os1bigger = df[vars.pt(mode.Pi_OS1)] > df[vars.pt(mode.Pi_OS2)]
    os2bigger = df[vars.pt(mode.Pi_OS1)] <= df[vars.pt(mode.Pi_OS2)]

    df.loc[os1bigger, 'H_PT'] = df[vars.pt(mode.Pi_OS1)]
    df.loc[os1bigger, 'L_PT'] = df[vars.pt(mode.Pi_OS2)]
    df.loc[os1bigger, 'H_ETA'] = df[vars.eta(mode.Pi_OS1)]
    df.loc[os1bigger, 'L_ETA'] = df[vars.eta(mode.Pi_OS2)]
    df.loc[os1bigger, 'H_PHI'] = df[vars.phi(mode.Pi_OS1)]
    df.loc[os1bigger, 'L_PHI'] = df[vars.phi(mode.Pi_OS2)]
    df.loc[os2bigger, 'H_PT'] = df[vars.pt(mode.Pi_OS2)]
    df.loc[os2bigger, 'L_PT'] = df[vars.pt(mode.Pi_OS1)]
    df.loc[os2bigger, 'H_ETA'] = df[vars.eta(mode.Pi_OS2)]
    df.loc[os2bigger, 'L_ETA'] = df[vars.eta(mode.Pi_OS1)]
    df.loc[os2bigger, 'H_PHI'] = df[vars.phi(mode.Pi_OS2)]
    df.loc[os2bigger, 'L_PHI'] = df[vars.phi(mode.Pi_OS1)]

    # Correct assignment as cross-check
    valC = vec_compute_four_delta_mass(
        df[vars.pt(mode.K)], df[vars.eta(mode.K)],
        df[vars.phi(mode.K)], config.PDG_MASSES['K'],
        df[vars.pt(mode.Pi_SS)], df[vars.eta(mode.Pi_SS)],
        df[vars.phi(mode.Pi_SS)], config.PDG_MASSES['Pi'],
        df['H_PT'], df['H_ETA'],
        df['H_PHI'], config.PDG_MASSES['Pi'],
        df['L_PT'], df['L_ETA'],
        df['L_PHI'], config.PDG_MASSES['Pi'],
        df[vars.pt(mode.Pislow)], df[vars.eta(mode.Pislow)],
        df[vars.phi(mode.Pislow)], config.PDG_MASSES['Pi']
    )

    # Exchange K <-> SS Pion
    valSS = vec_compute_four_delta_mass(
        df[vars.pt(mode.K)], df[vars.eta(mode.K)],
        df[vars.phi(mode.K)], config.PDG_MASSES['Pi'],
        df[vars.pt(mode.Pi_SS)], df[vars.eta(mode.Pi_SS)],
        df[vars.phi(mode.Pi_SS)], config.PDG_MASSES['K'],
        df['H_PT'], df['H_ETA'],
        df['H_PHI'], config.PDG_MASSES['Pi'],
        df['L_PT'], df['L_ETA'],
        df['L_PHI'], config.PDG_MASSES['Pi'],
        df[vars.pt(mode.Pislow)], df[vars.eta(mode.Pislow)],
        df[vars.phi(mode.Pislow)], config.PDG_MASSES['Pi']
    )

    # Exchange K <-> OS1 Pion
    valOS1 = vec_compute_four_delta_mass(
        df[vars.pt(mode.K)], df[vars.eta(mode.K)],
        df[vars.phi(mode.K)], config.PDG_MASSES['Pi'],
        df[vars.pt(mode.Pi_SS)], df[vars.eta(mode.Pi_SS)],
        df[vars.phi(mode.Pi_SS)], config.PDG_MASSES['Pi'],
        df['H_PT'], df['H_ETA'],
        df['H_PHI'], config.PDG_MASSES['K'],
        df['L_PT'], df['L_ETA'],
        df['L_PHI'], config.PDG_MASSES['Pi'],
        df[vars.pt(mode.Pislow)], df[vars.eta(mode.Pislow)],
        df[vars.phi(mode.Pislow)], config.PDG_MASSES['Pi']
    )

    # Exchange K <-> OS2 Pion
    valOS2 = vec_compute_four_delta_mass(
        df[vars.pt(mode.K)], df[vars.eta(mode.K)],
        df[vars.phi(mode.K)], config.PDG_MASSES['Pi'],
        df[vars.pt(mode.Pi_SS)], df[vars.eta(mode.Pi_SS)],
        df[vars.phi(mode.Pi_SS)], config.PDG_MASSES['Pi'],
        df['H_PT'], df['H_ETA'],
        df['H_PHI'], config.PDG_MASSES['Pi'],
        df['L_PT'], df['L_ETA'],
        df['L_PHI'], config.PDG_MASSES['K'],
        df[vars.pt(mode.Pislow)], df[vars.eta(mode.Pislow)],
        df[vars.phi(mode.Pislow)], config.PDG_MASSES['Pi']
    )
    if not is_dummy_run(df):
        return pd.DataFrame({
            'm_SS': valSS[0],
            'dm_SS': valSS[1],
            'm_OSH': valOS1[0],
            'dm_OSH': valOS1[1],
            'm_C': valC[0],
            'dm_C': valC[1],
            'm_OSL': valOS2[0],
            'dm_OSL': valOS2[1]}, index=df.index)
    return 1


@buffer_load
@pop_arg(selective_load, allow_for=[None, 'mc'])
@call_debug
def other_slowpi(df):
    """Returns d0 mass with changed kaon and ss pion mass hypthesis"""
    mode = gcm()

    val = change_slowpi_d0(
        df[vars.dtf_pt(mode.K)], df[vars.dtf_eta(mode.K)],
        df[vars.dtf_phi(mode.K)], config.PDG_MASSES['K'],
        df[vars.dtf_pt(mode.Pi_SS)], df[vars.dtf_eta(mode.Pi_SS)],
        df[vars.dtf_phi(mode.Pi_SS)], config.PDG_MASSES['Pi'],
        df[vars.dtf_pt(mode.Pi_OS1)], df[vars.dtf_eta(mode.Pi_OS1)],
        df[vars.dtf_phi(mode.Pi_OS1)], config.PDG_MASSES['Pi'],
        df[vars.dtf_pt(mode.Pi_OS2)], df[vars.dtf_eta(mode.Pi_OS2)],
        df[vars.dtf_phi(mode.Pi_OS2)], config.PDG_MASSES['Pi'],
        df[vars.dtf_pt(mode.Pislow)], df[vars.dtf_eta(mode.Pislow)],
        df[vars.dtf_phi(mode.Pislow)], config.PDG_MASSES['Pi'],
        config.PDG_MASSES['D0']
    )
    if not is_dummy_run(df):
        return pd.Series(val, name=vars.m(gcm().D0), index=df.index)
    return 1


@buffer_load
@pop_arg(selective_load, allow_for=[None, 'mc'])
@call_debug
def other_slowpi_ws(df):
    """Returns d0 mass with changed kaon and ss pion mass hypthesis"""
    mode = gcm()

    val = change_slowpi_d0_ws(
        df[vars.dtf_pt(mode.K)], df[vars.dtf_eta(mode.K)],
        df[vars.dtf_phi(mode.K)], config.PDG_MASSES['K'],
        df[vars.dtf_pt(mode.Pi_OS1)], df[vars.dtf_eta(mode.Pi_OS1)],
        df[vars.dtf_phi(mode.Pi_OS1)], config.PDG_MASSES['Pi'],
        df[vars.dtf_pt(mode.Pi_OS2)], df[vars.dtf_eta(mode.Pi_OS2)],
        df[vars.dtf_phi(mode.Pi_OS2)], config.PDG_MASSES['Pi'],
        df[vars.dtf_pt(mode.Pi_SS)], df[vars.dtf_eta(mode.Pi_SS)],
        df[vars.dtf_phi(mode.Pi_SS)], config.PDG_MASSES['Pi'],
        df[vars.dtf_pt(mode.Pislow)], df[vars.dtf_eta(mode.Pislow)],
        df[vars.dtf_phi(mode.Pislow)], config.PDG_MASSES['Pi'],
        config.PDG_MASSES['D0']
    )
    if not is_dummy_run(df):
        return pd.Series(val, name=vars.m(gcm().D0), index=df.index)
    return 1


@selective_load
@call_debug
def _dtf_ip_diff(df):
    return df[vars.dtf_chi2(gcm().head)] - df[vars.ipchi2(gcm().D0)]


if __name__ == '__main__':
    import sys
    args = parser.create_parser()

    funcs = [
        'phsp_variables',
        '_dstp_slowpi_angle',
        'double_misid_d0',
        'double_misid',
        'other_slowpi',
        'other_slowpi_ws',
    ]
    for sel in funcs:
        remove_buffer_for_function(getattr(sys.modules[__name__], sel))
