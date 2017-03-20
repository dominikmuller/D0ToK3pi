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
            'Dst': '[D*(2010)+ -> (D~0 -> K+ pi- pi- pi+) pi+]CC',
        },
        {
            'D0': '[D*(2010)+ -> ^(D~0 -> K+ pi- pi- pi+) pi+]CC'
        },
        {
            'K': '[D*(2010)+ -> (D~0 -> ^K+ pi- pi- pi+) pi+]CC',
            'Pi_OS1': '[D*(2010)+ -> (D~0 -> K+ ^pi- pi- pi+) pi+]CC',
            'Pi_OS2': '[D*(2010)+ -> (D~0 -> K+ pi- ^pi- pi+) pi+]CC',
            'Pi_SS': '[D*(2010)+ -> (D~0 -> K+ pi- pi- ^pi+) pi+]CC',
            'Pislow': '[D*(2010)+ -> (D~0 -> K+ pi- pi-  pi+) ^pi+]CC',
        },
        inputs_template.format(line),
        simulation
    )

    return d
