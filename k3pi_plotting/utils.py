import numpy as np


def y_margin_scaler(ax, lf=0.1, hf=0.2, la=False, ha=False, log=False):
    if la and ha:
        ax.set_ylim((lf, hf))
        return

    mi, ma = ax.yaxis.get_data_interval()

    if log:
        if la:
            new_mi = lf
        else:
            new_mi = lf * mi
        delta = np.abs(np.log10(ma)-np.log10(new_mi))/(1. - hf)
        new_ma = 10.**((np.log10(new_mi) + delta))

    elif la:
        new_mi = lf
        new_ma = lf + (ma-lf)/(1. - hf)
    elif ha:
        new_ma = hf
        new_mi = hf - (hf-mi)/(1. - lf)
    else:
        rel_hf = hf/(1-lf-hf)
        rel_lf = lf/(1-lf-hf)
        new_ma = ma + (ma - mi)*rel_hf
        new_mi = mi - (ma - mi)*rel_lf

    ax.set_ylim((new_mi, new_ma))
