from Configurables import DaVinci

stream = 'Turbo'

simulation = DaVinci().Simulation
# inputs_template = '/Event/{0}/{{0}}/Particles'.format(stream)
inputs_template = '{0}/{{0}}/Particles'.format(stream)

# Import things necessary for LoKi MC truth matching
truth_matching_preambulo = [
    'from LoKiPhysMC.decorators import *',
    'from LoKiPhysMC.functions import mcMatch'
]

# Locations of standard particles
pions = 'Phys/StdAllNoPIDsPions'
merged_pions = 'Phys/StdLooseMergedPi0'
resolved_pions = 'Phys/StdLooseResolvedPi0'
kaons = 'Phys/StdAllNoPIDsKaons'
protons = 'Phys/StdAllNoPIDsProtons'
photons = 'Phys/StdLooseAllPhotons'
