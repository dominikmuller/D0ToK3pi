from k3pi_utilities.variables import (p, pt, ipchi2, m, dtf_chi2, ltime,
                                      vdchi2, maxdoca, mindoca, probnnk,
                                      probnnpi, probnnghost)
from k3pi_config import config


_functions = [
    'ROOTex::Leading',
    'ROOTex::SecondLeading',
    'ROOTex::ThirdLeading',
    'ROOTex::FourthLeading',
]


def build_step_cuts(var_functor, particles, cuts):
    """ROOTex commands can be used"""
    assert len(particles) == len(cuts), 'Particles and cuts not same length.'
    _temp = []
    for fnc, cut in zip(_functions[:len(cuts)], cuts):
        _temp.append('{}({}) >= {}'.format(
            fnc, ', '.join([var_functor(x) for x in particles]), cut))

    return ' && '.join(_temp)


def get(mode):
    """Get the preselection ROOT information from the mode

    :mode: TODO
    :returns: TODO

    """
    _cuts = []
    _cuts += ['fabs(' +
              m(mode.D0) +
              ' - {}) < 60.'.format(config.PDG_MASSES[config.Dz])]
    _cuts += [build_step_cuts(ipchi2, mode.D0.all_daughters(), [4, 4, 4, 4])]
    for daug in mode.head.all_daughters():
        _cuts += [p(daug) + ' >= 3000.']
        _cuts += [p(daug) + ' < 100000.']
    _cuts += [dtf_chi2(mode.head) + ' > 0.']
    _cuts += [vdchi2(mode.D0) + ' > 0.']
    _cuts += [maxdoca(mode.D0) + ' > 0.']
    _cuts += [mindoca(mode.D0) + ' > 0.']
    _cuts += [ltime(mode.D0) + ' > -10000.']
    for daug in mode.head.all_daughters():
        _cuts += [p(daug) + ' >= 3000.']
        _cuts += [p(daug) + ' < 100000.']
    for kaon in mode.head.all_pid(config.kaon):
        _cuts += [probnnk(kaon) + ' > 0.3']
        _cuts += [probnnpi(kaon) + ' < 0.7']
    for pion in mode.head.all_pid(config.pion):
        _cuts += [probnnpi(pion) + ' > 0.3']
        _cuts += [probnnk(pion) + ' < 0.7']
    for pion in mode.head.all_pid(config.slowpion):
        _cuts += [probnnghost(mode.Pislow) + ' < 0.3']
        _cuts += [probnnpi(mode.Pislow) + ' > 0.3']
        _cuts += [probnnk(mode.Pislow) + ' < 0.7']

    if mode.mode in config.twotag_modes:
        _cuts += [pt(mode.D0) + ' >= 1800.']
    else:
        _cuts += [pt(mode.D0) + ' >= 5000.']
        _cuts += ['TMath::Log(' + ipchi2(mode.D0) + ') < 2.']

    return ' && '.join(['({})'.format(x) for x in _cuts])
