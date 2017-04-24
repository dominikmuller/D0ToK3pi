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
mm = r'mm'
ns = r'ns'
kev = r'$\mathrm{\,ke\kern -0.1em V}$'
ev = r'$\mathrm{\,e\kern -0.1em V}$'
gevc = r'${\mathrm{\,Ge\kern -0.1em V\!/}c}$'
mevc = r'${\mathrm{\,Me\kern -0.1em V\!/}c}$'
gevcc = r'${\mathrm{\,Ge\kern -0.1em V\!/}c^2}$'
gevgevcccc = r'${\mathrm{\,Ge\kern -0.1em V^2\!/}c^4}$'
mevcc = r'${\mathrm{\,Me\kern -0.1em V\!/}c^2}$'


class var(object):
    def __init__(self, name, fmt, mom, kid, pretty=None,
                 unit=None, append=True, additional=False):
        self.name = name
        self.fmt = fmt
        self.mom = mom
        self.kid = kid
        if pretty is not None:
            self.pretty = pretty
        else:
            self.pretty = fmt
        self.unit = unit
        self.additional = additional
        setattr(thismodule, name, self)
        if append and not additional:
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

    def latex(self, part=None, with_unit=False):
        if self.pretty is None:
            return None
        if self.mom is False and self.kid is False:
            if with_unit and self.unit is not None:
                return self.pretty + ' [{}]'.format(self.unit)
            else:
                return self.pretty
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
var('eta', '{part}_ETA', True, True, r'$\eta(PART)$', mevc)
var('phi', '{part}_PHI', True, True, r'$\phi(PART)$', mevc)
var('m', '{part}_M', True, False, r'$m(PART)$', mevcc)
var('ltime', '{part}_Loki_BPVLTIME', True, False, r'$\tau$', ns)  # NOQA
var('vchi2', '{part}_Loki_VCHI2NDOF', True, False, r'Vertex $\chi^2/\text{dof}(PART)$')  # NOQA
var('ipchi2', '{part}_Loki_BPVIPCHI2', True, True, r'$\chi^2_\text{IP}(PART)$')  # NOQA
var('dira', '{part}_Loki_BPVDIRA', True, False, r'DIRA$(PART)$')
var('maxdoca', '{part}_Loki_AMAXDOCA', True, False, r'DOCA$_{\text{max}}(PART)$', mm)  # NOQA
var('mindoca', '{part}_Loki_AMINDOCA', True, False, r'DOCA$_{\text{min}}(PART)$', mm)  # NOQA
var('vdchi2', '{part}_Loki_BPVVDCHI2', True, False, r'$\chi^2_\text{VD}(PART)$')  # NOQA
var('probnnk', '{part}_MC15TuneV1_ProbNNk', False, True, r'ProbNN$K(PART)$')
var('probnne', '{part}_MC15TuneV1_ProbNNe', False, True, r'ProbNN$e(PART)$')
var('probnnp', '{part}_MC15TuneV1_ProbNNp', False, True, r'ProbNN$p(PART)$')
var('probnnmu', '{part}_MC15TuneV1_ProbNNmu', False, True, r'ProbNN$\mu(PART)$')
var('probnnpi', '{part}_MC15TuneV1_ProbNNpi', False, True, r'ProbNN$\pi(PART)$')  # NOQA
var('probnnghost', '{part}_MC15TuneV1_ProbNNghost', False, True, r'ProbNNghost$(PART)$')  # NOQA
var('pidk', '{part}_PIDK', False, True, r'$\text{DLL}_{K^\pm-\pi^\pm}(PART)$')
var('evt_num', 'eventNumber', False, False, 'Eventnumber')
var('run_num', 'runNumber', False, False, 'Runnumber')
var('dtf_pt', '{head}_DTFDict_{part}_PT', True, True, r'DTF $p_{\text{T}}(PART)$', mevc)  # NOQA
var('dtf_p', '{head}_DTFDict_{part}_P', True, True, r'DTF $p(PART)$', mevc)
var('dtf_eta', '{head}_DTFDict_{part}_ETA', True, True, r'DTF $\phi(PART)$', mevc)  # NOQA
var('dtf_phi', '{head}_DTFDict_{part}_PHI', True, True, r'DTF $\eta(PART)$', mevc)  # NOQA
var('dtf_m', '{head}_DTFDict_{part}_M', True, True, r'DTF $m(PART)$', mevcc)
var('dtf_chi2', '{head}_DTF_CHI2', True, False, r'DTF $\chi^2$')
var('dtf_ndof', '{head}_DTF_NDOF', True, False, r'DTF dof')
var('dm', 'delta_m', False, False, '$\Delta m$', mevcc, append=False)
var('dtf_dm', 'delta_m_dtf', False, False, 'DTF $\Delta m$', mevcc, append=False)  # NOQA
var('ipchi21', 'ipchi2_1', False, False, r'$1^\text{st} \chi^2_\text{IP}$', append=False)  # NOQA
var('ipchi22', 'ipchi2_2', False, False, r'$2^\text{nd} \chi^2_\text{IP}$', append=False)  # NOQA
var('ipchi23', 'ipchi2_3', False, False, r'$3^\text{rd} \chi^2_\text{IP}$', append=False)  # NOQA
var('ipchi24', 'ipchi2_4', False, False, r'$4^\text{th} \chi^2_\text{IP}$', append=False)  # NOQA
var('pt1', 'pt_1', False, False, r'$1^\text{st} p_{\text{T}}$', mevc, append=False)  # NOQA
var('pt2', 'pt_2', False, False, r'$2^\text{nd} p_{\text{T}}$', mevc, append=False)  # NOQA
var('pt3', 'pt_3', False, False, r'$3^\text{rd} p_{\text{T}}$', mevc, append=False)  # NOQA
var('pt4', 'pt_4', False, False, r'$4^\text{th} p_{\text{T}}$', mevc, append=False)  # NOQA
var('angle', 'dstp_slowpi_angle', False, False, r'$\Delta\Phi$', append=False, additional=True)  # NOQA
var('m12', 'm12', False, False, r'$m_{K^\pm\pi^\mp}$', mevcc, append=False, additional=True)  # NOQA
var('m34', 'm34', False, False, r'$m_{\pi^\pm\pi^\mp}$', mevcc, append=False, additional=True)  # NOQA
var('cos1', 'cos1', False, False, r'$\cos\theta_1$', None, append=False, additional=True)  # NOQA
var('cos2', 'cos2', False, False, r'$\cos\theta_2$', None, append=False, additional=True)  # NOQA
var('phi1', 'phi1', False, False, r'$\phi_1$', None, append=False, additional=True)  # NOQA
var('bdt', 'bdt', False, False, r'BDT discriminant', None, append=False, additional=True)  # NOQA
var('dtf_ip_diff', 'dtf_ip_diff', False, False, r'DTF $\chi^2 - \chi^2_\text{IP}(D^0)$', None, append=False, additional=True)  # NOQA
