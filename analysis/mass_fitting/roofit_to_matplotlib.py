import re
import numpy as np
import ROOT.RooFit as RF
import matplotlib.pyplot as plt
import logging as log
import palettable


def rooplot(ax, rc, **kwargs):
    """Plot the RooCurve on the matplotlib axis."""
    x, y = roocurve(ax, rc)
    opts = dict(fmt='-', linestyle='-', linewidth=4, color='#0000ff')
    opts.update(kwargs)

    return ax.errorbar(x, y, **opts)


def roocurve(ax, rc):
    """Plot the RooCurve on the matplotlib axis."""
    axis = rc.GetXaxis()
    xmin = axis.GetXmin()
    xmax = axis.GetXmax()
    # Walk along the curve in steps
    resolution = 1e-3
    step = (xmax - xmin)*resolution
    i = xmin
    x, y = [], []
    while i <= xmax:
        x.append(i)
        y.append(rc.interpolate(i))
        i += step

    return x, y


def double_buffer_to_list(buf, N):
    """Return a Python list from a C++ double array buffer of length N."""
    buf.SetSize(N)
    return np.array(buf, copy=True)


def tgraphasymerrors(ax, tgae, **kwargs):
    """Plot the TGraphAsymErrors on the matplotlib axis."""
    N = tgae.GetN()
    x = double_buffer_to_list(tgae.GetX(), N)
    y = double_buffer_to_list(tgae.GetY(), N)
    x_err_lo = double_buffer_to_list(tgae.GetEXlow(), N)
    x_err_hi = double_buffer_to_list(tgae.GetEXhigh(), N)
    y_err_lo = double_buffer_to_list(tgae.GetEYlow(), N)
    y_err_hi = double_buffer_to_list(tgae.GetEYhigh(), N)

    color = kwargs.get('color', '#000000')
    options = dict(
        fmt='o', markersize=5, capthick=1, capsize=0, elinewidth=2,
        color=color, markeredgecolor=color,
        # Assume that markers drawn with white should be hidden
        alpha=[1, 0][color == '#ffffff']
    )
    options.update(kwargs)

    return ax.errorbar(
        x, y,
        xerr=[x_err_lo, x_err_hi],
        yerr=[y_err_lo, y_err_hi],
        **options
    )


def pull_plot(ax, pdf, data, **kwargs):
    """Plot the error-normalised PDF-data difference on the axis."""
    N = data.GetN()
    xs = double_buffer_to_list(data.GetX(), N)
    ys = double_buffer_to_list(data.GetY(), N)
    yerrlo = double_buffer_to_list(data.GetEYlow(), N)
    yerrhi = double_buffer_to_list(data.GetEYhigh(), N)
    yerrs = (yerrlo + yerrhi)/2
    pulls = [0 if y == 0 else (pdf.interpolate(x) - y)/err
             for x, y, err in zip(xs, ys, yerrs)]
    bin_width = data.getNominalBinWidth()
    xs = xs - bin_width/2.

    opts = dict(color='#222222', edgecolor='#222222', linewidth=1)
    opts.update(kwargs)

    ax.bar(xs, pulls, width=bin_width, **opts)

    # Plot +/- 2 sigma lines. 95% of the data should be within these lines
    ax.plot([xs[0], xs[-1]+bin_width], [2, 2], color='red')
    ax.plot([xs[0], xs[-1]+bin_width], [-2, -2], color='red')
    ax.set_ylim(-5, 5)


