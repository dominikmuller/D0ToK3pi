from __future__ import print_function
from analysis import selection, add_variables, final_selection
import matplotlib.pyplot as plt
from k3pi_utilities import parser, helpers
from matplotlib.backends.backend_pdf import PdfPages
from itertools import permutations
from k3pi_config.modes import MODE, gcm
from analysis.model_generated import get_model
from k3pi_utilities import bdt_utils, buffer
from k3pi_utilities.helpers import dump, load

from k3pi_plotting import comparison
from k3pi_plotting import utils as plot_utils

from k3pi_utilities import logger
import numpy as np
import pandas as pd
from hep_ml.reweight import GBReweighter

log = logger.get_logger('efficiencies')


@buffer.buffer_load
def get_efficiency():
    """Returns or first trains the BDT efficiency."""
    extra_vars = [
        gcm().ltime_var
    ]
    all_vars = gcm().phsp_vars + extra_vars
    columns = [v.var for v in all_vars if 'phi' not in v.var]
    columns += ['cosphi', 'sinphi']
    log.info('Getting efficiencies for {}'.format(', '.join(columns)))

    # Current mode stuff
    data = gcm().get_data([f.var for f in extra_vars])
    add_variables.append_phsp(data)

    data['cosphi'] = np.cos(data.phi1)
    data['sinphi'] = np.sin(data.phi1)
    return compute_efficiency(data)


def get_efficiency_gen():
    """Returns or first trains the BDT efficiency."""
    extra_vars = [
        gcm().ltime_var
    ]
    all_vars = gcm().phsp_vars + extra_vars
    columns = [v.var for v in all_vars if 'phi' not in v.var]
    columns += ['cosphi', 'sinphi']
    log.info('Getting efficiencies for {}'.format(', '.join(columns)))

    # Current mode stuff
    data = get_model()
    data['cosphi'] = np.cos(data.phi1)
    data['sinphi'] = np.sin(data.phi1)
    return compute_efficiency(data)


def compute_efficiency(df):
    """Returns or first trains the BDT efficiency."""
    extra_vars = [
        gcm().ltime_var
    ]
    all_vars = gcm().phsp_vars + extra_vars
    columns = [v.var for v in all_vars if 'phi' not in v.var]
    columns += ['cosphi', 'sinphi']
    log.info('Getting efficiencies for {}'.format(', '.join(columns)))

    # Current mode stuff
    data = df.copy()
    data['cosphi'] = np.cos(data.phi1)
    data['sinphi'] = np.sin(data.phi1)
    failed_lcut = data[gcm().ltime_var.var] < 0.0001725
    failed_lcut = data[gcm().ltime_var.var] > 0.003256
    limits = {v.var: v.binning[1:] for v in all_vars}
    limits['cosphi'] = (-1., 1)
    limits['sinphi'] = (-1., 1)
    for c in columns:
        mi, ma = limits[c]
        data[c] = (data[c] - mi) / (ma - mi) + 2.

    reweighter = bdt_utils.load_reweighter()
    weight = reweighter.predict_weights(data[columns])
    weight = pd.Series(weight, index=data.index)
    weight[failed_lcut] = 0.
    weight[weight > 6.] = 6.
    return weight/6.


def train_reweighter():
    extra_vars = [
        gcm().ltime_var
    ]
    all_vars = gcm().phsp_vars + extra_vars
    columns = [v.var for v in all_vars if 'phi' not in v.var]
    columns += ['cosphi', 'sinphi']

    # Current mode stuff
    data = gcm().get_data([f.var for f in extra_vars])
    add_variables.append_phsp(data)
    data['cosphi'] = np.cos(data.phi1)
    data['sinphi'] = np.sin(data.phi1)
    df_sel = final_selection.get_final_selection()
    df_sel &= selection.delta_mass_signal_region()

    gen = get_model()
    gen['cosphi'] = np.cos(gen.phi1)
    gen['sinphi'] = np.sin(gen.phi1)

    limits = {v.var: v.binning[1:] for v in all_vars}
    limits['cosphi'] = (-1., 1)
    limits['sinphi'] = (-1., 1)
    for c in columns:
        mi, ma = limits[c]
        data[c] = (data[c] - mi) / (ma - mi) + 2.
        gen[c] = (gen[c] - mi) / (ma - mi) + 2.

    log.info('Training BDT reweighter for {}'.format(', '.join(columns)))
    reweighter = GBReweighter(n_estimators=300, max_depth=5, learning_rate=0.2)

    reweighter.fit(original=gen[columns].sample(n=250000),
                   target=data[columns][df_sel].sample(n=250000))
    bdt_utils.dump_reweighter(reweighter)


