# MIT License
#
# Copyright (c) 2015-2019 Iakiv Kramarenko
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from abc import ABCMeta


def _make_delegator_method(name):
    def delegator(self, *args, **kwargs):
        return getattr(self.__delegate__, name)(*args, **kwargs)  # pragma: no cover
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
    return property(lambda self: getattr(self.__delegate__, name))  # pragma: no cover


def _is_property(name, cls):
    return isinstance(getattr(cls, name, None), property)


class DelegatingMeta(ABCMeta):
    def __new__(mcs, name, bases, dct):
        abstract_property_names = frozenset.union(
            *(frozenset(filter(lambda m: _is_property(m, base), base.__abstractmethods__))
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
