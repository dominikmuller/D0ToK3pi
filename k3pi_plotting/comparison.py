import matplotlib.pyplot as plt
import numpy as np


def plot_comparison(pc, filled, errorbars, filled_label, errorbars_label,
                    ax=None, add_uncertainties=False, normed=True,
                    filled_weight=None, errorbars_weight=None):
    """

    :pc: PlotConfig object
    :filled: data plotted in the background
    :errorbars: data plotted as errorbars
    :ax: Axis to plot on. If false a new one is created
    :add_uncertainties: Propagate unc from filled to errorbars

    :returns: ax

    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 10))
    nbins, xmin, xmax = pc.binning
    if filled_weight is None:
        filled_weight = np.ones(len(filled))
    if errorbars_weight is None:
        errorbars_weight = np.ones(len(errorbars))

    # Plot train signal and background

    h_filled, edges = np.histogram(filled, bins=nbins, range=(xmin, xmax), weights=filled_weight)
    h_errorbars, _ = np.histogram(errorbars, bins=nbins, range=(xmin, xmax), weights=errorbars_weight)
    err_filled, _ = np.histogram(filled, bins=nbins, range=(xmin, xmax), weights=filled_weight**2.)
    err_errorbars, _ = np.histogram(errorbars, bins=nbins, range=(xmin, xmax), weights=errorbars_weight**2.)

    err_filled = np.sqrt(err_filled)
    err_errorbars = np.sqrt(err_errorbars)
    if normed:
        h_filled = h_filled.astype(np.float) / (np.sum(filled_weight)*(xmax - xmin))  # NOQA
        h_errorbars = h_errorbars.astype(np.float) / (np.sum(errorbars_weight)*(xmax - xmin))  # NOQA
        err_filled = err_filled.astype(np.float) / (np.sum(filled_weight)*(xmax - xmin))  # NOQA
        err_errorbars = err_errorbars.astype(np.float) / (np.sum(errorbars_weight)*(xmax - xmin))  # NOQA

    if add_uncertainties:
        err_errorbars = np.sqrt(err_errorbars**2. + err_filled**2.)

    x_ctr = (edges[1:] + edges[:-1])/2.
    width = (edges[1:] - edges[:-1])
    x_err = width/2.

    ax.bar(x_ctr, h_filled, 2.*x_err,
           color='#5F5293', label=filled_label, linewidth=0, alpha=0.50)

    options = dict(
        fmt='o', markersize=5, capthick=1, capsize=0, elinewidth=2,
        alpha=1)

    ax.errorbar(
        x_ctr, h_errorbars, xerr=x_err, yerr=err_errorbars,
        label=errorbars_label,
        color='#5F5293', markeredgecolor='#5F5293',   **options)

    return ax
