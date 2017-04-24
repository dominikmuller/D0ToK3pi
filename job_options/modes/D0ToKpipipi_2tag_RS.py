from helpers import tuple_templates
from helpers.config import (
    inputs_template,
    simulation
)


def get():
    line = 'B02DstarMuNuDst2D0Pi_D2HHHHBeauty2CharmLine'

    d = dict()
    d['name'] = 'D0ToKpipipi_2tag_RS'
    d['tuple'] = tuple_templates.charm_tuple(
        'Tuple{0}'.format(d['name']),
        '( ( B0  -> ^( D*(2010)+  -> ^( D0  -> ^K-  ^pi-  ^pi+  ^pi+ )  ^pi+ )  ^mu- ) || ( B0  -> ^( D*(2010)-  -> ^( D0  -> ^K+  ^pi+  ^pi-  ^pi- )  ^pi- )  ^mu+ ) )',
        {
            'B0': '( ( B0  -> ( D*(2010)+  -> ( D0  -> K-  pi-  pi+  pi+ )  pi+ )  mu- ) || ( B0  -> ( D*(2010)-  -> ( D0  -> K+  pi+  pi-  pi- )  pi- )  mu+ ) )'
        },
        {
            'Dstp': '( ( B0  -> ^( ( D*(2010)+  -> ( D0  -> K-  pi-  pi+  pi+ )  pi+ ) ) mu- ) || ( B0  -> ^( ( D*(2010)-  -> ( D0  -> K+  pi+  pi-  pi- )  pi- ) ) mu+ ) )',
            'D0': '( ( B0  -> ( D*(2010)+  -> ^( ( D0  -> K-  pi-  pi+  pi+ ) ) pi+ )  mu- ) || ( B0  -> ( D*(2010)-  -> ^( ( D0  -> K+  pi+  pi-  pi- ) ) pi- )  mu+ ) )'
        },
        {
            'K': '( ( B0  -> ( D*(2010)+  -> ( D0  -> ^( K- ) pi-  pi+  pi+ )  pi+ )  mu- ) || ( B0  -> ( D*(2010)-  -> ( D0  -> ^( K+ ) pi+  pi-  pi- )  pi- )  mu+ ) )',
            'Pi_SS': '( ( B0  -> ( D*(2010)+  -> ( D0  -> K-  ^( pi- ) pi+  pi+ )  pi+ )  mu- ) || ( B0  -> ( D*(2010)-  -> ( D0  -> K+  ^( pi+ ) pi-  pi- )  pi- )  mu+ ) )',
            'Pi_OS1': '( ( B0  -> ( D*(2010)+  -> ( D0  -> K-  pi-  ^( pi+ ) pi+ )  pi+ )  mu- ) || ( B0  -> ( D*(2010)-  -> ( D0  -> K+  pi+  ^( pi- ) pi- )  pi- )  mu+ ) )',
            'Pi_OS2': '( ( B0  -> ( D*(2010)+  -> ( D0  -> K-  pi-  pi+  ^( pi+ ))  pi+ )  mu- ) || ( B0  -> ( D*(2010)-  -> ( D0  -> K+  pi+  pi-  ^( pi- ))  pi- )  mu+ ) )',
            'Pislow': '( ( B0  -> ( D*(2010)+  -> ( D0  -> K-  pi-  pi+  pi+ )  ^( pi+ ))  mu- ) || ( B0  -> ( D*(2010)-  -> ( D0  -> K+  pi+  pi-  pi- )  ^( pi- ))  mu+ ) )',
            'mu': '( ( B0  -> ( D*(2010)+  -> ( D0  -> K-  pi-  pi+  pi+ )  pi+ )  ^( mu- )) || ( B0  -> ( D*(2010)-  -> ( D0  -> K+  pi+  pi-  pi- )  pi- )  ^( mu+ )) )',
        },
        inputs_template().format(line),
        simulation
    )

    return d
