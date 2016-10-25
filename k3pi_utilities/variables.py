import sys

__all__ = []

all_ever_used = set()


class AccessorUsage(Exception):

    def __init__(self, message):
        super(AccessorUsage, self).__init__(message)

thismodule = sys.modules[__name__]


tev = r'$\mathrm{\,Te\kern -0.1em V}$'
gev = r'$\mathrm{\,Ge\kern -0.1em V}$'
mev = r'$\mathrm{\,Me\kern -0.1em V}$'
kev = r'$\mathrm{\,ke\kern -0.1em V}$'
ev = r'$\mathrm{\,e\kern -0.1em V}$'
gevc = r'${\mathrm{\,Ge\kern -0.1em V\!/}c}$'
mevc = r'${\mathrm{\,Me\kern -0.1em V\!/}c}$'
gevcc = r'${\mathrm{\,Ge\kern -0.1em V\!/}c^2}$'
gevgevcccc = r'${\mathrm{\,Ge\kern -0.1em V^2\!/}c^4}$'
mevcc = r'${\mathrm{\,Me\kern -0.1em V\!/}c^2}$'


class var(object):
    def __init__(self, name, fmt, mom, kid, pretty=None, unit=None):
        self.name = name
        self.fmt = fmt
        self.mom = mom
        self.kid = kid
        if pretty is not None:
            self.pretty = pretty
        else:
            self.pretty = fmt
        self.unit = unit
        setattr(thismodule, name, self)
        __all__.append(name)

    def __call__(self, part=None):
        if 'head' not in self.fmt and 'part' not in self.fmt:
            all_ever_used.add(self.fmt)
            return self.fmt
        if len(part.daughters) > 0 and not self.mom:
            raise AccessorUsage('Variable only for final state.')
        if len(part.daughters) == 0 and not self.kid:
            raise AccessorUsage('Variable only for decayed.')
        head = part
        while(hasattr(head, 'head')):
            head = head.head
        var_name = self.fmt.format(head=head.name, part=part.name)
        all_ever_used.add(var_name)
        return var_name

    def latex(self, part, with_unit=False):
        if self.pretty is None:
            return None
        pn = part.title.replace('$', '')
        if 'PART' in self.pretty:
            fm = self.pretty.replace('PART', pn)
        else:
            fm = self.pretty.format(part=pn)
        if with_unit and self.unit is not None:
            fm += ' [{}]'.format(self.unit)
        return fm


var('pt', '{part}_PT', True, True, r'$p_{\text{T}}(PART)$', mevc)
var('p', '{part}_P', True, True, r'$p(PART)$', mevc)
var('eta', '{part}_ETA', True, True, r'$\phi(PART)$', mevc)
var('phi', '{part}_PHI', True, True, r'$\eta(PART)$', mevc)
var('m', '{part}_M', True, False, r'$m(PART)$', mevcc)
var('vchi2', '{part}_Loki_VCHI2NDOF', True, False)
var('ipchi2', '{part}_Loki_BPVIPCHI2', True, True)
var('dira', '{part}_Loki_BPVDIRA', True, False)
var('maxdoca', '{part}_Loki_ADOCAMAX', True, False)
var('mindoca', '{part}_Loki_ADOCAMIN', True, False)
var('probnnk', '{part}_MC15TuneV1_ProbNNk', False, True)
var('probnnpi', '{part}_MC15TuneV1_ProbNNpi', False, True)
var('probnnghost', '{part}_MC15TuneV1_ProbNNghost', False, True)
var('pidk', '{part}_PIDK', False, True)
var('evt_num', 'eventNumber', False, False)
var('dtf_pt', '{head}_DTFDict_{part}_PT', True, True)
var('dtf_p', '{head}_DTFDict_{part}_P', True, True)
var('dtf_eta', '{head}_DTFDict_{part}_ETA', True, True)
var('dtf_phi', '{head}_DTFDict_{part}_PHI', True, True)
var('dtf_m', '{head}_DTFDict_{part}_M', True, True)
var('dtf_chi2', '{head}_DTF_CHI2', True, False)
var('dtf_ndof', '{head}_DTF_NDOF', True, False)
