from Configurables import (
    DecayTreeTuple,
    MCDecayTreeTuple,
)
# This adds the addTupleTool and addBranches methods to {MC,}DecayTreeTuple
from DecayTreeTuple.Configuration import *  # NOQA
from Configurables import LoKi__Hybrid__DictOfFunctors
from Configurables import LoKi__Hybrid__Dict2Tuple
from Configurables import LoKi__Hybrid__DTFDict as DTFDict
from Configurables import TupleToolMCTruth, DaVinciSmartAssociator, P2MCPFromProtoP
from Configurables import MCMatchObjP2MCRelator, TupleToolMCBackgroundInfo, BackgroundCategory


def decay_tree_tuple(name, decay, mothers, intermediate,
                     daughters, inputs, mc):
    """Return a configured DecayTreeTuple instance.

    A DecayTreeTuple is configured with the given decay descriptor.
    The mothers dictionary is used to give exclusive tools to vertices, and it
    should be, as daughters, a dictionary of tuple branch names to branch
    descriptors.
    A typical method call might look like
        decay_tree_tuple(
            'TupleDstToD0pi_D0ToKpi',
            '[D*(2010)+ -> K- pi+]CC',
            {
                'Dst': '[D*(2010) -> (D0 -> K- pi+) pi+]CC',
                'D0': '[D*(2010) -> ^(D0 -> K- pi+) pi+]CC'
            },
            {
                'D0_K': '[D*(2010) -> (D0 -> ^K- pi+) pi+]CC',
                'D0_pi': '[D*(2010) -> (D0 -> K- ^pi+) pi+]CC',
                'Dst_pi': '[D*(2010) -> (D0 -> K- pi+) ^pi+]CC'
            },
            'Phys/StrippingLineName/Particles'
        )
    Keyword arguments:
    name -- TDirectory the DecayTreeTuple TTree will be saved in
    decay -- Decay descriptor
    mothers -- Branch descriptors to be added to the tuple as mothers;
               decaying particles
    daughters -- Branch descriptors to be added to the tuple as daughters;
                 final state particles
    inputs -- str of list of str, as the value of DecayTreeTuple.Inputs
    mc -- Extra MC information is included if True
    """

    # Define tuple tools to add
    tools = [
        "TupleToolPropertime",
        'TupleToolEventInfo',
    ]

    # Extra variables, added using LoKi hybrid tuple tools
    basic_loki_vars = {
        'ETA': 'ETA',
        'PHI': 'PHI',
        'PT': 'PT',
        'P': 'P',
        'Loki_BPVIPCHI2': 'BPVIPCHI2()',
        'Loki_MIPCHI2DV': 'MIPCHI2DV(PRIMARY)',
    }
    intermediate_loki_vars = {
        'Loki_AM34': 'LoKi.Particles.PFunA(AM34)',
        'Loki_AM4': 'LoKi.Particles.PFunA(AM4)',
        'Loki_BPVDIRA': "BPVDIRA",
        'Loki_acosBPVDIRA': "acos(BPVDIRA)",
    }
    daughter_loki_vars = {
        'PIDK': 'PIDK',
        'PIDe': 'PIDe',
        'PIDmu': 'PIDmu',
        'PIDp': 'PIDp',
        'Loki_TRACKCHI2NDOF': 'TRCHI2DOF',
        'Loki_TRACKGHOSTPROB': 'TRGHOSTPROB',
    }
    mother_loki_vars = {
        'M': 'M',
        'Loki_BPVVDCHI2': 'BPVVDCHI2',
        'Loki_BPVIPCHI2': 'BPVIPCHI2()',
        'Loki_DOCAMAX': 'DOCAMAX',
        'Loki_AMAXDOCA': "LoKi.Particles.PFunA(AMAXDOCA(''))",
        'Loki_AMINDOCA': "LoKi.Particles.PFunA(AMINDOCA(''))",
        'Loki_DOCACHI2MAX': 'DOCACHI2MAX',
        'Loki_VCHI2NDOF': 'VFASPF(VCHI2/VDOF)',
        'Loki_VX': 'VFASPF(VX)',
        'Loki_VY': 'VFASPF(VY)',
        'Loki_VZ': 'VFASPF(VZ)',
        'Loki_SUMPT': 'SUMTREE(PT,  ISBASIC)',
        'Loki_BPVLTIME': "BPVLTIME()",
    }

    # Template DecayTreeTuple
    t = DecayTreeTuple(name)

    # Providing str will throw an exception, so wrap it in a list
    try:
        t.Inputs = inputs
    except ValueError:
        t.Inputs = [inputs]
    t.Decay = decay
    # Merge the mother and daughter dictionaries
    dict(mothers.items() + intermediate.items() + daughters.items())
    t.addBranches(dict(mothers.items() + intermediate.items()
                       + daughters.items()))
    # Tools for all branches
    t.ToolList = tools
    # Verbose reconstruction information
    t.addTupleTool('TupleToolANNPID').ANNPIDTunes = ["MC15TuneV1"]
    # t.addTupleTool('TupleToolRecoStats')
    # MC truth information
    if mc:
        if has_turbo_inputs(t):
            print 'Adding MC truth information for Turbo'
            from TeslaTools import TeslaTruthUtils
            relations = TeslaTruthUtils.getRelLoc("")
            print 'relations = {}'.format(relations)
            toollist = ['MCTupleToolPrompt']
            rels = [relations]

            MCTruth = TupleToolMCTruth()
            #MCTruth.OutputLevel = 1
            MCTruth = t.addTupleTool('TupleToolMCTruth')
            MCTruth.ToolList = toollist
            MCTruth.addTool(DaVinciSmartAssociator)
            MCTruth.DaVinciSmartAssociator.RedoNeutral=False
            MCTruth.DaVinciSmartAssociator.addTool(P2MCPFromProtoP)
            MCTruth.DaVinciSmartAssociator.P2MCPFromProtoP.Locations = rels
            MCTruth.addTool(MCMatchObjP2MCRelator)
            MCTruth.MCMatchObjP2MCRelator.RelTableLocations = rels

            MCTruth.DaVinciSmartAssociator.addTool(BackgroundCategory)
            MCTruth.DaVinciSmartAssociator.BackgroundCategory.addTool(P2MCPFromProtoP)
            MCTruth.DaVinciSmartAssociator.BackgroundCategory.vetoNeutralRedo=True
            MCTruth.DaVinciSmartAssociator.BackgroundCategory.P2MCPFromProtoP.Locations = rels

            bkgcat = t.addTupleTool('TupleToolMCBackgroundInfo')
            bkgcat.addTool(BackgroundCategory)
            bkgcat.OutputLevel=10
            bkgcat.BackgroundCategory.vetoNeutralRedo=True
            bkgcat.BackgroundCategory.addTool(P2MCPFromProtoP)
            bkgcat.BackgroundCategory.P2MCPFromProtoP.Locations= rels

            t.OutputLevel=10
        else:
            print 'Adding MC truth information'
            t.addTupleTool('TupleToolMCTruth')
            t.addTupleTool('TupleToolMCBackgroundInfo')
    # Extra information from LoKi
    hybrid_tt = t.addTupleTool(
        'LoKi::Hybrid::TupleTool/basicLoKiTT'
    )
    hybrid_tt.Variables = basic_loki_vars
    hybrid_tt.Preambulo = ['from LoKiTracks.decorators import TrIDC']

    # Add mother-specific varaibles to each mother branch
    for mother in mothers:
        branch = getattr(t, mother)
        branch.addTupleTool(
            'LoKi::Hybrid::TupleTool/{0}LoKiTT'.format(mother)
        ).Variables = mother_loki_vars
        # For some unknown reason this doesn't work with Turbo candidates, so
        # the information for them has to be added to every branch
        DictTuple = branch.addTupleTool(LoKi__Hybrid__Dict2Tuple,
                                        name="DTFTuple")
        DictTuple.addTool(DTFDict, name="DTF")
        DictTuple.Source = "LoKi::Hybrid::DTFDict/DTF"
        DictTuple.NumVar = 6*(len(mothers) + len(intermediate)
                              + len(daughters))

        # configure the DecayTreeFitter in the usual way
        DictTuple.DTF.constrainToOriginVertex = True
        DictTuple.DTF.daughtersToConstrain = ['D0']
        DictTuple.DTF.addTool(LoKi__Hybrid__DictOfFunctors, name="dict")
        DictTuple.DTF.Source = "LoKi::Hybrid::DictOfFunctors/dict"
        DictTuple.DTF.dict.Variables = {
            "DTFDict_{}_PT".format(mother): "PT",
            "DTFDict_{}_ETA".format(mother): "ETA",
            "DTFDict_{}_PHI".format(mother): "PHI",
            "DTFDict_{}_P".format(mother): "P",
            "DTFDict_{}_M".format(mother): "M",
        }
        for part, decay in intermediate.items() + daughters.items():
            DictTuple.DTF.dict.Variables["DTFDict_{}_PT".format(
                part)] = "CHILD(PT,'{}')".format(decay)
            DictTuple.DTF.dict.Variables["DTFDict_{}_ETA".format(
                part)] = "CHILD(ETA,'{}')".format(decay)
            DictTuple.DTF.dict.Variables["DTFDict_{}_PHI".format(
                part)] = "CHILD(PHI,'{}')".format(decay)
            DictTuple.DTF.dict.Variables["DTFDict_{}_P".format(
                part)] = "CHILD(P,'{}')".format(decay)
            DictTuple.DTF.dict.Variables["DTFDict_{}_M".format(
                part)] = "CHILD(M,'{}')".format(decay)

    # Add intermediate-specific varaibles to each mother branch
    mom_int = mother_loki_vars.copy()
    mom_int.update(intermediate_loki_vars)
    for mother in intermediate:
        branch = getattr(t, mother)
        branch.addTupleTool(
            'LoKi::Hybrid::TupleTool/{0}LoKiTT'.format(mother)
        ).Variables = mom_int
        # For some unknown reason this doesn't work with Turbo candidates, so
        # the information for them has to be added to every branch

    for daughter in daughters:
        branch = getattr(t, daughter)
        branch.addTupleTool(
            'LoKi::Hybrid::TupleTool/{0}LoKiTT'.format(daughter)
        ).Variables = daughter_loki_vars

    return t


