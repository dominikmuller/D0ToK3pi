magup = 'MagUp'
magdown = 'MagDown'
magboth = 'MagBoth'
polarities = (magup, magdown)
all_polarities = (magup, magdown, magboth)
eos_root = 'root://eoslhcb.cern.ch//eos/lhcb/user/d/dmuller/K3PI'

D0ToKpipipi_RS = 'D0ToKpipipi_RS'
D0ToKpipipi_WS = 'D0ToKpipipi_WS'
D0ToKpipipi_2tag_RS = 'D0ToKpipipi_2tag_RS'
D0ToKpipipi_2tag_WS = 'D0ToKpipipi_2tag_WS'

kaon = 'K'
muon = 'Mu'
pion = 'Pi'
slowpion = 'sPi'
proton = 'P'
proton = 'muon'
Dz = 'D0'
Dst = 'Dst'
species = [kaon, pion, proton]

PDG_MASSES = {
    Dz: 1864.84,
    Dst: 2010.26,
    pion: 139.57,
    kaon: 493.677
}

ntuple_strip = 'Tuple{0}/DecayTree'
store_name = '{0}_{1}'
output_prefix = 'output'
output_mode = output_prefix + '/{}_{}_{}/'
data_store = output_prefix + '/data/store.h5'
