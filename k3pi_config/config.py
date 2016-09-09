magup = 'MagUp'
magdown = 'MagDown'
magboth = 'MagBoth'
polarities = (magup, magdown)
all_polarities = (magup, magdown, magboth)
eos_root = 'root://eoslhcb.cern.ch//eos/lhcb/user/d/dmuller/K3PI'

D0ToKpipipi_RS = 'D0ToKpipipi_RS'

kaon = 'K'
pion = 'Pi'
slowpion = 'sPi'
proton = 'P'
Dz = 'Dz'
Dst = 'Dst'
species = [kaon, pion, proton]

PDG_MASSES = {
    Dz: 1864.84,
    Dst: 2010.26,
    pion: 139.57,
    kaon: 493.677
}

ntuple_strip = 'Tuple{0}/DecayTree'
output_prefix = '../output'
