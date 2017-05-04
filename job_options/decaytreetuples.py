from Configurables import DaVinci, GaudiSequencer
from Configurables import FilterDesktop
from PhysSelPython.Wrappers import DataOnDemand, Selection, SelectionSequence
from configs import get_modes, is_mc

import modes

tuples = []

if 'RS' in get_modes():
    tuples.append(modes.D0ToKpipipi_RS.get(is_mc()))
if 'WS' in get_modes():
    tuples.append(modes.D0ToKpipipi_WS.get(is_mc()))

tuple_members = []
gen_members = []

for t in tuples:

    # vertex_filter = FilterDesktop(
        # '{0}VertexFilter'.format(t['name']),
        # Code='HASVERTEX',
        # Inputs=t['tuple'].Inputs
    # )
    # vertex_filter_seq = GaudiSequencer(
        # '{0}VertexFilterSequencer'.format(t['name']),
        # Members=[vertex_filter, t['tuple']]
    # )
    if 'sel' in t:
        sel = t['sel']  #
        dstp = DataOnDemand(t['line'])
        cutter = FilterDesktop(
            t['name']+'selector', Code=sel)
        selection = Selection(t['name']+'selection',
                              Algorithm=cutter,
                              RequiredSelections=[dstp])

        selseq = SelectionSequence(
            t['name']+'selectionsequence',
            TopSelection=selection
        )

        t['tuple'].Inputs = [selection.outputLocation()]

        sequencer = GaudiSequencer(
            '{0}SelectionSequencer'.format(t['name']),
            Members=[selseq.sequence(), t['tuple']])
        tuple_members.append(sequencer)
    else:
        tuple_members.append(t['tuple'])
    if is_mc():
        gen_members.append(t['gen'])


# Run the ntuple creation as a sequence, but don't worry about whether each
# ntuple gets filled
tuple_seq = GaudiSequencer('TupleSequencer', Members=tuple_members,
                           IgnoreFilterPassed=True)

if is_mc():
    gen_seq = GaudiSequencer('GenTupleSequencer', Members=gen_members,
                             IgnoreFilterPassed=True)
    main_seq = GaudiSequencer('MainSequencer', Members=[tuple_seq, gen_seq])
else:
    main_seq = GaudiSequencer('MainSequencer', Members=[tuple_seq])

DaVinci().UserAlgorithms.append(main_seq)