def charm_tuple(name, decay, mothers, intermediate,
                daughters, inputs, mc):
    """Return a charm cross section specific DecayTreeTuple instance.

    This amounts to the return value of decay_tree_tuple plus some event-level
    trigger decisions.
    Keyword arguments:
    See decay_tree_tuple.
    """
    t = decay_tree_tuple(name, decay, mothers, intermediate,
                         daughters, inputs, mc)

    # Define trigger lines we'd like to know the decisions of
    triggers_list = ['L0HadronDecision',
                     'Hlt1TrackMVADecision',
                     'Hlt1TwoTrackMVADecision',
                     'Hlt2CharmHadDstp2D0Pip_D02KmPimPipPipTurboDecision'
                     ]

    for part in mothers.keys() + intermediate.keys():
        branch = getattr(t, part)
        # TISTOS
        tistos = branch.addTupleTool('TupleToolTISTOS')
        tistos.TriggerList = triggers_list
        tistos.Verbose = True
        # tistos.VerboseL0 = True
        # tistos.VerboseHlt1 = True
        # tistos.VerboseHlt2 = True

    # Triggers
    trigger = t.addTupleTool('TupleToolTrigger')
    trigger.TriggerList = triggers_list
    trigger.Verbose = True
    # trigger.VerboseHlt1 = True

    if has_turbo_inputs(t):
        t.WriteP2PVRelations = False
        t.InputPrimaryVertices = "Turbo/Primary"

    return t


