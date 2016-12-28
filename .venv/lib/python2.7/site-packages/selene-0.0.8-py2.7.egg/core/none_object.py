
class NoneObject(object):
    def __init__(self, description):
        self.description = description

    def __getattr__(self, item):
        raise AttributeError("'NoneObject' for '%s' has no attribute '%s'" % (self.description, item))
