from k3pi_config.modes.D0ToKpipipi_RS import D0ToKpipipi_RS
from k3pi_config.modes.D0ToKpipipi_WS import D0ToKpipipi_WS
from k3pi_config.modes.D0ToKpipipi_2tag_RS import D0ToKpipipi_2tag_RS
from k3pi_config.modes.D0ToKpipipi_2tag_WS import D0ToKpipipi_2tag_WS
from k3pi_config.modes.mode_base import ModeConfig
import sys
from contextlib import contextmanager

_current_mode = None
_previous_modes = []
_thismodule = sys.modules[__name__]


@contextmanager
def MODE(polarity, year, mode, mc=None):
    global _current_mode
    global _previous_modes
    if not hasattr(_thismodule, 'D0ToKpipipi_' + mode):
        raise ModeConfig('No mode {} -> {}'.format(
            mode, 'D0ToKpipipi_' + mode))
    if _current_mode is not None:
        _previous_modes.append(_current_mode)
    _current_mode = getattr(
        _thismodule, 'D0ToKpipipi_' + mode)(polarity, year, mc)
    yield _current_mode
    try:
        _current_mode = _previous_modes.pop()
    except IndexError:
        _current_mode = None


def gcm():
    if _current_mode is None:
        raise ModeConfig('Current mode is not set')
    return _current_mode


__all__ = [
    'D0ToKpipipi_RS',
    'D0ToKpipipi_WS',
    'D0ToKpipipi_2tag_RS',
    'D0ToKpipipi_2tag_WS',
    'MODE'
]
