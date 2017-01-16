

def y_margin_scaler(ax, lf=0.1, hf=0.2):
    ax.margins(y=0.)
    mi, ma = ax.get_ylim()
    rel_lf = lf/(1-lf-hf)
    rel_hf = hf/(1-lf-hf)
    new_ma = ma + (ma - mi)*rel_hf
    new_mi = mi - (ma - mi)*rel_lf
    ax.set_ylim((new_mi, new_ma))
