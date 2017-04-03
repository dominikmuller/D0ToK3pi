"""To avoid circular dependences, this is the master
selection file."""

from analysis import selection
from analysis import extended_selection
from analysis import candidate_sorting
from k3pi_utilities.debugging import call_debug
from k3pi_config import config


@call_debug
def get_final_selection():
    """Returns the full selection. Respects the spearmint flag."""
    sel = selection.full_selection()
    if config.optimised_selection:
        sel = sel & extended_selection.bdt_selection()
        sel = sel & extended_selection.spearmint_spi_selection()
    if config.candidates_selection:
        sel = sel & candidate_sorting.remove_right_sign_candidates()
        sel = sel & candidate_sorting.randomly_remove_candidates()

    return sel
