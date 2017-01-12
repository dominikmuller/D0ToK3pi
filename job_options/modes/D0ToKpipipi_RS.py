from k3pi_config.modes.D0ToKpipipi_RS import D0ToKpipipi_RS as RS
from helpers import tuple_templates
from helpers.config import (
    inputs_template,
    simulation
)


def get(mc=False):
    line = 'Hlt2CharmHadDstp2D0Pip_D02KmPimPipPipTurbo'

    d = dict()
    d['name'] = RS.mode
    d['tuple'] = tuple_templates.charm_tuple(
        'Tuple{0}'.format(d['name']),
        '[D*(2010)+ --> ^(D0 --> ^K- ^pi- ^pi+ ^pi+) ^pi+]CC',
        {
            RS.Dstp.name: '[D*(2010)+ --> (D0 --> K- pi- pi+ pi+) pi+]CC',
        },
        {
            RS.D0.name: '[D*(2010)+ --> ^(D0 --> K- pi- pi+ pi+) pi+]CC'
        },
        {
            RS.K.name: '[D*(2010)+ --> (D0 --> ^K- pi- pi+ pi+) pi+]CC',
            RS.Pi_SS.name: '[D*(2010)+ --> (D0 --> K- ^pi- pi+ pi+) pi+]CC',
            RS.Pi_OS1.name: '[D*(2010)+ --> (D0 --> K- pi- ^pi+ pi+) pi+]CC',
            RS.Pi_OS2.name: '[D*(2010)+ --> (D0 --> K- pi- pi+ ^pi+) pi+]CC',
            RS.Pislow.name: '[D*(2010)+ --> (D0 --> K- pi- pi+  pi+) ^pi+]CC',
        },
        inputs_template().format(line),
        simulation
    )
    if mc:
        d['gen'] = tuple_templates.mc_decay_tree_tuple(
            'GenTuple{0}'.format(d['name']),
            '[D*(2010)+ ==> ^(D0 ==> ^K- ^pi- ^pi+ ^pi+) ^pi+]CC',
            {
                RS.Dstp.name: '[D*(2010)+ ==> (D0 ==> K- pi- pi+ pi+) pi+]CC',
            },
            {
                RS.D0.name: '[D*(2010)+ ==> ^(D0 ==> K- pi- pi+ pi+) pi+]CC',
                RS.K.name: '[D*(2010)+ ==> (D0 ==> ^K- pi- pi+ pi+) pi+]CC',
                RS.Pi_SS.name: '[D*(2010)+ ==> (D0 ==> K- ^pi- pi+ pi+) pi+]CC',
                RS.Pi_OS1.name: '[D*(2010)+ ==> (D0 ==> K- pi- ^pi+ pi+) pi+]CC',
                RS.Pi_OS2.name: '[D*(2010)+ ==> (D0 ==> K- pi- pi+ ^pi+) pi+]CC',
                RS.Pislow.name: '[D*(2010)+ ==> (D0 ==> K- pi- pi+  pi+) ^pi+]CC',
            }
        )

    return d
