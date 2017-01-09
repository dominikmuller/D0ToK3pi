class PlotConfig(object):
    def __init__(self, functor, particle, binning, convert=None,
                 convert_label=None):
        self.functor = functor
        self.particle = particle
        self.var = functor(particle)
        self.binning = binning
        self.convert = convert
        if convert is not None and convert_label is not None:
            self.xlabel = convert_label.format(functor.latex(particle,
                                               with_unit=True))
        else:
            self.xlabel = functor.latex(particle, with_unit=True)
