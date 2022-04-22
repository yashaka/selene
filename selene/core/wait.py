# MIT License
#
# Copyright (c) 2015-2022 Iakiv Kramarenko
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
from typing import Generic, Callable, TypeVar, Optional

from selene.core.exceptions import TimeoutException

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


Fn = Callable[[T], R]


# todo: consider moving outside of "wait" module... because there is no direct cohesion with it
class Query(Generic[T, R]):
    def __init__(self, description: str, fn: Callable[[T], R]):
        self._description = description
        self._fn = fn

    def __call__(self, entity: T) -> R:
        return self._fn(entity)

    def __str__(self):
        return self._description


class Command(Query[T, None]):
    pass


# todo: provide sexy fluent implementation via builder, i.e. Wait.the(element).atMost(3).orFailWith(hook)
class Wait(Generic[E]):

    # todo: provide the smallest possible timeout default, something like 1ms
    def __init__(
        self,
        entity: E,
        at_most: int,
        or_fail_with: Optional[Callable[[TimeoutException], Exception]] = None,
    ):
        self._entity = entity
        self._timeout = at_most
        self._hook_failure = or_fail_with or identity

    def at_most(self, timeout: int) -> Wait[E]:
        return Wait(self._entity, timeout, self._hook_failure)

    def or_fail_with(
        self, hook_failure: Optional[Callable[[TimeoutException], Exception]]
    ) -> Wait[E]:

        return Wait(self._entity, self._timeout, hook_failure)

    @property
    def hook_failure(
        self,
    ) -> Optional[Callable[[TimeoutException], Exception]]:
        # todo: hook_failure or failure_hook?
        return self._hook_failure

    # todo: consider renaming to `def to(...)`, though will sound awkward when wait.to(condition)
    def for_(self, fn: Callable[[E], R]) -> R:
        finish_time = time.time() + self._timeout

        while True:
            try:
                return fn(self._entity)
            except Exception as reason:
                if time.time() > finish_time:

                    reason_message = str(reason)

                    reason_string = '{name}: {message}'.format(
                        name=reason.__class__.__name__, message=reason_message
                    )
                    # todo: think on how can we improve logging failures in selene, e.g. reverse msg and stacktrace
                    # stacktrace = getattr(reason, 'stacktrace', None)
                    timeout = self._timeout
                    entity = self._entity

                    failure = TimeoutException(
                        f'''

Timed out after {timeout}s, while waiting for:
{entity}.{fn}

Reason: {reason_string}'''
                    )

                    raise self._hook_failure(failure)

    def until(self, fn: Callable[[E], R]) -> bool:
        try:
            self.for_(fn)
            return True
        except TimeoutException:
            return False

    # todo: do we really need these aliases?
    def command(self, description: str, fn: Callable[[E], None]) -> None:
        self.for_(Command(description, fn))

    def query(self, description: str, fn: Callable[[E], R]) -> R:
        return self.for_(Query(description, fn))
