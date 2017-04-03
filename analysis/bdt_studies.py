from __future__ import print_function
from k3pi_utilities import parser
from analysis import add_variables
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import palettable
from sklearn.ensemble import GradientBoostingClassifier
# this wrapper makes it possible to train on subset of features
from rep.estimators import SklearnClassifier
from k3pi_plotting import bdt
from k3pi_utilities import buffer, selective_load

from hep_ml import uboost, gradientboosting as ugb, losses  # NOQA
from k3pi_utilities import variables as vars
from k3pi_config.modes import MODE, gcm
from k3pi_utilities import bdt_utils
from analysis import bdt_data
from rep.metaml import ClassifiersFactory

from k3pi_utilities import tex_compile

# Because this stuff all lots of memory and I am too lazy to properly make
# sure all functions correctly delete their stuff.
from k3pi_utilities.processify import processify
from k3pi_utilities.logger import get_logger
log = get_logger('bdt_studies')


@processify
def train_bdts(sw=False, comb_bkg=False):
    log.info('Training BDTs for {} {} {}'.format(gcm().mode, gcm().polarity,
                                                 gcm().year))
    (train, test, train_lbl, test_lbl), features, spectators = bdt_data.prep_data_for_sklearn(sw=sw, same_weight=True, comb_data=comb_bkg)  # NOQA

    uniform_features = [vars.ltime(gcm().D0)]
    n_estimators = 200

    classifiers = ClassifiersFactory()
    log.info('Configuring classifiers')

    min_samples = 2000 if sw else 10
    if comb_bkg:
        lrate = 0.1
    else:
        lrate = 0.1

    base_ada = GradientBoostingClassifier(
        max_depth=3, n_estimators=n_estimators, learning_rate=lrate,
        min_samples_leaf=min_samples, loss='exponential')
    classifiers['Exponential'] = SklearnClassifier(base_ada, features=features)

    flatnessloss = ugb.KnnFlatnessLossFunction(
        uniform_features, fl_coefficient=3., power=1.3, uniform_label=1,
        max_groups=2000, n_neighbours=300)
    ugbFL = ugb.UGradientBoostingClassifier(
        loss=flatnessloss, max_depth=3, n_estimators=n_estimators,
        learning_rate=lrate, train_features=features,
        min_samples_leaf=min_samples)
    classifiers['KnnFlatness'] = SklearnClassifier(ugbFL)

    binflatnessloss = ugb.BinFlatnessLossFunction(
        uniform_features, fl_coefficient=3., power=2.0, uniform_label=1,
        n_bins=15)
    ugbBFL = ugb.UGradientBoostingClassifier(
        loss=binflatnessloss, max_depth=3, n_estimators=n_estimators,
        learning_rate=lrate, train_features=features,
        min_samples_leaf=min_samples)
    classifiers['BinFlatness'] = SklearnClassifier(ugbBFL)

    log.info('Fitting classifiers')

    classifiers.fit(
        train[features + uniform_features], train_lbl,
        sample_weight=train.weights, parallel_profile='threads-3')

    log.info('Pickling the thing')
    bdt_utils.dump_classifiers(classifiers, comb_bkg=comb_bkg)
    buffer.remove_buffer_for_function(get_bdt_discriminant)


