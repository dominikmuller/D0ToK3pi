from __future__ import print_function

import os
import pwd
import getpass
import argparse

# Don't need to import these as Ganga does it for us, but silences flake8
from Ganga.GPI import (
    BKQuery,
    DaVinci,
    Dirac,
    DiracFile,
    Job,
    Local,
    LocalFile,
    Notifier,
    SplitByFiles
)


def create_parser():
    """Build argument parser and returned parser arguments object."""
    # Set up the arguments parser
    parser = argparse.ArgumentParser(
        description='Submit jobs for ntuple creation'
    )
    parser.add_argument('-p', '--polarity', required=True,
                        help='Required: Magnet polarity of data to run over')
    parser.add_argument('-y', '--year', required=True,
                        help='Required: Year')
    parser.add_argument('--test', action='store_true', default=False,
                        help='Run locally with a subset of the input data')
    parser.add_argument('--inspect-job', action='store_true', default=False,
                        help='Do not submit the job after creating it')

    return parser.parse_args()


def stream():
    """Return the stream name for the given year and stripping version."""
    stream = 'TURBO.MDST'
    return stream


def bookkeeping_path(polarity, year):
    """Return the bookkeeping path for the given parameters."""
    bkq_path = (
        '/LHCb/Collision{year}/Beam6500GeV-VeloClosed-{polarity}/'
        'Real Data/Turbo02/RawRemoved/94000000/{stream}'
    )
    bkq = bkq_path.format(
        # Only use last two digits of the year
        year=(year - 2000),
        polarity=polarity,
        stream=stream()
    )
    print('BK path: {}'.format(bkq))
    return bkq

args = create_parser()
polarity = args.polarity
year = int(args.year)

OPTIONS = [
    '{0}/add_helpers.py',
    '{0}/davinci_collision.py',
    '{0}/decaytreetuples.py'
]

bkq = BKQuery(bookkeeping_path(polarity, year))
dataset = bkq.getDataset()

# Get the current user's name to build their email address
name = pwd.getpwnam(getpass.getuser()).pw_gecos.split(',')[0]
name = name.lower().split(' ')
email = '{0}.{1}@cern.ch'.format(name[0], name[-1])

basedir = os.getcwd()

# Make the file for configuring DaVinci
with open('{0}/davinci_collision.py'.format(basedir), 'w') as f:
    input_type = stream().split('.')[-1]
    f.write((
        'from helpers import davinci\n\n'
        "davinci.configure(year={1}, mc=False, input_type='{0}',"
        "n_events={2})\n"
    ).format(input_type, year, 25000 if args.test else -1))

j = Job(name='D0ToK3Pi_{0}_{1}'.format(polarity, year))
j.application = DaVinci(version='v40r2')
j.application.optsfile = [path.format(basedir) for path in OPTIONS]

# If testing, run over a couple of files locally, saving
# the results to the sandbox.
# Else, run over everything on the grid, splitting jobs into groups of 10
# files, notifying me on job completion/subjob failure,
# and save the results on the grid storage
if args.test:
    j.inputdata = dataset[0:1]
    j.backend = Local()
    # Prepend test string to job name
    j.name = 'TEST_{0}'.format(j.name)
    j.outputfiles = [LocalFile('DVntuple.root')]
else:
    j.inputdata = dataset
    j.backend = Dirac()
    j.do_auto_resubmit = True
    j.splitter = SplitByFiles(filesPerJob=100)
    j.postprocessors = [Notifier(address=email)]
    j.outputfiles = [DiracFile('DVntuple.root')]

if not args.inspect_job:
    queues.add(j.submit)  # noqa
