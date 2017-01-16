from k3pi_utilities import helpers
from k3pi_config.modes import gcm


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
    outfile = mode.get_output_path('bdt') + 'classifiers.p'
    return helpers.load(outfile)
