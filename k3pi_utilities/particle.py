class ParticleDefinition(Exception):
    def __init__(self, message):
        super(ParticleDefinition, self).__init__(message)


class Particle(object):
    """Container class representing a particle"""
    def __init__(self, name, title, daughters=None, pid=None):
        """Initialise a new Particle object.

        Keyword arguments:
        name -- Branch name prefix this Particle represents
        title -- Pretty name to display in TLatex format (default: '')
        daughters -- List of Particle objects representing the decay products
                     of this particle (default: [])
        """
        self.name = name
        self.title = title
        self.daughters = daughters or []
        if daughters:
            for daughter in daughters:
                if(hasattr(daughter, 'head')):
                    raise ParticleDefinition(
                        '{} already assigned to mother'.format(daughter.name))
                setattr(daughter, 'head', self)
        self.pid = pid

    def __getattr__(self, name):
        """Access decay Particle objects with dot notation.

        Given the Particle object
          a = Particle('A', 'A', {
            'B': Particle('B', 'B'),
            'C' Particle('C', 'C')
        })
        the decay products A and B can be accessed as
            b = a.B
            c = a.C
        or equivalently using
            b = getattr(a, 'B')
            c = getattr(a, 'C')
        """
        for d in self.daughters:
            if d.name == name:
                return d
        raise AttributeError

    def __repr__(self):
        return "Particle(name='{0}', title='{1}', daughters={2})".format(
            self.name, self.title, self.daughters
        )

    def daughters_title(self, joinstr=''):
        """Return concatenation of daughters' titles, only to first depth."""
        return ''.join(map(lambda d: d.title, self.daughters))

    def all_mothers(self):
        """Return a list of Particles of this decay that themselves decay.

        A flat list of all decaying particles from all sub-decays is returned,
        including self.
        """
        def recurse_mothers(mother):
            mothers = []
            if mother.daughters:
                mothers.append(mother)
            for d in mother.daughters:
                mothers += recurse_mothers(d)
            return mothers
        return recurse_mothers(self)

    def all_daughters(self):
        """Return a list of Particles of this decay that do not decay.

        A flat list of all non-decaying particles from all sub-decays is
        returned.
        """
        def recurse_daughters(mother):
            daughters = []
            for d in mother.daughters:
                if not d.daughters:
                    daughters.append(d)
                daughters += recurse_daughters(d)
            return daughters
        return recurse_daughters(self)

    def all_pid(self, pid):
        """Function to get all daugthers for a given pid
        """
        return [d for d in self.all_daughters() if d.pid == pid]