def plot_fit(part, wsp, varfunctor, output_name='', subs=None, data=None,
             dataname='data', pdf=None):
    varname = varfunctor(part)
    var = wsp.var(varname)

    if subs is None:
        fig = plt.figure(figsize=(10, 10))
        gs = plt.GridSpec(2, 1, height_ratios=[4, 1])
        gspl = gs[0]
        gspu = gs[1]
        ax = fig.add_subplot(gspl)
        pullax = fig.add_subplot(gspu)
    else:
        ax, pullax = subs

    pdf_tot = 'total'

    frame = var.frame(RF.Bins(100))
    if data is None:
        wsp.data(dataname).plotOn(frame)
    else:
        data.plotOn(frame)
    wsp.pdf(pdf_tot).plotOn(frame)
    wsp.pdf(pdf_tot).plotOn(frame, RF.Components('signal'))
    wsp.pdf(pdf_tot).plotOn(frame, RF.Components('random'))
    wsp.pdf(pdf_tot).plotOn(frame, RF.Components('combinatorial'))

    plotobjs = [frame.getObject(i) for i in range(int(frame.numItems()))]

    pdf_tot = plotobjs[1]
    pdf_sig = plotobjs[2]
    pdf_rnd = plotobjs[3]
    pdf_comb = plotobjs[4]

    # colours = ['#333333', '#325B9D', '#269784', '#8677CF']
    colours = ['#333333'] + palettable.tableau.Tableau_10.hex_colors[:3]
    cdata, csig, crn, cbkg = colours

    # Change 'Events' to 'Candidates and remove the parens around the units
    ylabel = frame.GetYaxis().GetTitle()
    # Match the default RooFit label format to extract the unit
    _, unit = re.findall('(.*) / \( (.*) \)', ylabel)[0]
    ylabel = 'Candidates / {0}'.format(unit)
    ax.set_ylabel(ylabel)

    # Plot the PDFs
    # roocurve(ax, pdf_sig, color=csig, linestyle='--', label='Signal')
    # roocurve(ax, pdf_rn,  color=crn, linestyle='--', label='Random')
    # roocurve(ax, pdf_bkg, color=cbkg, linestyle=':', label='Background')
    # plt.plot([], [], color=cbkg, label='Background', linewidth=10)
    # plt.plot([], [], color=crn, label='Random pion', linewidth=10)
    # plt.plot([], [], color=csig, label='Signal', linewidth=10)
    xa, siga = roocurve(ax, pdf_sig)
    xa, rna = roocurve(ax, pdf_rnd)
    xa, bkga = roocurve(ax, pdf_comb)
    ax.stackplot(xa, [bkga, rna, siga], colors=[cbkg, crn, csig],
                 labels=['Comb. Bkg.', 'Rand. $\pi_s^+$', 'Signal'])
    # roocurve(ax, pdf_tot, color=csig, label='Total fit')
    # Plot the data
    datalabel = 'Data'
    tgraphasymerrors(ax, plotobjs[0], color=cdata, label=datalabel)
    ax.set_xlim((frame.GetXaxis().GetXmin(), frame.GetXaxis().GetXmax()))
    # Hide the x-axis labels and exponents
    [xtl.set_visible(False) for xtl in ax.get_xticklabels()]
    ax.get_xaxis().get_offset_text().set_visible(False)

    pull_plot(pullax, plotobjs[1], plotobjs[0])
    pullax.set_xlim((frame.GetXaxis().GetXmin(), frame.GetXaxis().GetXmax()))
    pullax.set_xlabel(varfunctor.latex(part, with_unit=True))
    pullax.set_ylabel(r'$\Delta/\sigma$')
    ax.legend()

    if pdf is not None:
        pdf.savefig(fig)
        ax.set_yscale("log", nonposy='clip')
        pdf.savefig(fig)
        plt.clf()


def check_fit_result(fit_result):
    """Check for poor fit quality using the error matrix status.
    Logs a warning and returns False for a bad fit.
    Keyword arguments:
    fit_result -- Instance of RooFitResult
    """
    # Values of the covariance matrix error status from http://cern.ch/go/6PwR
    fit_quality = fit_result.covQual()
    good_fit = True
    if fit_quality < 3:
        log.warning('{0}: {1}'.format(fit_result.GetTitle(), fit_quality))
        good_fit = False
    return good_fit
