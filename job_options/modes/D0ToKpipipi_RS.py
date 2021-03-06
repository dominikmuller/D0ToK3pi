from helpers import tuple_templates
from helpers.config import (
    inputs_template
)


def get(mc=False):
    line = 'Hlt2CharmHadDstp2D0Pip_D02KmPimPipPipTurbo'
    d0_dec = '[D*(2010)+ -> ^(D0 -> K- pi- pi+ pi+) pi+]CC'

    d = dict()
    d['name'] = 'D0ToKpipipi_RS'
    d['tuple'] = tuple_templates.charm_tuple(
        'Tuple{0}'.format(d['name']),
        '[D*(2010)+ -> ^(D0 -> ^K- ^pi- ^pi+ ^pi+) ^pi+]CC',
        {
            'Dstp': '[D*(2010)+ -> (D0 -> K- pi- pi+ pi+) pi+]CC',
        },
        {
            'D0': d0_dec
        },
        {
            'K': '[D*(2010)+ -> (D0 -> ^K- pi- pi+ pi+) pi+]CC',
            'Pi_SS': '[D*(2010)+ -> (D0 -> K- ^pi- pi+ pi+) pi+]CC',
            'Pi_OS1': '[D*(2010)+ -> (D0 -> K- pi- ^pi+ pi+) pi+]CC',
            'Pi_OS2': '[D*(2010)+ -> (D0 -> K- pi- pi+ ^pi+) pi+]CC',
            'Pislow': '[D*(2010)+ -> (D0 -> K- pi- pi+  pi+) ^pi+]CC',
        },
        inputs_template().format(line),
        mc
    )
    if mc:
        d['gen'] = tuple_templates.mc_decay_tree_tuple(
            'GenTuple{0}'.format(d['name']),
            '[D*(2010)+ ==> ^(D0 ==> ^K- ^pi- ^pi+ ^pi+) ^pi+]CC',
            {
                'Dstp': '[D*(2010)+ ==> (D0 ==> K- pi- pi+ pi+) pi+]CC',
            },
            {
                'D0': '[D*(2010)+ ==> ^(D0 ==> K- pi- pi+ pi+) pi+]CC',
                'K': '[D*(2010)+ ==> (D0 ==> ^K- pi- pi+ pi+) pi+]CC',
                'Pi_SS': '[D*(2010)+ ==> (D0 ==> K- ^pi- pi+ pi+) pi+]CC',
                'Pi_OS1': '[D*(2010)+ ==> (D0 ==> K- pi- ^pi+ pi+) pi+]CC',
                'Pi_OS2': '[D*(2010)+ ==> (D0 ==> K- pi- pi+ ^pi+) pi+]CC',
                'Pislow': '[D*(2010)+ ==> (D0 ==> K- pi- pi+  pi+) ^pi+]CC',
            }
        )

    d['sel'] = "(CHILD(PT, '{0}') > 3000*MeV) &" \
               "(CHILD(BPVIPCHI2(), '{0}') < 20.)".format(d0_dec)
    d['line'] = inputs_template().format(line)

    return d
