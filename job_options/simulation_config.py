# Mode specific configuration dictionaries

modeconfig = {}

modeconfig['RS'] = {
    'sim': {2015: 'Sim09b'},
    'reco': {2015: 'Reco15a'},
    'turbo': {2015: 'Turbo02'},
    'trig': {2015: 'Trig0x411400a2'},
    'event_type': 27265000,
    'stream': 'ALLSTREAMS.DST'
}

year_2015 = {
    'year': '2015',
    'dv': 'v38r1p1',
    'query': '/MC/2015/Beam6500GeV-2015-{polarity}-Nu1.6-25ns-Pythia8/{sim}/'
             '{trig}/{reco}/{turbo}/Stripping24NoPrescalingFlagged/'
             '{event_type}/{stream}',
    'dddb': 'dddb-20150724',
    'conddb': 'sim-20161124-vc-m{}100',
}

years = {
    2015: year_2015,
}

tags_file = (
    'from Configurables import DaVinci\n'
    '\n'
    '\n'
    "DaVinci().DDDBtag = '{dddb_tag}'\n"
    "DaVinci().CondDBtag = '{conddb_tag}'\n"
    'DaVinci().EvtMax = {evt_max}\n'
    'DaVinci().PrintFreq = {printf}\n'
)

configs_file = (
    'def get_modes():\n'
    "    return {modes}\n"
    '\n'
    '\n'
    'def is_turbo():\n'
    '    return {turbo}\n'
    '\n'
    '\n'
    'def is_mc():\n'
    '    return {mc}\n'
)