@processify
def plot_roc(sw=False, comb_bkg=False):
    classifiers = bdt_utils.load_classifiers(comb_bkg=comb_bkg)
    fig, ax = plt.subplots(figsize=(10, 10))
    colours = palettable.tableau.TableauMedium_10.hex_colors

    if comb_bkg:
        features_config = gcm().comb_bkg_bdt_vars
        bdt_folder = 'bdt_comb_bkg'
    else:
        features_config = gcm().rand_spi_bdt_vars
        bdt_folder = 'bdt_rand_spi'

    log.info('Plotting ROC for  {}'.format(
        'comb. bkg' if comb_bkg else 'rand. pion bkg.'))

    log.info('Plotting ROCs for {} {} {} {}'.format(
        bdt_folder, gcm().mode, gcm().polarity, gcm().year))

    log.info('Features: {}'.format(' '.join(
        [f.functor(f.particle) for f in features_config])))

    (train, test, train_lbl, test_lbl), features, spectators = bdt_data.prep_data_for_sklearn(sw=sw, comb_data=comb_bkg)  # NOQA
    bdt.plot_roc(ax, 'Exponential', colours[0], test,
                 classifiers['Exponential'],
                 test_lbl, test.weights)
    # bdt.plot_roc(ax, 'KnnAdaFlatness', colours[1], test,
    # classifiers['KnnAdaFlatness'], test_lbl, test.weights)
    bdt.plot_roc(ax, 'KnnFlatness', colours[1], test,
                 classifiers['KnnFlatness'], test_lbl, test.weights)

    bdt.plot_roc(ax, 'BinFlatness', colours[2], test,
                 classifiers['BinFlatness'], test_lbl, test.weights)
    for i, var in enumerate(features_config):
        bdt.plot_roc_for_feature(
            ax, test[var.var], var.functor.latex(var.particle),
            colours[i], test_lbl, test.weights)

    ax.set_xlim((0, 1))
    ax.set_ylim((0, 1))
    ax.set_xlabel('False positive rate')
    ax.set_ylabel('True positive rate')
    ax.legend(loc='best', fontsize=14, ncol=2)

    outfile = gcm().get_output_path(bdt_folder) + 'ROC.pdf'

    plt.savefig(outfile)
    plt.clf()


@buffer.buffer_load
def get_bdt_discriminant():
    spi_bdt = get_named_bdt_discriminant()
    bkg_bdt = get_named_bdt_discriminant(comb_bkg=True)

    return pd.DataFrame({
        'rand_spi_bdt': spi_bdt,
        'comb_bkg_bdt': bkg_bdt
    })


@selective_load.selective_load
def get_named_bdt_discriminant(df, name='KnnFlatness', comb_bkg=False):
    # Trigger the loading of the needed objects
    if selective_load.is_dummy_run(df):
        [df[f.functor(f.particle)] for f in gcm().bdt_vars if f.functor != vars.angle]  # NOQA
        return 1

    log.info('Getting discriminant {} for {}'.format(
        name, 'comb. bkg' if comb_bkg else 'rand. pion bkg.'))

    if comb_bkg:
        features = [f.functor(f.particle) for f in gcm().comb_bkg_bdt_vars]
        bdt_vars = gcm().comb_bkg_bdt_vars
    else:
        features = [f.functor(f.particle) for f in gcm().rand_spi_bdt_vars]
        bdt_vars = gcm().rand_spi_bdt_vars

    log.info('Features: {}'.format(' '.join(features)))

    if vars.angle() in features:
        log.info('Adding angle.')
        add_variables.append_angle(df)

    for f in bdt_vars:
        if f.convert is not None:
            log.info('Converting {}'.format(f.var))
            df[f.var] = f.convert(df[f.var])

    df = df[features]

    classifiers = bdt_utils.load_classifiers(comb_bkg=comb_bkg)
    assert False not in (features == df.columns), 'Mismatching feature order'
    bdt = classifiers[name]
    probs = bdt.clf.predict_proba(df).transpose()[1]
    log.info('Returning probability.')
    return pd.Series(probs, index=df.index)


