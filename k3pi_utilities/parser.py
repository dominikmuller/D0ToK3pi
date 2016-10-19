import argparse

def create_parser():
    """Parse input arguments and return them.
    This method is responsible for checking that the input arguments are valid.
    """
    parser = argparse.ArgumentParser(description='Generate sWeights for PID')
    parser.add_argument('-5', '--reduced', action='store_true', default=True,
                        help='Uses the event number to only run on 5% of the data')
    parser.add_argument('-t', '--test', action='store_true', default=False,
                        help='Acticates testing mode')

    return parser.parse_args()