def mc_decay_tree_tuple(name, decay, mothers, daughters):
    """Return a configured MCDecayTreeTuple instance.

    A MCDecayTreeTuple is configured with the given decay descriptor.
    The mothers dictionary is used to give exclusive tools to vertices, and it
    should be, as daughters, a dictionary of tuple branch names to branch
    descriptors.
    A typical method call might look like
        mc_decay_tree_tuple(
            'MCTupleDstToD0pi_D0ToKpi',
            '[D*(2010) => ^(D0 => ^K- ^pi+) ^pi+]CC',
            {
                'Dst': '[D*(2010) => (D0 => K- pi+) pi+]CC',
                'D0': '[D*(2010) => ^(D0 => K- pi+) pi+]CC'
            },
            {
                'D0_K': '[D*(2010) => (D0 => ^K- pi+) pi+]CC',
                'D0_pi': '[D*(2010) => (D0 => K- ^pi+) pi+]CC',
                'Dst_pi': '[D*(2010) => (D0 => K- pi+) ^pi+]CC'
            }
        )
    Keyword arguments:
    name -- TDirectory the DecayTreeTuple TTree will be saved in
    decay -- Decay descriptor
    mothers -- Branch descriptors to be added to the tuple as mothers;
               decaying particles
    daughters -- Branch descriptors to be added to the tuple as daughters;
                 final state particles
    """
    t = MCDecayTreeTuple(name)
    t.Decay = decay
    t.addBranches(dict(mothers.items() + daughters.items()))
    t.ToolList = [
        'MCTupleToolPID',
        'MCTupleToolKinematic',
        'MCTupleToolReconstructed',
        'MCTupleToolHierarchy',
        'TupleToolPrimaries'
    ]
    # Verbose reconstruction information
    t.addTupleTool('TupleToolRecoStats').Verbose = True
    # Add MCTupleToolPrompt to all mothers
    for mother in mothers:
        branch = getattr(t, mother)
        # Does the particle ancestry contain a particle with a lifetime
        # above 1e-7 ns? Record the secondaries info if so
        branch.addTupleTool('MCTupleToolPrompt')
    return t


def has_turbo_inputs(dtt):
    """Return True if the DecayTreeTuple has Turbo stream inputs."""
    # Assume that 'Turbo' in any input string means this DTT runs on Turbo data
    return any('Turbo' in iput for iput in dtt.Inputs)