@processify
def plot_bdt_discriminant(sw=False, comb_bkg=False):
    log.info('Plotting discriminant for {}'.format(
        'comb. bkg' if comb_bkg else 'rand. pion bkg.'))
    train, test = bdt_data.just_the_labels(sw, comb_data=comb_bkg)  # NOQA
    if comb_bkg:
        bdt_folder = 'bdt_comb_bkg'
    else:
        bdt_folder = 'bdt_rand_spi'
    outfile = gcm().get_output_path(bdt_folder) + 'DISCRIMINANT.pdf'
    log.info('Saving to {}'.format(outfile))
    with PdfPages(outfile) as pdf:
        for bdt_name in ['Exponential', 'KnnFlatness', 'BinFlatness']:
            bdt_probs = get_named_bdt_discriminant(name=bdt_name,
                                                   comb_bkg=comb_bkg)
            train[vars.bdt()] = bdt_probs
            test[vars.bdt()] = bdt_probs
            fig = bdt.plot_bdt_discriminant(train, test)
            pdf.savefig(fig)
            plt.clf()


@processify
def create_feature_importance(comb_bkg=False):
    log.info('Feature importance for {}'.format(
        'comb. bkg' if comb_bkg else 'rand. pion bkg.'))
    classifiers = bdt_utils.load_classifiers(comb_bkg)
    bdt = classifiers['KnnFlatness']
    if comb_bkg:
        features = [f.functor.latex(f.particle) for f in gcm().comb_bkg_bdt_vars]
        bdt_folder = 'bdt_comb_bkg'
    else:
        features = [f.functor.latex(f.particle) for f in gcm().rand_spi_bdt_vars]
        bdt_folder = 'bdt_rand_spi'

    log.info('Features: {}'.format(' '.join(features)))

    paired = sorted(zip(features, bdt.feature_importances_),
                    key=lambda x: -x[1])
    row_template = r'{} & {:.0f}\\'

    fn = gcm().get_output_path(bdt_folder) + 'feature_importance.tex'
    log.info('Saving to {}'.format(fn))
    with open(fn, 'w') as of:
        print(r'\begin{tabular}{l|r}', file=of)
        print(r'Feature & Importance [\%] \\', file=of)
        print(r'\hline ', file=of)
        for f, i in paired:
            print(row_template.format(f, i*100.), file=of)
        print(r'\end{tabular}', file=of)
    tex_compile.convert_tex_to_pdf(fn)


@processify
def plot_efficiencies(sw=False, comb_bkg=False):
    """Plots the efficiencies for all spectator variables. Signal contribution
    only."""
    if comb_bkg:
        bdt_folder = 'bdt_comb_bkg'
    else:
        bdt_folder = 'bdt_rand_spi'
    classifiers = bdt_utils.load_classifiers(comb_bkg=comb_bkg)
    log.info('Plotting efficiencies for {} {} {}'.format(
        gcm().mode, gcm().polarity, gcm().year))
    (train, test, train_lbl, test_lbl), features, spectators = bdt_data.prep_data_for_sklearn(sw=sw, comb_data=comb_bkg)  # NOQA
    outfile = gcm().get_output_path(bdt_folder) + 'effs.pdf'
    with PdfPages(outfile) as pdf:
        for var in gcm().spectator_vars:
            for bdt_name in ['Exponential', 'KnnFlatness', 'BinFlatness']:
                fig = bdt.plot_eff(var.functor, var.particle,
                                   test, classifiers[bdt_name],
                                   test_lbl, test.weights)
                pdf.savefig(fig)
                plt.clf()
                fig = bdt.plot_eff(var.functor, var.particle,
                                   test, classifiers[bdt_name],
                                   ~test_lbl, test.weights)
                pdf.savefig(fig)
                plt.clf()


def bdt_control_plots():
    pass

if __name__ == '__main__':
    args = parser.create_parser(log)
    with MODE(args.polarity, args.year, args.mode, args.mc):
        if args.train:
            train_bdts(args.sweight)
            train_bdts(args.sweight, comb_bkg=True)
        plot_bdt_discriminant()
        plot_bdt_discriminant(comb_bkg=True)
        create_feature_importance()
        create_feature_importance(comb_bkg=True)
        plot_roc(args.sweight)
        plot_roc(args.sweight, comb_bkg=True)
        plot_efficiencies(args.sweight)
        plot_efficiencies(args.sweight, comb_bkg=True)
