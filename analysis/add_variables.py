from k3pi_utilities import variables as vars
from k3pi_utilities.selective_load import selective_load
from k3pi_utilities.buffer import buffer_load
from analysis import selection
import collections
from k3pi_utilities.debugging import call_debug
from k3pi_config.modes import gcm
from k3pi_cpp import compute_delta_angle, vec_phsp_variables
from k3pi_config import config
import pandas as pd


def append_angle(df, mode):
    extra = _dstp_slowpi_angle(mode)
    df[extra.name] = extra


@buffer_load
@selective_load
@call_debug
def _dstp_slowpi_angle(df, mode):

    ret = compute_delta_angle(
        df[vars.pt(mode.D0)], df[vars.eta(mode.D0)], df[vars.phi(mode.D0)],
        df[vars.m(mode.D0)],
        df[vars.pt(mode.Pislow)], df[vars.eta(mode.Pislow)],
        df[vars.phi(mode.Pislow)],
        config.PDG_MASSES[config.pion],
    )
    return pd.Series(ret, name='dstp_slowpi_angle')


@buffer_load
@selective_load
@call_debug
def phsp_variables(df):
    """Returns m12, m34, cos1, cos2, phi1"""
    mode = gcm()

    if type(df) != collections.defaultdict:
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
        return pd.DataFrame({'m12': vals[0],
                             'm34': vals[1],
                             'cos1': vals[2],
                             'cos2': vals[3],
                             'phi1': vals[4]})
    else:
        vals = (df[vars.dtf_pt(mode.K)], df[vars.dtf_eta(mode.K)],
                df[vars.dtf_phi(mode.K)], config.PDG_MASSES['K'],
                df[vars.dtf_pt(mode.Pi_OS1)], df[vars.dtf_eta(mode.Pi_OS1)],
                df[vars.dtf_phi(mode.Pi_OS1)], config.PDG_MASSES['Pi'],
                df[vars.dtf_pt(mode.Pi_SS)], df[vars.dtf_eta(mode.Pi_SS)],
                df[vars.dtf_phi(mode.Pi_SS)], config.PDG_MASSES['Pi'],
                df[vars.dtf_pt(mode.Pi_OS2)], df[vars.dtf_eta(mode.Pi_OS2)],
                df[vars.dtf_phi(mode.Pi_OS2)], config.PDG_MASSES['Pi'])
        return 1
