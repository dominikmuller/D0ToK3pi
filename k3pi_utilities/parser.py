import argparse
from k3pi_config import config
import logging as log


def create_parser(logger=None):
    """Parse input arguments and return them.
    This method is responsible for checking that the input arguments are valid.
    """
    parser = argparse.ArgumentParser(description='Generate sWeights for PID')
    parser.add_argument('-f', '--full', default=0.05,
                        help='Fraction of events to download. 5% of the data')  # NOQA
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
    parser.add_argument('--sweight', default=False, action='store_true',
                        help='Use sWeights for something.')
    parser.add_argument('--train', default=False, action='store_true',
                        help='Train the BDT.')
    parser.add_argument('-s', '--selections', nargs='+', default=None,
                        help='Run the specified selections')
    parser.add_argument(
        '-v', '--verbose', action='count', default=0,
        help='Set logging level: v - WARN, vv - INFO, vvv - DEBUG'
    )

    if logger is None:
        logger = log.getLogger()
    args = parser.parse_args()
    if args.verbose == 0:
        logger.setLevel(log.WARN)
    elif args.verbose == 1:
        logger.setLevel(log.INFO)
    elif args.verbose == 2:
        logger.setLevel(log.DEBUG)
    else:
        config.devnull = None
        import ROOT
        ROOT.RooMsgService.instance().setSilentMode(False)
        ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.DEBUG)
        logger.setLevel(log.DEBUG)
    return args
