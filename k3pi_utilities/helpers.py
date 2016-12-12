from __future__ import print_function

import collections
import itertools
try:
    from itertools import izip, izip_longest
except ImportError:
    izip = zip
    izip_longest = itertools.zip_longest
import logging as log
import multiprocessing
import os
from math import floor, log10
import pickle
import random
import shutil
import string
from math import ceil
import sys
from scipy.stats import gaussian_kde
from scipy.optimize import fmin

import numpy

# List of prefixes for branch names
# Can't place in config due to circular dependency
numbered_branch_prefixes = ['First', 'Second', 'Third', 'Fourth', 'Fifth']


def random_string(length=8):
    """Return a string of randomly chosen ASCII characters."""
    return ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(length)
    )


def get_mpv(thing, Npts=10000, initial=None):
    """Computes an approximated most probable value using gaussian kdes.
    thing should be something iterable, as the most common use case are
    mcerp objects, those are supported as well. The min max of thing are
    determined and scanned in Npts steps to find the maximum"""
    if hasattr(thing, '_mcpts'):
        initial = thing.percentile(0.5)
        thing = sorted(numpy.copy(thing._mcpts))
        thing = thing[20:-20]

    if not isinstance(thing, collections.Iterable):
        raise AttributeError

    if len(thing) == 0:
        return None
    # The gaussian_kde scipy.stats module doesn't like the trivial case
    # where all entries are equal
    if False not in (thing == thing[0]):
        return thing[0]
    kde = gaussian_kde(thing)
    if initial is None:
        x_min, x_max = numpy.min(thing), numpy.max(thing)
        x_set = numpy.linspace(x_min, x_max, Npts)
        y_set = kde(x_set)
        initial = x_set[numpy.argmax(y_set)]

    return fmin(lambda x: -kde(x), initial, disp=False)[0]


def progress_bar(fraction):
    """Prints a progress bar filled proportionally to fraction.

    Keyword arguments:
    fraction -- Float between 0 and 1.
    """
    width = 20
    percent = int(100*fraction)
    if percent % 5 != 0:
        return
    filled = percent/5
    sys.stdout.write("\r")
    sys.stdout.write("[{0}{1}] {2}%".format(
        "#"*int(filled),
        " "*int(width - filled),
        percent
    ))
    sys.stdout.flush()


def title(s, banner=False):
    """Print string s as a title, underlined or surrounded by hypens."""
    if banner:
        print('-'*79)
    print(s)
    if banner:
        print('-'*79)
    else:
        print('-'*len(s))


def directory_exists(path):
    """Return True if a directory exists at path."""
    return os.path.exists(path)


def ensure_directory_exists(path):
    """Create directory structure matching path if it doesn't already exist."""
    if not directory_exists(path):
        log.info('Creating directory structure {0}'.format(path))
        os.makedirs(path)


def recursive_dict_init(keys_list, d=None, previous_keys=None):
    """Recursively initialises d with keys from keys_list"""
    if d is None:
        d = dict()
    if previous_keys is None:
        previous_keys = []
    keys = keys_list.pop(0)
    current_dict = d
    for key in previous_keys:
        current_dict = current_dict[key]
    for key in keys:
        current_dict[key] = dict()
        if keys_list:
            recursive_dict_init(keys_list[:], d, previous_keys + [key])
    return d


def uniform_binning(begin, end, step):
    """Return a list of bin edges from begin to end, in increments of step.

    Steps may be non-integer and, unlike the range builtin, the end is included
    in the returned list.
    """
    return list(numpy.arange(begin, end + step, step))


def make_cut_string(mode, cuts, no_pid=False, cut_string='1'):
    """ Makes a TTreeFormula cut string from cuts """
    def add_cut(var_name, var_min, var_max, cut_string):
        if var_min is not None:
            cut_string += ' && {0} > {1}'.format(var_name, var_min)
        if var_max is not None:
            cut_string += ' && {0} < {1}'.format(var_name, var_max)
        return cut_string

    for var_name, var_min, var_max in cuts:
        skip = False
        for banned in ('_PID', '_ProbNN'):
            if banned in var_name:
                skip = True
        if no_pid and skip:
            continue

        if '{m}' in var_name:
            for mother_name in mode.mother_prefixes:
                cut_string = add_cut(var_name.format(m=mother_name), var_min,
                                     var_max, cut_string)
        elif '{d}' in var_name:
            for daughter_name in mode.daughter_prefixes:
                cut_string = add_cut(var_name.format(d=daughter_name), var_min,
                                     var_max, cut_string)
        else:
            cut_string = add_cut(var_name, var_min, var_max, cut_string)
    return cut_string


