from k3pi_utilities.buffer import buffer_load
from k3pi_utilities.debugging import call_debug

from k3pi_config import config
from k3pi_config.modes import MODE


@buffer_load
def bdt_selection():
    from analysis import bdt_studies
    # return bdt_studies.get_bdt_discriminant() > 0.5
    bdt = bdt_studies.get_bdt_discriminant()
    bdt_sel = bdt['comb_bkg_bdt'] > 0.000296
    bdt_sel &= bdt['rand_spi_bdt'] > 0.484488
    return bdt_sel


@buffer_load
def spearmint_spi_selection():
    from analysis.selection import _apply_slow_pion_cut
    return _apply_slow_pion_cut(
        # max_spi_nnghost=0.288,
        # min_spi_nnpi=0.3,
        # max_spi_nnk=0.7,
        # max_spi_nnp=0.05,
        # max_spi_nnghost=0.300000,
        # max_spi_nnk=0.305837,
        # min_spi_nnpi=0.300000,
        # max_spi_nnp=0.15,
        max_spi_nnp=0.150000,
        min_spi_nnpi=0.596740,
        max_spi_nnghost=0.150000,
        max_spi_nnk=0.700000,
    )


@buffer_load
def spearmint_pid_selection():
    from analysis.selection import _apply_pid_cut
    return _apply_pid_cut(
        # max_k_nnpi=0.487964,
        # min_pi_nnpi=0.327319,
        # min_k_nnk=0.413452,
        # max_pi_nnk=0.375757,
        max_k_nnpi=0.699872,
        min_pi_nnpi=0.503407,
        min_k_nnk=0.714475,
        max_pi_nnk=0.699463,
    )


@call_debug
def get_complete_selection(ignore_flag=False):
    """Returns the full selection. Respects the spearmint flag."""
    from analysis.selection import full_selection
    sel = full_selection()
    if config.optimised_selection or ignore_flag:
        sel = sel & bdt_selection()
        sel = sel & spearmint_spi_selection()
        # sel = sel & spearmint_pid_selection()

    return sel


if __name__ == '__main__':
    import sys
    from k3pi_utilities import parser
    args = parser.create_parser()

    if args.selections is None:
        sels = [
            'spearmint_spi_selection',
            'spearmint_pid_selection',
            'bdt_selection'
        ]
    else:
        sels = args.selections

    with MODE(args.polarity, args.year, args.mode):
        for sel in sels:
            getattr(sys.modules[__name__], sel)(use_buffered=False)