def simple_phsp_efficiencies():

    extra_vars = [
        gcm().ltime_var
    ]

    # Current mode stuff
    data = gcm().get_data([f.var for f in extra_vars])
    add_variables.append_phsp(data)
    df_sel = final_selection.get_final_selection()
    df_sel &= selection.delta_mass_signal_region()

    gen = get_model()

    outfile = gcm().get_output_path('effs') + 'Gen_DATA_Eff.pdf'
    with PdfPages(outfile) as pdf:
        for pc in gcm().phsp_vars + extra_vars:
            log.info('Plotting {}'.format(pc.var))
            denominator = gen[pc.var]
            numerator = data[pc.var][df_sel]
            weight_d = np.ones(denominator.index.size)*1./denominator.index.size  # NOQA
            weight_n = np.ones(numerator.index.size)*1./numerator.index.size
            fig, ax = plt.subplots(figsize=(10, 10))
            if pc.convert is not None:
                numerator = pc.convert(numerator)
                denominator = pc.convert(denominator)
            x, y, x_err, y_err = helpers.make_efficiency(
                numerator, denominator, 100, weight_n, weight_d, independent=True)  # NOQA
            options = dict(
                fmt='o', markersize=5, capthick=1, capsize=0, elinewidth=2,
                alpha=1)

            ax.errorbar(x, y, y_err, x_err, **options)
            ax.set_xlabel(pc.xlabel)
            ax.set_ylabel('Relative efficiency')
            pdf.savefig(plt.gcf())
            plt.close()


def dependence_study(use_efficiencies=False):

    extra_vars = [
        gcm().ltime_var
    ]
    all_vars = gcm().phsp_vars + extra_vars

    # Current mode stuff
    data = gcm().get_data([f.var for f in extra_vars])
    add_variables.append_phsp(data)
    df_sel = final_selection.get_final_selection()
    df_sel &= selection.delta_mass_signal_region()

    gen = get_model()

    if use_efficiencies:
        outfile = gcm().get_output_path('effs') + 'Gen_DATA_Eff_dep_eff.pdf'
        gen['weight'] = get_efficiency_gen()
    else:
        outfile = gcm().get_output_path('effs') + 'Gen_DATA_Eff_dep.pdf'
        gen['weight'] = 1.

    lim_file = gcm().get_output_path('effs') + 'limits_for_eff.p'
    with PdfPages(outfile) as pdf:
        for selected, plotted in permutations(all_vars, 2):
            log.info('Plotting {} in intervals of {}'.format(
                plotted.var, selected.var))
            percentiles = np.arange(0, 1.1, 0.2)
            boundaries = helpers.weighted_quantile(
                data[selected.var][df_sel], percentiles)
            fig, ax = plt.subplots(figsize=(10, 10))
            for low, high in zip(boundaries[:-1], boundaries[1:]):
                num_sel = (data[selected.var] > low) & (data[selected.var] < high)  # NOQA
                den_sel = (gen[selected.var] > low) & (gen[selected.var] < high)

                denominator = gen[plotted.var][den_sel]
                numerator = data[plotted.var][df_sel & num_sel]

                weight_d = gen['weight'][den_sel]
                weight_d /= np.sum(weight_d)
                weight_n = np.ones(numerator.index.size)*1./numerator.index.size  # NOQA

                x, y, x_err, y_err = helpers.make_efficiency(
                    numerator, denominator, 50, weight_n, weight_d, independent=True)  # NOQA
                options = dict(
                    fmt='o', markersize=5, capthick=1, capsize=0, elinewidth=2,
                    alpha=1)

                rlow, prec = helpers.rounder(low, boundaries)
                rhigh, _ = helpers.rounder(high, boundaries)

                spec = '{{:.{}f}}'.format(prec)
                label = r'${} <$ {} $ < {}$'.format(
                    spec.format(rlow), selected.xlabel, spec.format(rhigh))

                ax.errorbar(x, y, y_err, x_err, label=label, **options)
            ax.set_xlabel(plotted.xlabel)
            ax.set_ylabel('Relative efficiency')
            try:
                limits = load(lim_file)
            except:
                log.info('Creating new limits file')
                limits = {}
            if limits is None:
                log.info('Creating new limits file')
                limits = {}

            if (plotted.var, selected.var) not in limits or use_efficiencies is False:  # NOQA
                plot_utils.y_margin_scaler(ax, hf=0.4)
                limits[(plotted.var, selected.var)] = ax.get_ylim()
            else:
                log.info('Applying limits')
                lim = limits[(plotted.var, selected.var)]
                ax.set_ylim(lim)
            dump(limits, lim_file)
            ax.legend()
            pdf.savefig(plt.gcf())
            plt.close()


