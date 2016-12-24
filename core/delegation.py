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


class DelegatingMeta(ABCMeta):
    def __new__(mcs, name, bases, dct):
        abstract_method_names = frozenset.union(*(base.__abstractmethods__
                                                  for base in bases))
        for name in abstract_method_names:
            if name not in dct:
                dct[name] = _make_delegator_method(name)

        return super(DelegatingMeta, mcs).__new__(mcs, name, bases, dct)


# todo: finalize naming: Delegating, Delegate, actual_delegate, delegatee, delegator o_O ?
# We have the following players in this game:
# * MetaClass for Classes of Objects who delegates their implementation to aggregated object
# So who should be named how?
