from k3pi_config.modes import MODE, gcm, opposite_mode
from k3pi_utilities import parser, logger, PlotConfig
from analysis import final_selection, add_variables, selection
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from k3pi_utilities import variables as vars

from k3pi_plotting import comparison

log = logger.get_logger('phsp_comparison')


def phsp_comparison_plots():
    """Plots the mode sidebands and the opposite mode signal region phsp
    distributions. Only really meaningful if executed for the WS events.
    Opposite mode is plotted as solid, with the uncertainty propagated to
    the mode error plot.
    """
    # Beside phase space, also plot D0 momentum and flight distance
    extra_vars = [
        gcm().ltime_var,
        PlotConfig(vars.pt, gcm().D0, (100, 0, 15000)),
        PlotConfig(vars.vdchi2, gcm().D0, (100, 0, 10), np.log, r'$\ln(\text{{{}}})$'),  # NOQA
    ]
    # opposite_mode
    with opposite_mode():
        OS = gcm().get_data([f.var for f in extra_vars])
        add_variables.append_phsp(OS)
        os_sel = final_selection.get_final_selection()
        os_sel &= selection.delta_mass_wide_signal_region()

    # Current mode stuff
    DF = gcm().get_data([f.var for f in extra_vars])
    add_variables.append_phsp(DF)
    df_sel = final_selection.get_final_selection()
    df_sel &= selection.mass_sideband_region()

    outfile = gcm().get_output_path('selection') + 'phsp_comp.pdf'
    with PdfPages(outfile) as pdf:
        for pc in gcm().phsp_vars + extra_vars:
            log.info('Plotting {}'.format(pc.var))
            filled = OS[pc.var][os_sel]
            errorbars = DF[pc.var][df_sel]
            if pc.convert is not None:
                filled = pc.convert(filled)
                errorbars = pc.convert(errorbars)
            ax = comparison.plot_comparison(
                pc, filled, errorbars , 'RS signal', 'WS background')
            ax.set_xlabel(pc.xlabel)
            ax.yaxis.set_visible(False)
            ax.legend()
            pdf.savefig(plt.gcf())


if __name__ == '__main__':
    args = parser.create_parser()
    with MODE(args.polarity, args.year, args.mode):
        phsp_comparison_plots()
