from k3pi_utilities.variables import pt, eta, probnnk, probnnpi, p
from k3pi_utilities.selective_load import selective_load
from k3pi_utilities.debugging import call_debug
from k3pi_config.modes import D0ToKpipipi_RS as RS
from k3pi_config import config


@selective_load
@call_debug
def pid_selection(df):
    ret = True
    for kaon in RS.head.all_pid(config.kaon):
        ret &= (df[probnnk(kaon)] > 0.3) & (df[probnnpi(kaon)] < 0.7)
    for pion in RS.head.all_pid(config.pion):
        ret &= (df[probnnpi(pion)] > 0.3) & (df[probnnk(pion)] < 0.7)
    return ret


@selective_load
@call_debug
def pid_fiducial_selection(df):
    ret = True
    for part in RS.D0.all_daughters():
        ret &= (df[p(part)] >= 3000.)
        ret &= (df[p(part)] < 100000.)
        ret &= (df[eta(part)] >= 2.)
        ret &= (df[eta(part)] < 5.)

    return ret
