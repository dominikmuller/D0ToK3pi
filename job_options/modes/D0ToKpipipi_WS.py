from k3pi_config.modes.D0ToKpipipi_WS import D0ToKpipipi_WS as WS
from helpers import tuple_templates
from helpers.config import (
    inputs_template,
    simulation
)


def get():
    line = 'Hlt2CharmHadDstp2D0Pip_D02KpPimPimPipTurbo'

    d = dict()
    d['name'] = WS.mode
    d['tuple'] = tuple_templates.charm_tuple(
        'Tuple{0}'.format(d['name']),
        '[D*(2010)+ -> ^(D~0 -> ^K+ ^pi- ^pi- ^pi+) ^pi+]CC',
        {
            WS.Dst.name: '[D*(2010)+ -> (D~0 -> K+ pi- pi- pi+) pi+]CC',
        },
        {
            WS.D0.name: '[D*(2010)+ -> ^(D~0 -> K+ pi- pi- pi+) pi+]CC'
        },
        {
            WS.K.name: '[D*(2010)+ -> (D~0 -> ^K+ pi- pi- pi+) pi+]CC',
            WS.Pi_OS1.name: '[D*(2010)+ -> (D~0 -> K+ ^pi- pi- pi+) pi+]CC',
            WS.Pi_OS2.name: '[D*(2010)+ -> (D~0 -> K+ pi- ^pi- pi+) pi+]CC',
            WS.Pi_SS.name: '[D*(2010)+ -> (D~0 -> K+ pi- pi- ^pi+) pi+]CC',
            WS.Pislow.name: '[D*(2010)+ -> (D~0 -> K+ pi- pi-  pi+) ^pi+]CC',
        },
        inputs_template.format(line),
        simulation
    )

    return d
