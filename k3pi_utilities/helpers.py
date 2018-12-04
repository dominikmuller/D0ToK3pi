from __future__ import print_function

import collections
import itertools
try:
    from itertools import izip, izip_longest
except ImportError:
    izip = zip
    izip_longest = itertools.zip_longest
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
from collections import OrderedDict

import numpy
import matplotlib.pyplot as plt
from k3pi_utilities import logger

log = logger.get_logger('helpers')

# List of prefixes for branch names
# Can't place in config due to circular dependency
numbered_branch_prefixes = ['First', 'Second', 'Third', 'Fourth', 'Fifth']


def allow_root():
    """
    Removes the ban on ROOT (if previously set)
    Returns true if successful, false otherwise

    :returns: Boolean

    """
    if 'ROOT' in sys.modules:
        if sys.modules['ROOT'] is None:
            del sys.modules['ROOT']
            log.debug('Allowed ROOT')
        else:
            log.debug('ROOT already imported')
        return True
    log.debug('ROOT not imported')
    return False


def ban_root():
    """
    Bans ROOT (if not already loaded)
    Returns true if successful, false otherwise

    :returns: Boolean

    """
    if 'ROOT' not in sys.modules:
        sys.modules['ROOT'] = None
        log.debug('Banned ROOT')
        return True
    elif sys.modules['ROOT'] is None:
        log.debug('ROOT already banned')
        return True
    log.error('ROOT already imported')
    return False


def check_fit_result(fit_result, logger=None):
    """Check for poor fit quality using the error matrix status.

    Logs a warning and returns False for a bad fit.
    Keyword arguments:
    fit_result -- Instance of RooFitResult
    """
    # Values of the covariance matrix error status from http://cern.ch/go/6PwR
    if logger is None:
        logger = log
    fit_quality = fit_result.covQual()
    good_fit = True
    if fit_quality < 2:
        logger.warning('{0}: {1}'.format(fit_result.GetTitle(), fit_quality))
        good_fit = False
    return good_fit


def quiet_mode(silence_roofit=False):
    import ROOT
    """Enables ROOT batch mode (no X windows) and sets no INFO logging."""
    # Enable batch mode -> no X windows
    ROOT.gROOT.SetBatch(True)
    # Disable INFO level logging, i.e. WARNING and up
    ROOT.gErrorIgnoreLevel = ROOT.kWarning
    # Disable INFO level RooFit logging
    ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.WARNING)
    # *Really* shut up, RooFit
    if silence_roofit:
        ROOT.RooMsgService.instance().setSilentMode(True)


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


def add_separation_page(pdf, text):
    """Small helper function to add an empty plot with text in the middle.
    Intended to be used in PdfPages multipage to describe the following plot"""
    plt.figure()
    plt.axis('off')
    plt.text(0.5, 0.5, text, ha='center', va='center')
    pdf.savefig()
    plt.close()


def check_arrays(*arrays):
    """
    Left for consistency, version of `sklearn.validation.check_arrays`
    :param list[iterable] arrays: arrays with same length of first dimension.
    """
    assert len(arrays) > 0, 'The number of array must be greater than zero'
    checked_arrays = []
    shapes = []
    for arr in arrays:
        if arr is not None:
            checked_arrays.append(numpy.array(arr))
            shapes.append(checked_arrays[-1].shape[0])
        else:
            checked_arrays.append(None)
    assert numpy.sum(numpy.array(shapes) == shapes[0]) == len(
        shapes), 'Different shapes of the arrays {}'.format(shapes)
    return checked_arrays


def check_sample_weight(y_true, sample_weight):
    """Checks the weights, if None, returns array.
    :param y_true: labels (or any array of length [n_samples])
    :param sample_weight: None or array of length [n_samples]
    :return: numpy.array of shape [n_samples]
    """
    if sample_weight is None:
        return numpy.ones(len(y_true), dtype=numpy.float)
    else:
        sample_weight = numpy.array(sample_weight, dtype=numpy.float)
        assert len(y_true) == len(sample_weight), "The length of weights is different: not {0}, but {1}".format(  # NOQA
            len(y_true), len(sample_weight))
        return sample_weight


