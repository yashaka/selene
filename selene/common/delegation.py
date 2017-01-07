from abc import ABCMeta


def _make_delegator_method(name):
    def delegator(self, *args, **kwargs):
        return getattr(self.__delegate__, name)(*args, **kwargs)
        # todo: consider using __call__() instead of __delegate__
        # in Python delegates are objects with __call__ method..
        # so why not to use the following:
        #     return getattr(self(), name)(*args, **kwargs)
        # ?
    return delegator


# def _make_delegator_method_to_property(name):
#     def delegator(self, *args, **kwargs):
#         return getattr(self.__delegate__, name)
#     return delegator


def _make_delegator_property(name):
    return property(lambda self: getattr(self.__delegate__, name))


def _is_property(name, cls):
    return isinstance(getattr(cls, name, None), property)


class DelegatingMeta(ABCMeta):
    def __new__(mcs, name, bases, dct):
        abstract_property_names = frozenset.union(*(frozenset(filter(lambda m: _is_property(m, base), base.__abstractmethods__))
                                                    for base in bases))

        for base in bases:
            base.__abstractmethods__ = frozenset(filter(lambda m: not _is_property(m, base), base.__abstractmethods__))

        abstract_method_names = frozenset.union(*(base.__abstractmethods__
                                                  for base in bases))

        for name in abstract_method_names:
            if name not in dct:
                dct[name] = _make_delegator_method(name)

        # for name in abstract_property_names:
        #     if name not in dct:
        #         dct[name] = _make_delegator_method_to_property(name)

        cls = super(DelegatingMeta, mcs).__new__(mcs, name, bases, dct)

        for name in abstract_property_names:
            if name not in dct:
                setattr(cls, name, _make_delegator_property(name))

        return cls


# todo: finalize naming: Delegating, Delegate, actual_delegate, delegatee, delegator o_O ?
# We have the following players in this game:
# * MetaClass for Classes of Objects who delegates their implementation to aggregated object
# So who should be named how?