def move_file(src, dst):
    if os.path.exists(dst):
        if os.path.isdir(dst):
            new_name = os.path.join(dst, os.path.basename(src))
            if os.path.exists(new_name):
                os.remove(new_name)
        else:
            os.remove(dst)
    shutil.move(src, dst)


def cpu_count():
    """Return the number of cores available on the host machine.

    Uses multiprocessing.cpu_count, falling back to default value of 2 if that
    fails. 2 is used because it is likely that any processor this code will
    run on will have either 2 physical or 2 logical/virtual cores.
    """
    ncpu = 2
    try:
        ncpu = multiprocessing.cpu_count()
    except NotImplementedError:
        log.warning((
            'Could not find ncpu with multiprocessing.cpu_count, '
            'reverting to default value of {0}'
        ).format(ncpu))
    return ncpu


def dump(obj, filename):
    """Uses pickle to save an obj to filename."""
    log.debug('Dumping pickle file: {0}'.format(filename))
    # We need to specify the protocol to maintain Python 2 support
    with open(filename, 'wb') as f:
        pickle.dump(obj, f, protocol=2)


def load(filename):
    """Uses pickle to load the object stored in filename."""
    log.debug('Loading pickle file: {0}'.format(filename))
    # Python 3 needs the encoding specifying to open pickles from Python 2
    if os.access(filename, os.F_OK) is False:
        log.error('Could not unpickle {0}, does not exist!'.format(filename))
        return None
    with open(filename, 'rb') as f:
        if sys.version_info < (3, 0):
            return pickle.load(f)
        else:
            return pickle.load(f, encoding='latin1')


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return izip(a, b)


def chunks(l, n):
    """Yield n successive chunks from l."""
    N = int(ceil(len(l)/float(n)))
    for i in range(0, len(l), N):
        yield l[i:i + N]


def variables_from_formulae(formulae, modifiers=None):
    """Crudely parse variable names from a list of formulae containing variables.

    The input formulae is mutated to contain only variables.
    Keyword arguments:
    formulae -- List of strings to parse
    modifers -- List of symbols to consider as operations (default:
        ['+', '-', '/', '*'])
    """
    if modifiers is None:
        modifiers = ['+', '-', '/', '*']

    for modifier in modifiers:
        for formula in formulae[:]:
            if modifier in formula:
                del formulae[formulae.index(formula)]
                formulae.extend(formula.split(modifier))

    return list(set(formulae))


class buffer_return():
    def __init__(self, function):
        self._return = None
        self._func = function

    def __call__(self, *args, **kwargs):
        if self._return is None:
            self._return = self._func(*args, **kwargs)
        return self._return


class suppress_stdout_stderr(object):

    '''
    A context manager for doing a "deep suppression" of stdout and stderr in
    Python, i.e. will suppress all print, even if the print originates in a
    compiled C/Fortran sub-function.
    This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).
    '''

    def __init__(self):
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = (os.dup(1), os.dup(2))

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        # Close the null files
        os.close(self.null_fds[0])
        os.close(self.null_fds[1])


def rounder(num, l_for_sig_dgt, is_unc=False, sig_prec=1):
    l_for_sig_dgt = [x for x in l_for_sig_dgt if x != 0]
    if len(l_for_sig_dgt) == 0:
        return num, 0
    most_precise = min(map(abs, l_for_sig_dgt))
    dec_pos = [int(floor(log10(abs(x)))) for x in l_for_sig_dgt]
    sig_digit = int(floor(log10(abs(most_precise))))
    # normed_val = most_precise*10**(-sig_digit)
    # if 1.00 <= normed_val < 3.45:
    # sig_digit -= 1
    # elif normed_val >= 9.50:
    # sig_digit -= 1
    # if is_unc:
    # num += sign(num)*0.5*10**sig_digit
    if False not in [d == min(dec_pos) for d in dec_pos]:
        sig_digit -= sig_prec
    prec = [0, -sig_digit][sig_digit < 0]
    return round(num, -sig_digit), prec


