from k3pi_utilities import parser
from k3pi_config import get_mode

from analysis.mass_fitting import fit, plot_fit

if __name__ == '__main__':
    args = parser.create_parser()
    mode = get_mode(args.polarity, args.year, args.mode)
    fit(mode)
    plot_fit(mode)
