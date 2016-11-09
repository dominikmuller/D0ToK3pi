import os
import tempfile
from multiprocessing.pool import ThreadPool as Pool

def replicate(diracfile):
    diracfile.replicate('CERN-USER', diracfile.locations[0])

# After executing this script run

def make_lfn_file(output='eos_paths.py', *jobids):
    cern_user_path = 'root://eoslhcb.cern.ch//eos/lhcb/grid/user/'
    #replicate_command = '{lfn} CERN-USER {SE}\n'

    paths = []

    #replicate_jobs = ''

    #out = tempfile.mktemp()

    files_to_replicate = []
    for j in jobids:
        for sj in j.subjobs:
            if sj.status != 'completed':
                continue

            f = sj.outputfiles[0]

            if len(f.locations) == 0:
                continue

            if 'CERN-USER' not in f.locations:
                files_to_replicate.append(f)
                # f.replicate('CERN-USER', f.locations[0])

            paths.append(cern_user_path+f.lfn)

    with open(output, 'w') as f:
        f.write('paths = ' + str(paths))

    pool = Pool(20)
    pool.map(replicate, files_to_replicate)

    #with open(out, 'w') as f:
        #f.write(replicate_jobs)

    #print 'Run: cat {} | xargs --max-procs=20 -n 3 dirac-dms-replicate-lfn'.format(out)
