# MIT License
#
# Copyright (c) 2015 Iakiv Kramarenko
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
from __future__ import annotations

from typing_extensions import TypeVar, Callable, Generic, Optional


T = TypeVar('T')
E = TypeVar('E')
R = TypeVar('R')

# TODO: not sure, if we need all these Lambda, Proc, Query, Command in python
# TODO: they was added just to quickly port selenidejs waiting mechanism
# TODO: let's consider removing them... or moving them e.g. to fp

Lambda = Callable[[T], R]
Proc = Callable[[T], None]
Predicate = Callable[[T], bool]
Fn = Callable[[T], R]


class Query(Generic[E, R]):
    def __init__(self, description: str, fn: Callable[[E], R | None]):
        self._description = description
        self._fn = fn

    def __call__(self, entity: E) -> R | None:
        return self._fn(entity)

    def __str__(self):
        return self._description

    @staticmethod
    def full_name_for(callable_: Optional[Callable]) -> str | None:
        if isinstance(callable_, Query):
            return str(callable_)

        qualname = getattr(callable_, '__qualname__', None)
        if qualname is not None and not qualname.endswith('<lambda>'):
            return (
                qualname
                if '<locals>.' not in qualname
                else getattr(callable_, '__name__', None)
            )

        return None

    # TODO: should we define __name__ and __qualname__ on it?


class Command(Query[E, None]):
    pass
