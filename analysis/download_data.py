from pathos.multiprocessing import ProcessingPool
from analysis import get_root_preselection
import os
from k3pi_config import get_mode, config
from k3pi_utilities import variables, helpers, parser, get_logger
from k3pi_utilities.variables import m, dtf_m, evt_num, ipchi2, pt
from k3pi_utilities.buffer import remove_buffer_for_mode
from k3pi_cpp import treesplitter
import root_pandas
import tempfile
import tqdm
from itertools import product
import pandas as pd

log = get_logger('download_data')


def download(mode, polarity, year, full, test=False, mc=None):
    log.info('Getting data for {} {} {}'.format(
        mode, polarity, year))
    mode = get_mode(polarity, year, mode, mc)

    sel = get_root_preselection.get(mode)

    # Always download the entire MC
    if full != 1 and mc is None:
        ctr = int(1./float(full))
        sel = '({} % {} == 0) && '.format(evt_num(), ctr) + sel
        log.info('Using ({} % {} == 0)'.format(evt_num(), ctr))

    tempfile.mktemp('.root')

    input_files = mode.get_file_list()
    if test:
        input_files = input_files[:4]
    chunked = list(helpers.chunks(input_files, 25))
    length = len(list(chunked))

    # While the code is in developement, just get any variables we can
    # access
    for part in mode.head.all_mothers() + mode.head.all_daughters():
        for func in variables.__all__:
            try:
                getattr(variables, func)(part)
            except variables.AccessorUsage:
                pass

    # Make some sorted variables. Saves the hassle when later training BDTs
    arg_sorted_ip = '{},{},{},{}'.format(
        *[ipchi2(p) for p in mode.D0.all_daughters()])
    arg_sorted_pt = '{},{},{},{}'.format(
        *[pt(p) for p in mode.D0.all_daughters()])

    add_vars = {
        'delta_m': '{} - {}'.format(m(mode.Dstp), m(mode.D0)),
        'delta_m_dtf': '{} - {}'.format(dtf_m(mode.Dstp), dtf_m(mode.D0)),
        '1ipchi2': 'ROOTex::Leading({})'.format(arg_sorted_ip),
        '2ipchi2': 'ROOTex::SecondLeading({})'.format(arg_sorted_ip),
        '3ipchi2': 'ROOTex::ThirdLeading({})'.format(arg_sorted_ip),
        '4ipchi2': 'ROOTex::FourthLeading({})'.format(arg_sorted_ip),
        '1pt': 'ROOTex::Leading({})'.format(arg_sorted_pt),
        '2pt': 'ROOTex::SecondLeading({})'.format(arg_sorted_pt),
        '3pt': 'ROOTex::ThirdLeading({})'.format(arg_sorted_pt),
        '4pt': 'ROOTex::FourthLeading({})'.format(arg_sorted_pt),
    }
    variables_needed = list(variables.all_ever_used)

    if mc == 'mc':
        variables_needed.append('Dstp_BKGCAT')

    def run_splitter(fns):
        temp_file = tempfile.mktemp('.root')
        treesplitter(files=fns, treename=mode.get_tree_name(), output=temp_file,
                     variables=variables_needed, selection=sel,
                     addvariables=add_vars)
        return temp_file

    pool = ProcessingPool(8)
    temp_files = []
    for r in tqdm.tqdm(pool.uimap(run_splitter, chunked),
                       leave=True, total=length, smoothing=0):
        temp_files.append(r)

    log.info('Created {} temporary files.'.format(len(temp_files)))

    with pd.get_store(config.data_store) as store:
        try:
            store.remove(mode.get_store_name())
            log.info('Removing already existing data at {}'.format(
                mode.get_store_name(mc)))
        except KeyError:
            log.info('No previous data found. Nothing to delete.')

    df_gen = root_pandas.read_root(temp_files, mode.get_tree_name(),
                                   chunksize=[50000, 100][args.test])
    for df in df_gen:
        log.info('Adding {} events of {} to store {}.'.format(
            len(df), mode.get_tree_name(), config.data_store))
        df.to_hdf(config.data_store, mode.get_store_name(),
                  mode='a', format='t', append=True)
    for f in temp_files:
        os.remove(f)
    # Loop and delete everything in the datastore that needs to be recached
    remove_buffer_for_mode(mode.mode)


if __name__ == '__main__':
    args = parser.create_parser(log)
    if args.polarity == config.magboth:
        pols = [config.magup, config.magdown]
    else:
        pols = [args.polarity]
    if args.year == 1516:
        years = [2015, 2016]
    else:
        years = [args.year]
    for p, y in product(pols, years):
        download(args.mode, p, y, args.full, args.test, args.mc)
