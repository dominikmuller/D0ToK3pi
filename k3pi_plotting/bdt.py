from sklearn.metrics import roc_curve, roc_auc_score
import numpy as np
import matplotlib.pyplot as plt
from rep import utils
import palettable


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


def plot_eff(var, part, test, bdt, labels, weights, quantiles=None):
    if quantiles is None:
        quantiles = [0.2, 0.4, 0.6, 0.8]
    varname = var(part)
    colours = palettable.tableau.TableauMedium_10.hex_colors
    fig, ax = plt.subplots(figsize=(10, 10))

    probs = bdt.predict_proba(test).transpose()[1]
    thresholds = [utils.weighted_quantile(probs[labels], quantiles=1-eff,
                                          sample_weight=test.weights[labels])
                  for eff in quantiles]
    ret = utils.get_efficiencies(
        probs[labels], test[varname][labels], bins_number=15,
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
    ax.set_xlabel(var.latex(part))
    return fig
