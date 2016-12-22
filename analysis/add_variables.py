from k3pi_utilities import variables as vars
from k3pi_utilities.selective_load import selective_load
from k3pi_utilities.buffer import buffer_load
from k3pi_utilities import parser
from analysis import selection
import collections
from k3pi_utilities.debugging import call_debug
from k3pi_config.modes import gcm, MODE
from k3pi_cpp import compute_delta_angle, vec_phsp_variables
from k3pi_config import config
import pandas as pd


def append_angle(df):
    extra = _dstp_slowpi_angle()
    df[extra.name] = extra


def append_phsp(df):
    extra = phsp_variables()
    for c in extra.columns:
        df[c] = extra[c]


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
def phsp_variables(df):
    """Returns m12, m34, cos1, cos2, phi1"""
    mode = gcm()

    if not isinstance(df, collections.defaultdict):
        sel = selection.full_selection(mode)
        df = df[sel]
    vals = vec_phsp_variables(
        df[vars.dtf_pt(mode.K)], df[vars.dtf_eta(mode.K)],
        df[vars.dtf_phi(mode.K)], config.PDG_MASSES['K'],
        df[vars.dtf_pt(mode.Pi_OS1)], df[vars.dtf_eta(mode.Pi_OS1)],
        df[vars.dtf_phi(mode.Pi_OS1)], config.PDG_MASSES['Pi'],
        df[vars.dtf_pt(mode.Pi_SS)], df[vars.dtf_eta(mode.Pi_SS)],
        df[vars.dtf_phi(mode.Pi_SS)], config.PDG_MASSES['Pi'],
        df[vars.dtf_pt(mode.Pi_OS2)], df[vars.dtf_eta(mode.Pi_OS2)],
        df[vars.dtf_phi(mode.Pi_OS2)], config.PDG_MASSES['Pi'])
    if isinstance(df, collections.defaultdict):
        return 1
    return pd.DataFrame({'m12': vals[0],
                         'm34': vals[1],
                         'cos1': vals[2],
                         'cos2': vals[3],
                         'phi1': vals[4]},
                        index=df.index)


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
