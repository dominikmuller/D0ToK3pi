from k3pi_utilities.variables import pt, eta, probnnk, probnnpi
from k3pi_utilities.selective_load import selective_load
from k3pi_utilities.debugging import call_debug
from k3pi_config import right_sign as RS
from k3pi_config import config
import numpy as np


@selective_load
@call_debug
def pid_selection(df):
    ret = True
    for kaon in RS.Dst.all_pid(config.kaon):
        ret &= (df[probnnk(kaon)] > 0.3) & (df[probnnpi(kaon)] < 0.7)
    for pion in RS.Dst.all_pid(config.pion):
        ret &= (df[probnnpi(pion)] > 0.3) & (df[probnnk(pion)] < 0.7)
    return ret


@selective_load
@call_debug
def pid_fiducial_selection(df):
    ret = True
    for part in RS.D0.all_daughters():
        ret &= (df[pt(part)] * np.cosh(df[eta(part)]) >= 3000.)
        ret &= (df[pt(part)] * np.cosh(df[eta(part)]) < 100000.)
        ret &= (np.cosh(df[eta(part)]) >= 2.)
        ret &= (np.cosh(df[eta(part)]) < 5.)

    return ret
