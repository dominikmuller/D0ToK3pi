from k3pi_config.modes.D0ToKpipipi_RS import D0ToKpipipi_RS
from k3pi_config.modes.D0ToKpipipi_WS import D0ToKpipipi_WS
from k3pi_config.modes.D0ToKpipipi_2tag_RS import D0ToKpipipi_2tag_RS
from k3pi_config.modes.D0ToKpipipi_2tag_WS import D0ToKpipipi_2tag_WS
from k3pi_config.modes.mode_base import ModeConfig
import sys
from contextlib import contextmanager

_current_mode = None
_thismodule = sys.modules[__name__]


@contextmanager
def MODE(polarity, year, mode):
    global _current_mode
    if not hasattr(_thismodule, 'D0ToKpipipi_' + mode):
        raise ModeConfig('No mode {} -> {}'.format(
            mode, 'D0ToKpipipi_' + mode))
    _current_mode = getattr(
        _thismodule, 'D0ToKpipipi_' + mode)(polarity, year)
    yield _current_mode
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
