from k3pi_utilities.debugging import call_debug
from k3pi_config import config, filelists
from k3pi_config.modes.D0ToKpipipi_RS import D0ToKpipipi_RS as mode_config
from k3pi_utilities import variables as vars
from analysis import selection, add_variables, final_selection
import matplotlib.pyplot as plt
from k3pi_utilities import parser, helpers
from matplotlib.backends.backend_pdf import PdfPages
from k3pi_plotting import comparison
from k3pi_config.modes import MODE, gcm
import shutil
import bcolz

from k3pi_utilities import logger

log = logger.get_logger('model_converter')


@call_debug
def get_model(redo=False):
    files = filelists.Generated.paths

    bcolz_folder = config.bcolz_locations.format('generated_model')
    if redo:
        try:
            shutil.rmtree(bcolz_folder)
        except:
            pass
        helpers.allow_root()
        import root_pandas
        df = root_pandas.read_root(files)
        # Now rename stuff and fix units to MeV and ns.
        # Ugly hardcoded for now.
        df.rename(
            columns={'c12': vars.cos1(),
                     'c34': vars.cos2(),
                     'dtime': vars.ltime(mode_config.D0),
                     'phi': vars.phi1(),
                     'm12': vars.m12(),
                     'm34': vars.m34()},
            inplace=True)
        df[vars.m12()] = df[vars.m12()] * 1000.
        df[vars.m34()] = df[vars.m34()] * 1000.
        df[vars.ltime(mode_config.D0)] = df[vars.ltime(mode_config.D0)] / 1000.
        df = df.query('{} > 0.0001725'.format(vars.ltime(mode_config.D0)))
        bcolz.ctable.fromdataframe(df, rootdir=bcolz_folder)
        return df

    else:
        bc = bcolz.open(bcolz_folder)
        return bc.todataframe()

    return df


def plot_comparison():

    extra_vars = [
        gcm().ltime_var
    ]

    # Current mode stuff
    data = gcm().get_data([f.var for f in extra_vars])
    add_variables.append_phsp(data)
    df_sel = final_selection.get_final_selection()
    df_sel &= selection.mass_signal_region()

    gen = get_model()

    outfile = gcm().get_output_path('effs') + 'Gen_DATA_Comp.pdf'
    with PdfPages(outfile) as pdf:
        for pc in gcm().phsp_vars + extra_vars:
            log.info('Plotting {}'.format(pc.var))
            filled = gen[pc.var]
            errorbars = data[pc.var][df_sel]
            if pc.convert is not None:
                filled = pc.convert(filled)
                errorbars = pc.convert(errorbars)
            ax = comparison.plot_comparison(
                pc, filled, errorbars, 'Model', 'Data')
            ax.set_xlabel(pc.xlabel)
            ax.yaxis.set_visible(False)
            ax.legend()
            pdf.savefig(plt.gcf())


if __name__ == '__main__':
    args = parser.create_parser()
    get_model(True)
    with MODE(args.polarity, args.year, args.mode):
        plot_comparison()
