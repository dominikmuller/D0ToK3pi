import seaborn as sns
import matplotlib.pyplot as plt
from k3pi_utilities import parser
from scipy.cluster import hierarchy
from analysis import selection, add_variables
from k3pi_config.modes import MODE, gcm
import numpy as np
from k3pi_utilities.variables import m, dtf_dm


def correlations():
    sns.set(style="white")

    functors = set()
    for pc in gcm().bdt_vars:
        functors.add((pc.functor, pc.particle))

    functors.add((m, gcm().D0))
    functors.add((dtf_dm, None))

    varlist = [f(p) for f, p in functors]
    nlist = [f.latex(p) for f, p in functors]

    df = gcm().get_data(varlist)
    sel = selection.full_selection()
    add_variables.append_angle(df)
    df = df[sel]
    add_variables.append_phsp(df)

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

    outfile = gcm().get_output_path('sweight_fit') + 'correlations.pdf'

    bla.get_figure().savefig(outfile)

if __name__ == '__main__':
    args = parser.create_parser()
    with MODE(args.polarity, args.year, args.mode):
        correlations()
