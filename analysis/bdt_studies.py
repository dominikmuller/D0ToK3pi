from __future__ import print_function
from k3pi_utilities import parser
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
from k3pi_utilities.logger import get_logger
log = get_logger('bdt_studies')


def train_bdts(sw=False):
    log.info('Training BDTs for {} {} {}'.format(gcm().mode, gcm().polarity,
                                                 gcm().year))
    (train, test, train_lbl, test_lbl), features, spectators = bdt_data.prep_data_for_sklearn(sw=sw, same_weight=True)  # NOQA

    uniform_features = [vars.ltime(gcm().D0)]
    n_estimators = 300

    classifiers = ClassifiersFactory()
    log.info('Configuring classifiers')

    min_samples = 2000 if sw else 1

    # base_ada = GradientBoostingClassifier(
    # max_depth=3, n_estimators=n_estimators, learning_rate=0.1,
    # min_samples_leaf=min_samples)
    # classifiers['Deviance'] = SklearnClassifier(base_ada, features=features)

    base_ada = GradientBoostingClassifier(
        max_depth=3, n_estimators=n_estimators, learning_rate=0.1,
        min_samples_leaf=min_samples, loss='exponential')
    classifiers['Exponential'] = SklearnClassifier(base_ada, features=features)

    # flatnessada = ugb.KnnAdaLossFunction(
    # uniform_features, uniform_label=1, knn=50)
    # ugbFL = ugb.UGradientBoostingClassifier(
    # loss=flatnessada, max_depth=3, n_estimators=n_estimators,
    # learning_rate=0.1, train_features=features,
    # min_samples_leaf=min_samples)
    # classifiers['KnnAdaFlatness'] = SklearnClassifier(ugbFL)

    flatnessloss = ugb.KnnFlatnessLossFunction(
        uniform_features, fl_coefficient=3., power=1.5, uniform_label=1,
        max_groups=10000)
    ugbFL = ugb.UGradientBoostingClassifier(
        loss=flatnessloss, max_depth=3, n_estimators=n_estimators,
        learning_rate=0.1, train_features=features,
        min_samples_leaf=min_samples)
    classifiers['KnnFlatness'] = SklearnClassifier(ugbFL)

    log.info('Fitting classifiers')

    classifiers.fit(
        train[features + uniform_features], train_lbl,
        sample_weight=train.weights, parallel_profile='threads-3')

    log.info('Pickling the thing')
    bdt_utils.dump_classifiers(classifiers)
    buffer.remove_buffer_for_function(get_bdt_discriminant)


def plot_roc(sw=False):
    classifiers = bdt_utils.load_classifiers()
    fig, ax = plt.subplots(figsize=(10, 10))
    colours = palettable.tableau.TableauMedium_10.hex_colors
    log.info('Plotting ROCs for {} {} {}'.format(gcm().mode, gcm().polarity,
                                                 gcm().year))
    (train, test, train_lbl, test_lbl), features, spectators = bdt_data.prep_data_for_sklearn(sw=sw)  # NOQA
    bdt.plot_roc(ax, 'Exponential', colours[0], test,
                 classifiers['Exponential'],
                 test_lbl, test.weights)
    # bdt.plot_roc(ax, 'KnnAdaFlatness', colours[1], test,
    # classifiers['KnnAdaFlatness'], test_lbl, test.weights)
    bdt.plot_roc(ax, 'KnnFlatness', colours[2], test,
                 classifiers['KnnFlatness'], test_lbl, test.weights)
    for i, var in enumerate(gcm().bdt_vars):
        bdt.plot_roc_for_feature(
            ax, test[var.var], var.functor.latex(var.particle),
            colours[i], test_lbl, test.weights)

    ax.set_xlim((0, 1))
    ax.set_ylim((0, 1))
    ax.set_xlabel('False positive rate')
    ax.set_ylabel('True positive rate')
    ax.legend(loc='best', fontsize=14, ncol=2)

    outfile = gcm().get_output_path('bdt') + 'ROC.pdf'

    plt.savefig(outfile)
    plt.clf()


@buffer.buffer_load
def get_bdt_discriminant():
    return get_named_bdt_discriminant()


@selective_load.selective_load
def get_named_bdt_discriminant(df, name='KnnFlatness'):
    # Trigger the loading of the needed objects
    if selective_load.is_dummy_run(df):
        [df[f.functor(f.particle)] for f in gcm().bdt_vars]
        return 1

    features = [f.functor(f.particle) for f in gcm().bdt_vars]

    classifiers = bdt_utils.load_classifiers()
    assert False not in (features == df.columns), 'Mismatching feature order'
    bdt = classifiers[name]
    probs = bdt.clf.predict_proba(df).transpose()[1]
    return pd.Series(probs, index=df.index)


def plot_bdt_discriminant(sw=False):
    train, test = bdt_data.just_the_labels(sw)  # NOQA
    outfile = gcm().get_output_path('bdt') + 'DISCRIMINANT.pdf'
    with PdfPages(outfile) as pdf:
        for bdt_name in ['Exponential', 'KnnFlatness']:
            bdt_probs = get_named_bdt_discriminant(name=bdt_name)
            train[vars.bdt()] = bdt_probs
            test[vars.bdt()] = bdt_probs
            fig = bdt.plot_bdt_discriminant(train, test)
            pdf.savefig(fig)
            plt.clf()


def create_feature_importance():
    classifiers = bdt_utils.load_classifiers()
    bdt = classifiers['KnnFlatness']
    features = [f.functor.latex(f.particle) for f in gcm().bdt_vars]
    paired = sorted(zip(features, bdt.feature_importances_),
                    key=lambda x: -x[1])
    row_template = r'{} & {:.0f}\\'

    fn = gcm().get_output_path('bdt') + 'feature_importance.tex'
    with open(fn, 'w') as of:
        print(r'\begin{tabular}{l|r}', file=of)
        print(r'Feature & Importance [\%] \\', file=of)
        print(r'\hline ', file=of)
        for f, i in paired:
            print(row_template.format(f, i*100.), file=of)
        print(r'\end{tabular}', file=of)
    tex_compile.convert_tex_to_pdf(fn)


def plot_efficiencies(sw=False):
    """Plots the efficiencies for all spectator variables. Signal contribution
    only."""
    classifiers = bdt_utils.load_classifiers()
    log.info('Plotting efficiencies for {} {} {}'.format(
        gcm().mode, gcm().polarity, gcm().year))
    (train, test, train_lbl, test_lbl), features, spectators = bdt_data.prep_data_for_sklearn(sw=sw)  # NOQA
    outfile = gcm().get_output_path('bdt') + 'effs.pdf'
    with PdfPages(outfile) as pdf:
        for var in gcm().spectator_vars:
            for bdt_name in ['Exponential', 'KnnFlatness']:
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
        plot_bdt_discriminant()
        create_feature_importance()
        plot_roc(args.sweight)
        plot_efficiencies(args.sweight)
