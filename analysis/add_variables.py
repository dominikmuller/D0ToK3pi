from k3pi_utilities import variables as vars
from k3pi_utilities.selective_load import selective_load
from k3pi_utilities.buffer import buffer_load
from k3pi_utilities import parser
import collections
from k3pi_utilities.debugging import call_debug
from k3pi_config.modes import gcm, MODE
from k3pi_config import get_mode
from k3pi_cpp import (compute_delta_angle, vec_phsp_variables,
                      double_misid_d0_mass, change_slowpi_d0,
                      change_slowpi_d0_ws)
from k3pi_config import config
import pandas as pd
from k3pi_utilities import bdt_utils


def append_angle(df):
    extra = _dstp_slowpi_angle()
    df[extra.name] = extra


def append_phsp(df):
    extra = phsp_variables()
    for c in extra.columns:
        df[c] = extra[c]


def append_bdt(df):
    extra = bdt_variable()
    df['bdt'] = extra


@buffer_load
@selective_load
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
    if isinstance(df, collections.defaultdict):
        return 1
    return pd.Series(ret, name='dstp_slowpi_angle', index=df.index)


@buffer_load
@selective_load
@call_debug
def bdt_variable(df):
    year = gcm().year
    polarity = gcm().polarity
    # Make sure it reads to necessary variables
    if isinstance(df, collections.defaultdict):
        [df[f.functor(f.particle)] for f in gcm().bdt_vars + gcm().spectator_vars]
        return 1.
    # For now, we always use the RS BDT, even when looking at WS
    mode = get_mode(polarity, year, 'RS')
    bdt = bdt_utils.load_classifiers(mode)['KnnFlatnessWeak']

    probs = bdt.predict_proba(df).transpose()[1]

    return pd.Series(probs, name='BDT', index=df.index)


@buffer_load
@selective_load
@call_debug
def phsp_variables(df):
    """Returns m12, m34, cos1, cos2, phi1"""
    mode = gcm()

    # implementation using pybind11::array requires some special treatment
    # here, otherwise the passed arrays are of non-matching type.
    if not isinstance(df, collections.defaultdict):
        vals = vec_phsp_variables(
            df[vars.dtf_pt(mode.K)], df[vars.dtf_eta(mode.K)],
            df[vars.dtf_phi(mode.K)], config.PDG_MASSES['K'],
            df[vars.dtf_pt(mode.Pi_OS1)], df[vars.dtf_eta(mode.Pi_OS1)],
            df[vars.dtf_phi(mode.Pi_OS1)], config.PDG_MASSES['Pi'],
            df[vars.dtf_pt(mode.Pi_SS)], df[vars.dtf_eta(mode.Pi_SS)],
            df[vars.dtf_phi(mode.Pi_SS)], config.PDG_MASSES['Pi'],
            df[vars.dtf_pt(mode.Pi_OS2)], df[vars.dtf_eta(mode.Pi_OS2)],
            df[vars.dtf_phi(mode.Pi_OS2)], config.PDG_MASSES['Pi'])
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
@selective_load
@call_debug
def double_misid_d0(df):
    """Returns d0 mass with changed kaon and ss pion mass hypthesis"""
    mode = gcm()

    val = double_misid_d0_mass(
        df[vars.pt(mode.K)], df[vars.eta(mode.K)],
        df[vars.phi(mode.K)], config.PDG_MASSES['Pi'],
        df[vars.pt(mode.Pi_SS)], df[vars.eta(mode.Pi_SS)],
        df[vars.phi(mode.Pi_SS)], config.PDG_MASSES['K'],
        df[vars.pt(mode.Pi_OS1)], df[vars.eta(mode.Pi_OS1)],
        df[vars.phi(mode.Pi_OS1)], config.PDG_MASSES['Pi'],
        df[vars.pt(mode.Pi_OS2)], df[vars.eta(mode.Pi_OS2)],
        df[vars.phi(mode.Pi_OS2)], config.PDG_MASSES['Pi'])
    if not isinstance(df, collections.defaultdict):
        return pd.Series(val, name=vars.m(gcm().D0), index=df.index)
    return 1


@buffer_load
@selective_load
@call_debug
def other_slowpi(df):
    """Returns d0 mass with changed kaon and ss pion mass hypthesis"""
    mode = gcm()

    val = change_slowpi_d0(
        df[vars.pt(mode.K)], df[vars.eta(mode.K)],
        df[vars.phi(mode.K)], config.PDG_MASSES['K'],
        df[vars.pt(mode.Pi_SS)], df[vars.eta(mode.Pi_SS)],
        df[vars.phi(mode.Pi_SS)], config.PDG_MASSES['Pi'],
        df[vars.pt(mode.Pi_OS1)], df[vars.eta(mode.Pi_OS1)],
        df[vars.phi(mode.Pi_OS1)], config.PDG_MASSES['Pi'],
        df[vars.pt(mode.Pi_OS2)], df[vars.eta(mode.Pi_OS2)],
        df[vars.phi(mode.Pi_OS2)], config.PDG_MASSES['Pi'],
        df[vars.pt(mode.Pislow)], df[vars.eta(mode.Pislow)],
        df[vars.phi(mode.Pislow)], config.PDG_MASSES['Pi'],
        config.PDG_MASSES['D0']
    )
    if not isinstance(df, collections.defaultdict):
        return pd.Series(val, name=vars.m(gcm().D0), index=df.index)
    return 1


@buffer_load
@selective_load
@call_debug
def other_slowpi_ws(df):
    """Returns d0 mass with changed kaon and ss pion mass hypthesis"""
    mode = gcm()

    val = change_slowpi_d0_ws(
        df[vars.pt(mode.K)], df[vars.eta(mode.K)],
        df[vars.phi(mode.K)], config.PDG_MASSES['K'],
        df[vars.pt(mode.Pi_OS1)], df[vars.eta(mode.Pi_OS1)],
        df[vars.phi(mode.Pi_OS1)], config.PDG_MASSES['Pi'],
        df[vars.pt(mode.Pi_OS2)], df[vars.eta(mode.Pi_OS2)],
        df[vars.phi(mode.Pi_OS2)], config.PDG_MASSES['Pi'],
        df[vars.pt(mode.Pi_SS)], df[vars.eta(mode.Pi_SS)],
        df[vars.phi(mode.Pi_SS)], config.PDG_MASSES['Pi'],
        df[vars.pt(mode.Pislow)], df[vars.eta(mode.Pislow)],
        df[vars.phi(mode.Pislow)], config.PDG_MASSES['Pi'],
        config.PDG_MASSES['D0']
    )
    if not isinstance(df, collections.defaultdict):
        return pd.Series(val, name=vars.m(gcm().D0), index=df.index)
    return 1


if __name__ == '__main__':
    import sys
    args = parser.create_parser()

    funcs = [
        'phsp_variables',
        '_dstp_slowpi_angle'
    ]

    with MODE(args.polarity, args.year, args.mode):
        for f in funcs:
            getattr(sys.modules[__name__], f)(use_buffered=False)
