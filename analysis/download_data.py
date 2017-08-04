from pathos.multiprocessing import ProcessingPool
from analysis import get_root_preselection
import os
from k3pi_config import get_mode, config
from k3pi_utilities import variables, helpers, parser, get_logger
from k3pi_utilities.variables import m, dtf_m, evt_num, ipchi2, pt, ltime
from k3pi_utilities.buffer import remove_buffer_for_mode
from k3pi_cpp import treesplitter
import shutil
import bcolz
import tempfile
import tqdm
from itertools import product
import pandas as pd

log = get_logger('download_data')


def download(modename, polarity, year, full, test=False, mc=None):
    import root_pandas
    log.info('Getting data for {} {} {}'.format(
        modename, polarity, year))

    mode = get_mode(polarity, year, modename, mc)
    # I accidentally forgot the p in Dstp. Got to rename everything now for
    # this one exception. Hack incoming
    if modename == 'WS' and year == 2016:
        # As this is the start, hack name of the particle in the mode.
        mode.Dstp.name = 'Dst'

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
        'ltime_ratio': '{} / {}'.format(ltime(mode.D0), config.Dz_ltime),
        'ipchi2_1': 'ROOTex::Leading({})'.format(arg_sorted_ip),
        'ipchi2_2': 'ROOTex::SecondLeading({})'.format(arg_sorted_ip),
        'ipchi2_3': 'ROOTex::ThirdLeading({})'.format(arg_sorted_ip),
        'ipchi2_4': 'ROOTex::FourthLeading({})'.format(arg_sorted_ip),
        'pt_1': 'ROOTex::Leading({})'.format(arg_sorted_pt),
        'pt_2': 'ROOTex::SecondLeading({})'.format(arg_sorted_pt),
        'pt_3': 'ROOTex::ThirdLeading({})'.format(arg_sorted_pt),
        'pt_4': 'ROOTex::FourthLeading({})'.format(arg_sorted_pt),
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
    bcolz_folder = config.bcolz_locations.format(mode.get_store_name())

    try:
        log.info('Removing already existing data at {}'.format(
            bcolz_folder))
        shutil.rmtree(bcolz_folder)
    except OSError:
        log.info('No previous data found. Nothing to delete.')

    df_gen = root_pandas.read_root(temp_files, mode.get_tree_name(),
                                   chunksize=[500000, 100][args.test])

    # New storage using bcolz because better
    ctuple = None

    for df in df_gen:
        log.info('Adding {} events of {} to store {}.'.format(
            len(df), mode.get_tree_name(), bcolz_folder))
        if modename == 'WS' and year == 2016:
            new_names = {
                old: old.replace('Dst', 'Dstp')
                for old in df.columns if 'Dst' in old
            }
            df = df.rename(index=str, columns=new_names)
        if ctuple is None:
            ctuple = bcolz.ctable.fromdataframe(df, rootdir=bcolz_folder)
        else:
            ctuple.append(df.to_records(index=False))

    for f in temp_files:
        os.remove(f)
    # Loop and delete everything in the datastore that needs to be recached
    remove_buffer_for_mode(mode.mode)
    if modename == 'WS' and year == 2016:
        # As this is the start, hack name of the particle in the mode.
        mode.Dstp.name = 'Dstp'


if __name__ == '__main__':
    args = parser.create_parser(log)
    helpers.allow_root()

    if args.polarity == config.magboth:
        pols = [config.magup, config.magdown]
    else:
        pols = [args.polarity]
    if args.year == 1516:
        years = [2015, 2016]
    else:
        years = [args.year]
    for p, y in product(pols, years):
        download(args.mode, p, y, args.fraction, args.test, args.mc)