def lifetime_study(correct_efficiencies=False):
    # Current mode stuff
    data = gcm().get_data([gcm().ltime_var.var])
    add_variables.append_phsp(data)
    df_sel = final_selection.get_final_selection()
    df_sel &= selection.delta_mass_signal_region()
    data['weight'] = 1.

    if correct_efficiencies:
        outfile = gcm().get_output_path('effs') + 'DATA_ltime_dep_effs.pdf'
    else:
        outfile = gcm().get_output_path('effs') + 'DATA_ltime_dep.pdf'
    percentiles = np.arange(0, 1.1, 0.2)
    boundaries = helpers.weighted_quantile(
        data[gcm().ltime_var.var][df_sel], percentiles)
    if correct_efficiencies:
        data['weight'] = 1./get_efficiency()
        boundaries = boundaries[1:]
    with PdfPages(outfile) as pdf:
        for var in gcm().phsp_vars:
            fig, ax = plt.subplots(figsize=(10, 10))
            for low, high in zip(boundaries[:-1], boundaries[1:]):
                sel = (data[gcm().ltime_var.var] > low) & (data[gcm().ltime_var.var] < high)  # NOQA

                df = data[var.var][df_sel & sel]
                weight = data['weight'][df_sel & sel]

                rlow, prec = helpers.rounder(low*1000, [low*1000, high*1000])
                rhigh, _ = helpers.rounder(high*1000, [low*1000, high*1000])

                spec = '{{:.{}f}}'.format(prec)
                label = r'${} < \tau \mathrm{{ [ps]}}  < {}$'.format(
                    spec.format(rlow), spec.format(rhigh))

                values, edges = np.histogram(df, bins=int(var.binning[0]/5.), range=var.binning[1:], weights=weight)  # NOQA
                err, edges = np.histogram(df, bins=int(var.binning[0]/5.), range=var.binning[1:], weights=weight**2)  # NOQA
                norm = np.sum(values)
                values = values/norm
                err = np.sqrt(err)/norm
                x_ctr = (edges[1:] + edges[:-1])/2.
                width = (edges[1:] - edges[:-1])
                x_err = width/2.

                options = dict(
                    fmt='o', markersize=5, capthick=1, capsize=0, elinewidth=2,
                    alpha=1)

                ax.errorbar(x_ctr, values, err, x_err, label=label, **options)
            ax.set_xlabel(var.xlabel)
            ax.yaxis.set_visible(False)
            ax.legend()
            pdf.savefig(plt.gcf())
            plt.close()


def plot_comparison_test():

    extra_vars = [
        gcm().ltime_var
    ]

    # Current mode stuff
    data = gcm().get_data([f.var for f in extra_vars])
    add_variables.append_phsp(data)
    df_sel = final_selection.get_final_selection()
    df_sel &= selection.delta_mass_signal_region()

    gen = get_model()
    gen['weight'] = get_efficiency_gen()

    outfile = gcm().get_output_path('effs') + 'Gen_DATA_Comp_weights.pdf'
    with PdfPages(outfile) as pdf:
        for pc in gcm().phsp_vars + extra_vars:
            log.info('Plotting {}'.format(pc.var))
            filled = gen[pc.var]
            filled_weight = gen['weight']
            errorbars = data[pc.var][df_sel]
            if pc.convert is not None:
                filled = pc.convert(filled)
                errorbars = pc.convert(errorbars)
            ax = comparison.plot_comparison(
                pc, filled, errorbars, 'Model', 'Data',
                filled_weight=filled_weight)
            ax.set_xlabel(pc.xlabel)
            ax.yaxis.set_visible(False)
            ax.legend()
            pdf.savefig(plt.gcf())
            plt.close()


if __name__ == '__main__':
    args = parser.create_parser()
    with MODE(args.polarity, args.year, args.mode):
        if args.train:
            train_reweighter()
        buffer.remove_buffer_for_function(get_efficiency)
        # plot_comparison_test()
        # lifetime_study()
        # lifetime_study(True)
        # simple_phsp_efficiencies()
        dependence_study()
        dependence_study(True)
