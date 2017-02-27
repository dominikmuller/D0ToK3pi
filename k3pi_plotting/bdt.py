from sklearn.metrics import roc_curve, roc_auc_score
import numpy as np
import matplotlib.pyplot as plt
from rep import utils
import palettable
from k3pi_utilities import variables as vars
from k3pi_config import config
from k3pi_config.modes import gcm

from k3pi_utilities.logger import get_logger
log = get_logger('k3pi_plotting/bdt')


def roc(test, bdt, labels, weights):
    # Get the probabilities for class 1 (signal)
    probs = bdt.predict_proba(test).transpose()[1]
    x, y, _ = roc_curve(labels, probs, sample_weight=weights)
    # Make physical values so the plot looks nicer
    x[x < 0] = 0.
    x[x > 1] = 1.
    y[y < 0] = 0.
    y[y > 1] = 1.
    auc = roc_auc_score(labels, probs, sample_weight=weights)
    return x, y, auc


def plot_roc(ax, name, colour, test, bdt, labels, weights):
    x, y, auc = roc(test, bdt, labels, weights)
    legend = '{} ({:.2f})'.format(name, auc)
    ax.plot(x, y, color=colour, label=legend, linewidth=3)


def plot_roc_for_feature(ax, feature, legend, colour, test, labels, weights=1.):
    data = test[feature]
    import ipdb; ipdb.set_trace()  # XXX BREAKPOINT

    # if data[labels].median() > data[~labels]
    thresholds = [utils.weighted_quantile(
        data, quantiles=1-eff, sample_weight=weights)
        for eff in np.arange(0., 1., 1./200)]
    true_positive = []
    false_positive = []
    total_true = data[labels].sum()
    total_false = data[~labels].sum()
    # for thr in thresholds:
        # true_positive.append(np.sum(data[labels] > ))
    x, y, auc = roc(test, bdt, labels, weights)
    legend = '{} ({:.2f})'.format(name, auc)
    ax.plot(x, y, color=colour, label=legend, linewidth=3)


def plot_eff(var, part, test, bdt, labels, weights, quantiles=None):
    if quantiles is None:
        quantiles = [0.2, 0.4, 0.6, 0.8]
    varname = var(part)
    log.info('Doing efficiency for {}'.format(varname))
    colours = palettable.tableau.TableauMedium_10.hex_colors
    fig, ax = plt.subplots(figsize=(10, 10))

    probs = bdt.predict_proba(test).transpose()[1]
    thresholds = [utils.weighted_quantile(probs[labels.values], quantiles=1-eff,
                                          sample_weight=test.weights[labels])
                  for eff in quantiles]
    ret = utils.get_efficiencies(
        probs[labels.values], test[varname][labels], bins_number=15,
        sample_weight=test.weights[labels], errors=True, thresholds=thresholds)

    dt_options = dict(
        fmt='o', markersize=5, capthick=1, capsize=0, elinewidth=2)
    for r, q, c in zip(ret.items(), quantiles, colours):
        dt_options.update(dict(color=c, markeredgecolor=c))
        _, (x, y, yerr, xerr) = r
        yerr[np.isnan(yerr)] = 0.
        y, yerr = y*100., yerr*100.
        label = r'{}\%'.format(q*100)
        ax.errorbar(x, y, yerr=yerr, xerr=xerr, label=label,
                    **dt_options)
    ax.legend(loc='best')
    ax.set_xlabel(var.latex(part, with_unit=True))

    return fig


def plot_bdt_discriminant(train, test):
    fig, ax = plt.subplots(figsize=(10, 10))
    xmin, xmax = 0, 1
    nbins = 40

    # Plot train signal and background

    h_sig_train, edges = np.histogram(
        train.query('labels==1')['bdt'], bins=nbins,
        range=(xmin, xmax), weights=train.query('labels==1').weights)
    h_bkg_train, _ = np.histogram(
        train.query('labels==0')['bdt'], bins=nbins,
        range=(xmin, xmax), weights=train.query('labels==0').weights)
    h_sig_test, _ = np.histogram(
        test.query('labels==1')['bdt'], bins=nbins,
        range=(xmin, xmax), weights=test.query('labels==1').weights)
    h_bkg_test, _ = np.histogram(
        test.query('labels==0')['bdt'], bins=nbins,
        range=(xmin, xmax), weights=test.query('labels==0').weights)

    err_sig_test, _ = np.histogram(
        test.query('labels==1')['bdt'], bins=nbins,
        range=(xmin, xmax), weights=test.query('labels==1').weights**2)
    err_bkg_test, _ = np.histogram(
        test.query('labels==0')['bdt'], bins=nbins,
        range=(xmin, xmax), weights=test.query('labels==0').weights**2)

    x_ctr = (edges[1:] + edges[:-1])/2.
    width = (edges[1:] - edges[:-1])
    x_err = width/2.

    h_bkg_comb = h_bkg_train+h_bkg_test
    h_sig_comb = h_sig_train+h_sig_test
    h_bkg_comb /= np.max(h_bkg_comb)
    h_sig_comb /= np.max(h_sig_comb)

    h_bkg_train /= np.max(h_bkg_train)
    h_sig_train /= np.max(h_sig_train)

    n_sig_test = h_sig_test.max()
    n_bkg_test = h_bkg_test.max()

    err_bkg_test = np.sqrt(err_bkg_test)
    err_sig_test = np.sqrt(err_sig_test)

    h_bkg_test = h_bkg_test*1./float(n_bkg_test)
    err_bkg_test /= float(n_bkg_test)

    h_sig_test = h_sig_test*1./float(n_sig_test)
    err_sig_test /= float(n_sig_test)

    # Make a seperation here. WS modes haven't trained a BDT, so remove
    # so only plot the combined distributions
    if gcm().mode in config.wrong_sign_modes:
        ax.bar(x_ctr-x_err, h_bkg_comb, 2.*x_err,
               color='#11073B', label='Background', linewidth=0, alpha=0.50)
        ax.bar(x_ctr-x_err, h_sig_comb, 2.*x_err,
               color='#5F5293', label='Signal', linewidth=0, alpha=0.50)
    else:
        ax.bar(x_ctr, h_bkg_train, 2.*x_err,
               color='#11073B', label='Train background', linewidth=0, alpha=0.50)
        ax.bar(x_ctr, h_sig_train, 2.*x_err,
               color='#5F5293', label='Train signal', linewidth=0, alpha=0.50)

        options = dict(
            fmt='o', markersize=5, capthick=1, capsize=0, elinewidth=2,
            alpha=1)

        ax.errorbar(
            x_ctr, h_sig_test, xerr=x_err, yerr=err_sig_test,
            label='Test signal',
            color='#5F5293', markeredgecolor='#5F5293',   **options)
        ax.errorbar(
            x_ctr, h_bkg_test, xerr=x_err, yerr=err_bkg_test,
            label='Test background',
            color='#11073B', markeredgecolor='#11073B', **options)

    ax.set_ylim((0, 1.2))
    ax.legend(loc='best')
    ax.set_xlabel(vars.bdt.latex())
    return fig
