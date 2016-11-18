from k3pi_config.modes.D0ToKpipipi_2tag_RS import D0ToKpipipi_2tag_RS as RS
from helpers import tuple_templates
from helpers.config import (
    inputs_template,
    simulation
)


def get():
    line = 'B02DstarMuNuDst2D0Pi_D2HHHHBeauty2CharmLine'

    d = dict()
    d['name'] = RS.mode
    d['tuple'] = tuple_templates.charm_tuple(
        'Tuple{0}'.format(d['name']),
        '( ( B0  -> ^( D*(2010)+  -> ^( D0  -> ^K-  ^pi-  ^pi+  ^pi+ )  ^pi+ )  ^mu- ) || ( B0  -> ^( D*(2010)-  -> ^( D0  -> ^K+  ^pi+  ^pi-  ^pi- )  ^pi- )  ^mu+ ) )',
        {
            RS.head.name: '( ( B0  -> ( D*(2010)+  -> ( D0  -> K-  pi-  pi+  pi+ )  pi+ )  mu- ) || ( B0  -> ( D*(2010)-  -> ( D0  -> K+  pi+  pi-  pi- )  pi- )  mu+ ) )'
        },
        {
            RS.Dst.name: '( ( B0  -> ^( ( D*(2010)+  -> ( D0  -> K-  pi-  pi+  pi+ )  pi+ ) ) mu- ) || ( B0  -> ^( ( D*(2010)-  -> ( D0  -> K+  pi+  pi-  pi- )  pi- ) ) mu+ ) )',
            RS.D0.name: '( ( B0  -> ( D*(2010)+  -> ^( ( D0  -> K-  pi-  pi+  pi+ ) ) pi+ )  mu- ) || ( B0  -> ( D*(2010)-  -> ^( ( D0  -> K+  pi+  pi-  pi- ) ) pi- )  mu+ ) )'
        },
        {
            RS.K.name: '( ( B0  -> ( D*(2010)+  -> ( D0  -> ^( K- ) pi-  pi+  pi+ )  pi+ )  mu- ) || ( B0  -> ( D*(2010)-  -> ( D0  -> ^( K+ ) pi+  pi-  pi- )  pi- )  mu+ ) )',
            RS.Pi_SS.name: '( ( B0  -> ( D*(2010)+  -> ( D0  -> K-  ^( pi- ) pi+  pi+ )  pi+ )  mu- ) || ( B0  -> ( D*(2010)-  -> ( D0  -> K+  ^( pi+ ) pi-  pi- )  pi- )  mu+ ) )',
            RS.Pi_OS1.name: '( ( B0  -> ( D*(2010)+  -> ( D0  -> K-  pi-  ^( pi+ ) pi+ )  pi+ )  mu- ) || ( B0  -> ( D*(2010)-  -> ( D0  -> K+  pi+  ^( pi- ) pi- )  pi- )  mu+ ) )',
            RS.Pi_OS2.name: '( ( B0  -> ( D*(2010)+  -> ( D0  -> K-  pi-  pi+  ^( pi+ ))  pi+ )  mu- ) || ( B0  -> ( D*(2010)-  -> ( D0  -> K+  pi+  pi-  ^( pi- ))  pi- )  mu+ ) )',
            RS.Pislow.name: '( ( B0  -> ( D*(2010)+  -> ( D0  -> K-  pi-  pi+  pi+ )  ^( pi+ ))  mu- ) || ( B0  -> ( D*(2010)-  -> ( D0  -> K+  pi+  pi-  pi- )  ^( pi- ))  mu+ ) )',
            RS.Mu.name: '( ( B0  -> ( D*(2010)+  -> ( D0  -> K-  pi-  pi+  pi+ )  pi+ )  ^( mu- )) || ( B0  -> ( D*(2010)-  -> ( D0  -> K+  pi+  pi-  pi- )  pi- )  ^( mu+ )) )',
        },
        inputs_template().format(line),
        simulation
    )

    return d
