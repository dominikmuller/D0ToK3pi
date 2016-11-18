from Configurables import DaVinci, GaudiSequencer, FilterDesktop
from helpers import config

config.stream = 'Phys'

import modes

tuples = []

tuples.append(modes.D0ToKpipipi_2tag_RS.get())
tuples.append(modes.D0ToKpipipi_2tag_WS.get())

tuple_members = []

# for t in tuples:

    # vertex_filter = FilterDesktop(
        # '{0}VertexFilter'.format(t['name']),
        # Code='HASVERTEX',
        # Inputs=t['tuple'].Inputs
    # )
    # vertex_filter_seq = GaudiSequencer(
        # '{0}VertexFilterSequencer'.format(t['name']),
        # Members=[vertex_filter, t['tuple']]
    # )
    # tuple_members.append(vertex_filter_seq)

tuple_seq = GaudiSequencer('TupleSequencer', Members=[t['tuple'] for t in tuples],
                           IgnoreFilterPassed=True)

# Only run the ntuple sequence if the filter passes
main_seq = GaudiSequencer('MainSequencer', Members=[tuple_seq])

DaVinci().UserAlgorithms.append(main_seq)
