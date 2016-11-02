import argparse


def create_parser():
    """Parse input arguments and return them.
    This method is responsible for checking that the input arguments are valid.
    """
    parser = argparse.ArgumentParser(description='Generate sWeights for PID')
    parser.add_argument('-f', '--full', action='store_true', default=False,
                        help='No using the event number to only run on 5% of the data')  # NOQA
    parser.add_argument('-t', '--test', action='store_true', default=False,
                        help='Acticates testing mode')
    parser.add_argument('-m', '--mode', default='RS', choices=['RS', 'WS'],
                        help='Acticates testing mode')
    parser.add_argument('-y', '--year', default=None, choices=[2015, 2016],
                        type=int, help='Acticates testing mode')
    parser.add_argument('-p', '--polarity', default=None,
                        choices=['MagDown', 'MagUp', 'MagBoth'],
                        help='Acticates testing mode')

    return parser.parse_args()
