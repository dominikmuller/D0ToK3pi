from Configurables import DaVinci


def configure(year, mc, input_type, n_events, root=None, tfn=None):
    """General configuration of DaVinci object.

    Keyword arguments:
    year -- One of (2011, 2012)
    mc -- True if creating Monte Carlo ntuples, else False
    """
    dv = DaVinci()
    # Stripping output on CHARMCOMPLETEEVENT.DST, MC on ALLSTREAMS.DST
    dv.InputType = input_type
    # Output ntuple name
    dv.TupleFile = 'DVntuple.root'
    # Print status every 1000 events
    dv.PrintFreq = 1000
    dv.EvtMax = n_events
    # Year of data taking
    dv.DataType = str(year)
    # Is the data from simulation
    dv.Simulation = mc
    # Add a GetIntegratedLuminosity/LumiTuple TTree to output if appropriate
    dv.Lumi = not mc
    if root is not None:
        dv.RootInTES = root
    if tfn is not None:
        dv.TupleFile = tfn