def weighted_quantile(
        array,
        quantiles,
        sample_weight=None,
        array_sorted=False,
        old_style=False):
    """Computing quantiles of array. Unlike the numpy.percentile,
    this function supports weights,
    but it is inefficient and performs complete sorting.
    :param array: distribution, array of shape [n_samples]
    :param quantiles: floats from range [0, 1] with quantiles
        of shape [n_quantiles]
    :param sample_weight: optional weights of samples,
        array of shape [n_samples]
    :param array_sorted: if True, the sorting step will be skipped
    :param old_style: if True, will correct output
        to be consistent with numpy.percentile.
    :return: array of shape [n_quantiles]
    Example:
    >>> weighted_quantile([1, 2, 3, 4, 5], [0.5])
    Out: array([ 3.])
    >>> weighted_quantile([1, 2, 3, 4, 5], [0.5], sample_weight=[3, 1, 1, 1, 1])
    Out: array([ 2.])
    """
    array = numpy.array(array)
    quantiles = numpy.array(quantiles)
    sample_weight = check_sample_weight(array, sample_weight)
    assert numpy.all(
        quantiles >= 0) and numpy.all(
        quantiles <= 1), 'Percentiles should be in [0, 1]'

    if not array_sorted:
        array, sample_weight = reorder_by_first(array, sample_weight)

    weighted_quantiles = numpy.cumsum(sample_weight) - 0.5 * sample_weight
    if old_style:
        # To be convenient with numpy.percentile
        weighted_quantiles -= weighted_quantiles[0]
        weighted_quantiles /= weighted_quantiles[-1]
    else:
        weighted_quantiles /= numpy.sum(sample_weight)
    return numpy.interp(quantiles, weighted_quantiles, array)


def reorder_by_first(*arrays):
    """
    Applies the same permutation to all passed arrays,
    permutation sorts the first passed array
    """
    arrays = check_arrays(*arrays)
    order = numpy.argsort(arrays[0])
    return [arr[order] for arr in arrays]


class Binner(object):

    def __init__(self, values, bins_number, weights=None):
        """
        Binner is a class that helps to split the values into several bins.
        Initially an array of values is given, which is then splitted into
        'bins_number' equal parts,
        and thus we are computing limits (boundaries of bins).
        Adapted from the rep/utils.py to allow weights use weighted quantiles
        """

        if weights:
            assert len(weights) == len(values), "weights not same length"
        percentiles = [i * 1.0 / bins_number for i in range(1, bins_number)]
        self.limits = weighted_quantile(values, percentiles, weights)

    def get_bins(self, values):
        """Given the values of feature, compute the index of bin
        :param values: array of shape [n_samples]
        :return: array of shape [n_samples]
        """
        return numpy.searchsorted(self.limits, values)

    def set_limits(self, limits):
        """Change the thresholds inside bins."""
        self.limits = limits

    @property
    def bins_number(self):
        """:return: number of bins"""
        return len(self.limits) + 1

    def split_into_bins(self, *arrays):
        """
        :param arrays: data to be splitted, the first array corresponds
        :return: sequence of length [n_bins] with values corresponding to
        each bin.
        """
        values = arrays[0]
        for array in arrays:
            assert len(array) == len(
                values), "passed arrays have different length"
        bins = self.get_bins(values)
        result = []
        for bin in range(len(self.limits) + 1):
            indices = bins == bin
            result.append([numpy.array(array)[indices] for array in arrays])
        return result


