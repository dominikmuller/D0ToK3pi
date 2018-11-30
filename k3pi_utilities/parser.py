import argparse
from k3pi_config import config
from k3pi_utilities.logger import update_level
from k3pi_utilities.helpers import ban_root


def create_parser(logger=None):
    """Parse input arguments and return them.
    This method is responsible for checking that the input arguments are valid.
    """
    parser = argparse.ArgumentParser(description='Generate sWeights for PID')
    parser.add_argument('-f', '--fraction', default=0.05,
                        help='Fraction of events to download. 5 percent of the data')  # NOQA
    parser.add_argument('-j', '--jobs', default=1, type=int,
                        help='Number of concurrent units')  # NOQA
    parser.add_argument('-t', '--test', action='store_true', default=False,
                        help='Acticates testing mode')
    parser.add_argument('-m', '--mode', default='RS', choices=['RS', 'WS', '2tag_RS', '2tag_WS'],  # NOQA
                        help='Acticates testing mode')
    parser.add_argument('-a', '--all', action='store_true', default=False,
                        help='All modes, overrules --mode')
    parser.add_argument('-y', '--year', default=None, choices=[2015, 2016, 1516],  # NOQA
                        type=int, help='Acticates testing mode')
    parser.add_argument('-p', '--polarity', default=None,
                        choices=['MagDown', 'MagUp', 'MagBoth'],
                        help='Acticates testing mode')
    parser.add_argument('-g', '--mc', default=None, choices=[None, 'mc', 'gen'],
                        help='Can turn on MC instead of data.')
    parser.add_argument('--sweight', default=False, action='store_true',
                        help='Use sWeights for something.')
    parser.add_argument('--train', default=False, action='store_true',
                        help='Train the BDT.')
    parser.add_argument('--cbbdt', default=False, action='store_true',
                        help='Run the training and plotting for the comb. Bkg BDT')  # NOQA
    parser.add_argument('--root', default=False, action='store_true',
                        help='Allows ROOT to be imported')  # NOQA
    parser.add_argument('-s', '--selections', nargs='+', default=None,
                        help='Run the specified selections')
    parser.add_argument('--spearmint', default=False, action='store_true',
                        help='Activate something spearmint related.')
    parser.add_argument('--candidates', default=False, action='store_true',
                        help='Activate multiple candidate treatment.')
    parser.add_argument('--misid', default=False, action='store_true',
                        help='Activate misid treatment.')
    parser.add_argument('--addwrongsign', default=False, action='store_true',
                        help='BDT data will add the WS sidebands to the  data')
    parser.add_argument(
        '-v', '--verbose', action='count', default=0,
        help='Set logging level: v - WARN, vv - INFO, vvv - DEBUG'
    )

    args = parser.parse_args()
    if args.spearmint:
        config.optimised_selection = True
    if args.candidates:
        config.candidates_selection = True
    if args.misid:
        config.misid_selection = True
    if args.addwrongsign:
        config.add_wrongsign = True
    if args.verbose == 0:
        update_level(30)
    elif args.verbose == 1:
        update_level(20)
    elif args.verbose == 2:
        update_level(10)
    else:
        config.devnull = None
        update_level(10)
        if args.root:
            import ROOT
            ROOT.RooMsgService.instance().setSilentMode(False)
            ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.DEBUG)
    if args.root is False:
        ban_root()
    else:
        import ROOT
        ROOT.PyConfig.IgnoreCommandLineOptions = True
    return args
