from k3pi_utilities import parser
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import palettable
from sklearn.ensemble import GradientBoostingClassifier
# this wrapper makes it possible to train on subset of features
from rep.estimators import SklearnClassifier
from k3pi_plotting import bdt

from hep_ml import uboost, gradientboosting as ugb, losses  # NOQA
from k3pi_utilities import variables as vars
from k3pi_config.modes import MODE, gcm
from k3pi_utilities import bdt_utils
from analysis import bdt_data
from rep.metaml import ClassifiersFactory

from k3pi_utilities.logger import get_logger
log = get_logger('bdt_studies')


def train_bdts(sw=False):
    log.info('Training BDTs for {} {} {}'.format(gcm().mode, gcm().polarity,
                                                 gcm().year))
    (train, test, train_lbl, test_lbl), features, spectators = bdt_data.prep_data_for_sklearn(sw)  # NOQA

    uniform_features = [vars.ltime(gcm().D0)]
    n_estimators = 400

    classifiers = ClassifiersFactory()
    log.info('Configuring classifiers')

    min_samples = 2000 if sw else 1

    base_ada = GradientBoostingClassifier(
        max_depth=4, n_estimators=n_estimators, learning_rate=0.1,
        min_samples_leaf=min_samples)
    classifiers['Deviance'] = SklearnClassifier(base_ada, features=features)

    base_ada = GradientBoostingClassifier(
        max_depth=4, n_estimators=n_estimators, learning_rate=0.1,
        min_samples_leaf=min_samples, loss='exponential')
    classifiers['Exponential'] = SklearnClassifier(base_ada, features=features)

    flatnessloss = ugb.KnnFlatnessLossFunction(
        uniform_features, fl_coefficient=3., power=1.3, uniform_label=1)
    ugbFL = ugb.UGradientBoostingClassifier(
        loss=flatnessloss, max_depth=4, n_estimators=n_estimators,
        learning_rate=0.1, train_features=features, min_samples_leaf=min_samples)
    classifiers['KnnFlatnessWeak'] = SklearnClassifier(ugbFL)

    log.info('Fitting classifiers')

    classifiers.fit(
        train[features + uniform_features], train_lbl,
        sample_weight=train.weights, parallel_profile='threads-2')

    log.info('Pickling the thing')
    bdt_utils.dump_classifiers(classifiers)


def plot_roc(sw=False):
    classifiers = bdt_utils.load_classifiers()
    fig, ax = plt.subplots(figsize=(10, 10))
    colours = palettable.tableau.TableauMedium_10.hex_colors
    log.info('Plotting ROCs for {} {} {}'.format(gcm().mode, gcm().polarity,
                                                 gcm().year))
    (train, test, train_lbl, test_lbl), features, spectators = bdt_data.prep_data_for_sklearn(sw)  # NOQA
    bdt.plot_roc(ax, 'Deviance', colours[0], test, classifiers['Deviance'],
                 test_lbl, test.weights)
    bdt.plot_roc(ax, 'Exponential', colours[1], test,
                 classifiers['Exponential'], test_lbl, test.weights)
    bdt.plot_roc(ax, 'KnnFlatness', colours[2], test,
                 classifiers['KnnFlatnessWeak'], test_lbl, test.weights)

    ax.set_xlim((0, 1))
    ax.set_ylim((0, 1))
    ax.set_xlabel('False positive rate')
    ax.set_ylabel('True positive rate')
    ax.legend(loc='best')

    outfile = gcm().get_output_path('bdt') + 'ROC.pdf'

    plt.savefig(outfile)
    plt.clf()


def plot_efficiencies(sw=False):
    """Plots the efficiencies for all spectator variables. Signal contribution
    only."""
    classifiers = bdt_utils.load_classifiers()
    log.info('Plotting efficiencies for {} {} {}'.format(
        gcm().mode, gcm().polarity, gcm().year))
    (train, test, train_lbl, test_lbl), features, spectators = bdt_data.prep_data_for_sklearn(sw)  # NOQA
    outfile = gcm().get_output_path('bdt') + 'effs.pdf'
    with PdfPages(outfile) as pdf:
        for var in gcm().spectator_vars:
            for bdt_name in ['Deviance', 'Exponential',
                             'KnnFlatnessWeak']:
                fig = bdt.plot_eff(var.functor, var.particle,
                                   test, classifiers[bdt_name],
                                   test_lbl, test.weights)
                pdf.savefig(fig)
                plt.clf()


def bdt_control_plots():
    pass

if __name__ == '__main__':
    args = parser.create_parser(log)
    with MODE(args.polarity, args.year, args.mode):
        if args.train:
            train_bdts(args.sweight)
        plot_roc(args.sweight)
        plot_efficiencies(args.sweight)
