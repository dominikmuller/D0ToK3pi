from k3pi_utilities import variables as vars
import seaborn as sns
import matplotlib.pyplot as plt
from k3pi_utilities import parser
from k3pi_config import config
from scipy.cluster import hierarchy
from analysis import selection, add_variables
import numpy as np

from k3pi_config import get_mode


def correlations(mode, year, polarity):
    sns.set(style="white")
    mode = get_mode(polarity, year, mode)

    functors = [(vars.pt, p) for p in mode.head.all_daughters()]
    functors += [(vars.ipchi2, p) for p in mode.head.all_daughters()]
    functors += [(vars.maxdoca, p) for p in mode.head.all_mothers()]
    functors += [(vars.probnnk, p) for p in mode.head.all_pid('K')]
    functors += [(vars.probnnpi, p) for p in mode.head.all_pid('Pi')]
    functors += [(vars.mindoca, p) for p in mode.head.all_mothers()]
    functors += [(vars.vdchi2, p) for p in mode.head.all_mothers()]
    functors += [(vars.pt, mode.D0)]
    functors += [(vars.ipchi2, mode.D0)]
    functors += [(vars.dira, mode.D0)]
    functors += [(vars.ltime, mode.D0)]
    functors += [(vars.dm, None), (vars.m, mode.D0)]

    varlist = [f(p) for f, p in functors]
    nlist = [f.latex(p) for f, p in functors]

    df = mode.get_data(varlist)
    sel = selection.pid_selection(mode)
    sel &= selection.pid_fiducial_selection(mode)
    sel &= selection.mass_fiducial_selection(mode)
    if mode.mode not in config.twotag_modes:
        sel &= selection.remove_secondary(mode)
    sel &= selection.slow_pion(mode)
    add_variables.append_angle(df, mode)
    df = df[sel]

    varlist += [vars.angle()]
    nlist += [vars.angle.latex()]

    correlations = df.corr()
    correlations_array = np.asarray(df.corr())

    row_linkage = hierarchy.linkage(correlations_array, method='average')

    from scipy.cluster.hierarchy import fcluster
    clusters = fcluster(row_linkage, 10, criterion='maxclust')
    clustered = list(
        zip(*sorted(zip(varlist, clusters), key=lambda x: x[1]))[0])
    clustered_names = list(
        zip(*sorted(zip(nlist, clusters), key=lambda x: x[1]))[0])
    correlations = correlations[clustered].loc[clustered]*100

    f, ax = plt.subplots(figsize=(15, 15))
    mask = np.zeros_like(correlations, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True

    bla = sns.heatmap(correlations, mask=mask, annot=True, ax=ax, vmin=-100,
                      square=True, vmax=100, fmt="+2.0f", linewidths=.8,
                      yticklabels=clustered_names[1:],
                      xticklabels=clustered_names[:-1], cbar=False)
    bla.set_xticklabels(bla.get_xticklabels(), rotation=90)
    bla.set_yticklabels(bla.get_yticklabels(), rotation=0)

    outfile = mode.get_output_path('sweight_fit') + 'correlations.pdf'

    bla.get_figure().savefig(outfile)

if __name__ == '__main__':
    args = parser.create_parser()
    correlations(args.mode, args.year, args.polarity)
