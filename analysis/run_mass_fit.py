from k3pi_utilities import parser
from k3pi_config import modes

from analysis.mass_fitting import fit, plot_fit, get_sweights, fit_parameters

if __name__ == '__main__':
    args = parser.create_parser()
    with modes.MODE(args.polarity, args.year, args.mode):
        fit()
        plot_fit()
        fit_parameters()
        # Call the get sweights function to cache the sweights
        mode = modes.gcm()
        get_sweights(mode, False)
