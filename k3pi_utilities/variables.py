import sys


class AccessorUsage(Exception):
    def __init__(self, message):
        super(AccessorUsage, self).__init__(message)

__variables__ = [
    ('pt', '{part}_PT', True, True),
    ('eta', '{part}_ETA', True, True),
    ('phi', '{part}_PHI', True, True),
    ('m', '{part}_M', True, True),
    ('vchi2', '{part}_Loki_VCHI2NDOF', True, False),
    ('ipchi2', '{part}_BPVIPCHI2', True, False),
    ('probnnk', '{part}_MC15TuneV1_ProbNNk', False, True),
    ('probnnpi', '{part}_MC15TuneV1_ProbNNpi', False, True),
    ('pidk', '{part}_PIDK', False, True),
    ('evt_num', 'eventNumber', False, False),
    ('dtf_pt', '{head}_DTFDict_{part}_PT', True, True),
    ('dtf_eta', '{head}_DTFDict_{part}_ETA', True, True),
    ('dtf_phi', '{head}_DTFDict_{part}_PHI', True, True),
    ('dtf_m', '{head}_DTFDict_{part}_M', True, True),
    ('dtf_chi2', '{head}_DTF_CHI2', True, False),
    ('dtf_ndof', '{head}_DTF_NDOF', True, False),
]


def make_function(definition):
    idf, form, mom, kid = definition
    if 'head' not in form and 'part' not in form:
        def tmp():
            return form
    else:
        def tmp(part):
            if len(part.daughters) > 0 and not mom:
                raise AccessorUsage('Variable only for final state.')
            if len(part.daughters) == 0 and not kid:
                raise AccessorUsage('Variable only for decayed.')
            head = part
            while(hasattr(head, 'head')):
                head = head.head
            return form.format(head=head.name, part=part.name)
    tmp.__name__ = idf
    return tmp


thismodule = sys.modules[__name__]
for definition in __variables__:
    setattr(thismodule, definition[0], make_function(definition))
