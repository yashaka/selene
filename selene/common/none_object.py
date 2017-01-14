
class NoneObject(object):
    def __init__(self, description):
        # type: (str) -> None
        self.description = description

    def __getattr__(self, item):
        raise AttributeError("'NoneObject' for '%s' has no attribute '%s'" % (self.description, item))

    def __nonzero__(self):
        return False
