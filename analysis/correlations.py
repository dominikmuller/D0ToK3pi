import seaborn as sns
import matplotlib.pyplot as plt
from k3pi_utilities import parser
from scipy.cluster import hierarchy
from analysis import selection, add_variables
from k3pi_config.modes import MODE, gcm
import numpy as np
from k3pi_utilities.variables import m, dtf_dm


def correlations(comb_bkg=False):
    sns.set(style="white")

    if comb_bkg:
        features_config = gcm().comb_bkg_bdt_vars
        bdt_folder = 'bdt_comb_bkg'
        bkg_sel = selection.comb_bkg_sideband_region()
    else:
        features_config = gcm().rand_spi_bdt_vars
        bdt_folder = 'bdt_rand_spi'
        bkg_sel = selection.rand_spi_sideband_region()

    functors = set()
    for pc in features_config:
        functors.add((pc.functor, pc.particle))

    functors.add((m, gcm().D0))
    functors.add((dtf_dm, None))

    varlist = [f(p) for f, p in functors]
    nlist = [f.latex(p) for f, p in functors]

    df = gcm().get_data([i for i in varlist if 'angle' not in i])

    for pc in gcm().phsp_vars:
        functors.add((pc.functor, pc.particle))
    varlist = [f(p) for f, p in functors]
    nlist = [f.latex(p) for f, p in functors]

    sel = selection.full_selection()
    add_variables.append_angle(df)
    add_variables.append_phsp(df)
    df = df[sel]
    signal_sel = selection.mass_signal_region()
    suffix = ['sig', 'bkg']
    for s, n in zip([signal_sel, bkg_sel], suffix):

        correlations = df.corr()
        correlations_array = np.asarray(df.corr())

        row_linkage = hierarchy.linkage(correlations_array, method='average')

        from scipy.cluster.hierarchy import fcluster
        clusters = fcluster(row_linkage, 10, criterion='maxclust')

        clustered = list(
            next(zip(*sorted(zip(varlist, clusters), key=lambda x: x[1]))))
        clustered_names = list(
            next(zip(*sorted(zip(nlist, clusters), key=lambda x: x[1]))))
        correlations = correlations[clustered].loc[clustered]*100

        f, ax = plt.subplots(figsize=(15, 15))
        mask = np.zeros_like(correlations, dtype=np.bool)
        mask[np.triu_indices_from(mask)] = True

        bla = sns.heatmap(correlations, mask=mask, annot=True,
                          ax=ax, vmin=-100,
                          square=True, vmax=100, fmt="+2.0f", linewidths=.8,
                          yticklabels=clustered_names[1:],
                          xticklabels=clustered_names[:-1], cbar=False)
        bla.set_xticklabels(bla.get_xticklabels(), rotation=90)
        bla.set_yticklabels(bla.get_yticklabels(), rotation=0)

        fn = 'correlations_{}.pdf'.format(n)

        outfile = gcm().get_output_path(bdt_folder) + fn

        bla.get_figure().savefig(outfile)

if __name__ == '__main__':
    args = parser.create_parser()
    with MODE(args.polarity, args.year, args.mode):
        correlations()
        correlations(True)