def make_efficiency(numerator, denominator, bins, weight_n=None,
                    weight_d=None, independent=False):
    """Efficiency computation"""

    # First do the binning, either equal as specified by tuple
    if isinstance(bins, int):
        percentiles = [i * 1. / bins for i in range(0, bins)]
        edges = weighted_quantile(denominator, percentiles, weight_d)
    elif isinstance(bins, str):
        _, edges = numpy.histogram(denominator, bins=bins)
    else:
        bins, xmin, xmax = bins
        _, edges = numpy.histogram(denominator, bins=bins, range=(xmin, xmax))

    x_ctr = (edges[1:] + edges[:-1])/2.
    width = (edges[1:] - edges[:-1])
    x_err = width/2.

    h_num, _ = numpy.histogram(numerator, bins=edges, weights=weight_n)
    h_den, _ = numpy.histogram(denominator, bins=edges, weights=weight_d)
    h_eff = h_num / h_den
    h_num_errsq, _ = numpy.histogram(
        numerator, bins=edges, weights=weight_n**2.)
    h_den_errsq, _ = numpy.histogram(
        denominator, bins=edges, weights=weight_d**2.)
    if independent:
        h_eff_err = numpy.sqrt(h_num_errsq/h_den**2 + (h_num/h_den**2)**2*h_den_errsq)  # NOQA
    else:
        h_eff_err = numpy.abs(
            ((1. -
              2. *
              h_num /
              h_den) *
             h_num_errsq +
             h_num**2 *
             h_den_errsq /
             h_den**2) /
            h_den**2)
    mask = ~numpy.isnan(h_eff) & ~numpy.isnan(h_eff_err)

    return x_ctr[mask], h_eff[mask], x_err[mask], h_eff_err[mask]


# FIXME: copied from rep.utils
def get_efficiencies(prediction, spectator, sample_weight=None, bins_number=20,
                     thresholds=None, errors=False, ignored_sideband=0.0):
    """
    Construct efficiency function dependent on spectator for each threshold
    Different score functions available: Efficiency, Precision, Recall
    and other things from sklearn.metrics
    :param prediction: list of probabilities
    :param spectator: list of spectator's values
    :param bins_number: int, count of bins for plot
    :param thresholds: list of prediction's threshold
        (default=prediction's cuts for which efficiency
         will be [0.2, 0.4, 0.5, 0.6, 0.8])
    :return:
        if errors=False
        OrderedDict threshold -> (x_values, y_values)
        if errors=True
        OrderedDict threshold -> (x_values, y_values, y_err, x_err)
        All the parts: x_values, y_values, y_err, x_err are numpy.arrays
        of the same length.
    """
    prediction, spectator, sample_weight = \
        check_arrays(prediction, spectator, sample_weight)

    spectator_min, spectator_max = weighted_quantile(
        spectator, [ignored_sideband, (1. - ignored_sideband)])
    mask = (spectator >= spectator_min) & (spectator <= spectator_max)
    spectator = spectator[mask]
    prediction = prediction[mask]
    bins_number = min(bins_number, len(prediction))
    sample_weight = sample_weight if sample_weight is None else numpy.array(sample_weight)[mask]  # NOQA

    if thresholds is None:
        thresholds = [weighted_quantile(prediction, quantiles=1 - eff,
                                        sample_weight=sample_weight)
                      for eff in [0.2, 0.4, 0.5, 0.6, 0.8]]

    binner = Binner(spectator, bins_number=bins_number)
    if sample_weight is None:
        sample_weight = numpy.ones(len(prediction))
    bins_data = binner.split_into_bins(spectator, prediction, sample_weight)

    bin_edges = numpy.array([spectator_min] + list(binner.limits) + [spectator_max])  # NOQA
    xerr = numpy.diff(bin_edges) / 2.
    result = OrderedDict()
    for threshold in thresholds:
        x_values = []
        y_values = []
        N_in_bin = []
        for num, (masses, probabilities, weights) in enumerate(bins_data):
            y_values.append(numpy.average(probabilities > threshold,
                                          weights=weights))
            N_in_bin.append(numpy.sum(weights))
            if errors:
                x_values.append((bin_edges[num + 1] + bin_edges[num]) / 2.)
            else:
                x_values.append(numpy.mean(masses))

        x_values, y_values, N_in_bin = check_arrays(x_values, y_values,
                                                    N_in_bin)
        if errors:
            result[threshold] = (x_values, y_values, numpy.sqrt(y_values * (1 - y_values) / N_in_bin), xerr)  # NOQA
        else:
            result[threshold] = (x_values, y_values)
    return result
