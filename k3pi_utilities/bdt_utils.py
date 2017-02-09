from k3pi_utilities import helpers
from k3pi_config.modes import gcm
from k3pi_config import config, get_mode


def dump_bdt(bdt):
    outfile = gcm().get_output_path('bdt') + 'bdt.p'
    helpers.dump(bdt, outfile)


def load_bdt(mode=None):
    if mode is None:
        mode = gcm()
    outfile = mode.get_output_path('bdt') + 'bdt.p'
    return helpers.load(outfile)


def dump_classifiers(classifiers):
    outfile = gcm().get_output_path('bdt') + 'classifiers.p'
    helpers.dump(classifiers, outfile)


def load_classifiers(mode=None):
    if mode is None:
        mode = gcm()
    # Hard coded check here: Use the RS mode if WS is supplied. Also get a new
    # mode object to remove possible MC flags.
    if mode.mode == config.D0ToKpipipi_WS:
        mode = get_mode(mode.polarity, mode.year, 'RS')
    if mode.mode == config.D0ToKpipipi_2tag_WS:
        mode = get_mode(mode.polarity, mode.year, '2tag_RS')
    outfile = mode.get_output_path('bdt') + 'classifiers.p'
    return helpers.load(outfile)
