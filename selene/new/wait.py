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

from __future__ import annotations

import time
from abc import abstractmethod, ABC
from typing import Generic, Callable, TypeVar

from selenium.common.exceptions import TimeoutException

from selene.common.fp import identity

T = TypeVar('T')
R = TypeVar('R')
E = TypeVar('E')

# todo: not sure, if we need all these Lambda, Proc, Query, Command in python
# todo: they was added just to quickly port selenidejs waiting mechanism
# todo: let's consider removing them... or moving them e.g. to fp

Lambda = Callable[[T], R]
Proc = Callable[[T], None]
Predicate = Callable[[T], bool]


class IFn(ABC, Generic[T, R]):  # todo: consider using Callable[[T], R] instead

    @abstractmethod
    def call(self, entity: T) -> R:
        pass


# todo: consider renaming to DescribedFn or DescribedQuery
class Query(IFn[T, R]):

    def __init__(self, description: str, fn: Lambda[T, R]):
        self._description = description
        self._fn = fn

    def call(self, entity: T) -> R:
        return self._fn(entity)

    def __str__(self):
        return self._description


Command = Query[T, None]


# todo: provide sexy fluent implementation via builder, i.e. Wait.the(element).atMost(3).orFailWith(hook)
class Wait(Generic[E]):

    # todo: provide the smallest possible timeout default, something like 1ms
    def __init__(self, entity: E, at_most: int, or_fail_with: Callable[[TimeoutException], Exception] = identity):
        self._entity = entity
        self._timeout = at_most
        self._hook_failure = or_fail_with

    # todo: consider renaming to `def to(...)`, though will sound awkward when wait.to(condition)
    def for_(self, fn: IFn[E, R]) -> R:
        finish_time = time.time() + self._timeout

        while True:
            try:
                return fn.call(self._entity)
            except Exception as reason:
                if time.time() > finish_time:

                    reason_message = str(reason)

                    reason_string = '{name}: {message}'.format(name=reason.__class__.__name__, message=reason_message)
                    screen = getattr(reason, 'screen', None)
                    stacktrace = getattr(reason, 'stacktrace', None)
                    timeout = self._timeout
                    entity = self._entity

                    failure = TimeoutException(
                        f'''
            Timed out after {timeout}ms, while waiting for:
            {entity}.{fn}
            Reason: {reason_string}''',
                        screen,
                        stacktrace)

                    raise self._hook_failure(failure)

    def until(self, fn: IFn[E, R]) -> bool:
        try:
            self.for_(fn)
            return True
        except TimeoutException:
            return False

    # todo: do we need it?
    def command(self, fn: Callable[[E], R]) -> None:
        self.for_(Command(str(fn), fn))

    def query(self, fn: Callable[[E], R]) -> R:
        return self.for_(Query(str(fn), fn))