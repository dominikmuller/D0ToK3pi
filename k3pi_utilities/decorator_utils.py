class pop_arg:
    """Little helper to change initialiser arguments of decorating classes.
    Not elegant but better than rewriting large chunks of the code."""
    def __init__(self, deco, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.deco = deco
    def __call__(self, func):
        return self.deco(func, *self.args, **self.kwargs)
