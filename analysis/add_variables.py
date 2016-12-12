from k3pi_utilities import variables as vars
from k3pi_utilities.selective_load import selective_load
from k3pi_utilities.buffer import buffer_load
from k3pi_utilities.debugging import call_debug
from k3pi_cpp import compute_delta_angle
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
