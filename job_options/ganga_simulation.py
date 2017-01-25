from __future__ import print_function

import argparse
import getpass
import os
import pwd
import sys

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
exit = exit  # NOQA Make flake8 recognise that exit is defined

# To import we must append the current directory to our python path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), '..', 'k3pi_config'))
import config  # NOQA
from simulation_config import (  # NOQA
    modeconfig,
    years,
    tags_file,
    configs_file
)

# List of options files, with {0} substituted with the cwd
# davinci_collision.py will be dynamically created by this script
OPTIONS = [
    '{path}/add_helpers.py',
    '{path}/davinci_simulation.py',
    '{path}/configs.py',
    '{path}/tags.py'  # This defines a function called modes
]


def create_parser():
    """Build argument parser and returned parser arguments object."""
    # Set up the arguments parser
    parser = argparse.ArgumentParser(
        description='Submit jobs for ntuple creation'
    )
    parser.add_argument('-p', '--polarity', required=True,
                        choices=config.polarities,
                        help='Required: Magnet polarity of data to run over')
    parser.add_argument('-y', '--year', required=True, type=int,
                        choices=years,
                        help='Required: Year of data to run over')
    parser.add_argument('-m', '--mode', required=True,
                        choices=['RS'],
                        help='Required: Mode to run over')
    parser.add_argument('--test', action='store_true', default=False,
                        help='Run locally with a subset of the input data')
    parser.add_argument('--inspect-job', action='store_true', default=False,
                        help='Do not submit the job after creating it')
    parser.add_argument('--no-turbo', action='store_true', default=False,
                        help="Use stripping instead of the turbo stream "
                             "regardless of year")
    parser.add_argument('-t', '--twotag', action='store_true', default=False,
                        help='Create the two tag sample')

    return parser.parse_args()

args = create_parser()

if args.twotag:
    OPTIONS += ['{path}/decaytreetuples_2tag.py']
    ROOT = "'Bhadron'"
else:
    OPTIONS += ['{path}/decaytreetuples.py']
    ROOT = 'None'
JNAME = 'D0ToK3Pi_{0}_{1}_{2}_MC'


polarity = args.polarity
year = args.year
year_config = years[year]
# Need to make a special case for DpToKpipi
mode = args.mode
MODES = "['{}']".format(mode)

event_type = modeconfig[mode]['event_type']
year_config = years[year]

selected_settings = {}

for k, v in modeconfig[mode].iteritems():
    try:
        selected_settings[k] = v[year]
    except:
        selected_settings[k] = v
        pass

job_title = (
    'Creating job for MC K3Pi mixing ntuples using {0} {1} {2} data'
    .format(polarity, year, mode)
)
print('='*len(job_title))
print(job_title)
print('Event type {0}: {1}'.format(mode, event_type))
bqloc = year_config['query'].format(
    polarity=polarity, **selected_settings
)
print('BKQuery: {0}'.format(bqloc))
print('='*len(job_title))

book_keeping_query = BKQuery(bqloc)
dataset = book_keeping_query.getDataset()

print('Found {} files'.format(len(dataset.files)))

if len(dataset) is 0:
    print('Empty dataset! Quitting')
    print('Dataset path: {0}'.format(book_keeping_query.path))
    exit()

tfn = JNAME.format(polarity, year, mode) + '.root'

# Get the current user's name to build their email address
name = pwd.getpwnam(getpass.getuser()).pw_gecos.split(',')[0]
name = name.lower().split(' ')
email = '{0}.{1}@cern.ch'.format(name[0], name[-1])

base = os.getcwd()

# Make the file for setting the DB tags
with open('{0}/tags.py'.format(base), 'w+') as f:
    f.write(tags_file.format(
        dddb_tag=year_config['dddb'],
        conddb_tag=year_config['conddb']
        .format(
            'u' if polarity == 'MagUp' else 'd'
        ),
        evt_max=1000 if args.test else -1,
        printf=1 if args.test else 10000,
    ))

# Make the file for setting the access functions for ntuple settings
with open('{0}/configs.py'.format(base), 'w+') as f:
    f.write(configs_file.format(
        modes=MODES,
        turbo=(year in [2015, 2016] and not args.no_turbo),
        mc='True'
    ))

with open('{0}/davinci_simulation.py'.format(base), 'w') as f:
    input_type = modeconfig[mode]['stream'].split('.')[-1]
    f.write((
        'from helpers import davinci\n\n'
        "davinci.configure(year={1}, mc=True, input_type='{0}',"
        "n_events={2}, root={3}, tfn='{4}')\n"
    ).format(input_type, year, 10000 if args.test else -1, ROOT, tfn))

print('Created all helper files for the options.')
print('Options files:' + ' '.join([s.format(path=base, year=year) for s in OPTIONS]))  # NOQA

j = Job(name=JNAME.format(
    polarity, year, mode
))
j.comment = (
    '{1} {2} MC {0} ntuple creation for k3pi mixing measurement.'
    .format(event_type, year, polarity)
)
j.application = DaVinci(version='v41r3')
j.application.optsfile = [s.format(path=base, year=year) for s in OPTIONS]

if args.test:
    # If testing, run over a couple of files locally,
    # saving the results to the sandbox
    j.inputdata = dataset[0:1]
    j.backend = Local()
    # Prepend test string to job name
    j.name = 'TEST_{0}'.format(j.name)
    j.outputfiles = [LocalFile(tfn)]
else:
    # If not testing, run over everything on the grid, splitting jobs
    # into groups of 10 files, notifying me on job completion/subjob failure,
    # and save the results on the grid storage
    j.inputdata = dataset
    j.backend = Dirac()
    j.backend.settings['CPUTime'] = 60*60*24*7
    j.do_auto_resubmit = True
    j.splitter = SplitByFiles(filesPerJob=5, ignoremissing=True)
    j.postprocessors = [Notifier(address=email)]
    j.outputfiles = [DiracFile(tfn)]

if not args.inspect_job:
    queues.add(j.submit)  # noqa
