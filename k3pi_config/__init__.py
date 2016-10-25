from . import config,  modes

__all__ = [config, modes]

def get_mode(polarity, year, mode):
    return getattr(modes, 'D0ToKpipipi_' + mode)(polarity, year)
