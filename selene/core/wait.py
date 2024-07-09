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

import time
import warnings
from typing_extensions import Generic, Callable, TypeVar, Optional

from selene.core.exceptions import TimeoutException

from selene.common.fp import identity
from selene.common._typing_functions import Query, Command

T = TypeVar('T')
R = TypeVar('R')
E = TypeVar('E')
'''
A generic TypeVar to identify an Entity Type, i.e. something to wait on
'''


# TODO: provide sexy fluent implementation via builder, i.e. Wait.the(element).atMost(3).orFailWith(hook)
class Wait(Generic[E]):
    # TODO: provide the smallest possible timeout default, something like 1ms
    def __init__(
        self,
        entity: E,
        at_most: float,
        or_fail_with: Optional[Callable[[TimeoutException], Exception]] = None,
        _decorator: (
            Callable[[Wait[E]], Callable[[Callable[..., R]], Callable[..., R]]] | None
        ) = None,
        # TODO: should not we add here ignore_exceptions?
        #       (called as _falsy_exceptions in Condition init)
        #       and then tune it depending on context,
        #       e.g. in should we need to ignore only ConditionMismatch errors
        #       in commands we probably need to ignore a low more of WebDriverExceptions
        #       and so on...
    ):
        self.entity = entity
        self._timeout = at_most
        self._hook_failure = or_fail_with or identity
        self._decorator = _decorator or (lambda wait: identity)

    def with_(
        self,
        *,
        decorator: (
            Callable[[Wait[E]], Callable[[Callable[..., R]], Callable[..., R]]] | None
        ),
        # TODO: consider adding other options for consistency
    ) -> Wait[E]:
        return Wait(self.entity, self._timeout, self._hook_failure, decorator)

    @property
    def _entity(self):
        warnings.warn(
            'wait.entity will be removed in next version, '
            + 'please use wait.entity instead',
            DeprecationWarning,
        )
        return self.entity

    def at_most(self, timeout: float) -> Wait[E]:
        return Wait(self.entity, timeout, self._hook_failure)

    def or_fail_with(
        self, hook_failure: Optional[Callable[[TimeoutException], Exception]]
    ) -> Wait[E]:
        return Wait(self.entity, self._timeout, hook_failure)

    @property
    def hook_failure(
        self,
    ) -> Optional[Callable[[TimeoutException], Exception]]:
        # TODO: hook_failure or failure_hook?
        return self._hook_failure

    # TODO: consider renaming to `def to(...)`, though will sound awkward when wait.to(condition)
    # TODO: do we need a second description/named param?
    def for_(self, fn: Callable[[E], R]) -> R:
        def logic(fn: Callable[[E], R]) -> R:
            finish_time = time.time() + self._timeout

            while True:
                try:
                    return fn(self.entity)
                except Exception as reason:
                    if time.time() > finish_time:
                        reason_string = '{name}: {message}'.format(
                            name=reason.__class__.__name__,
                            message=getattr(reason, "msg", str(reason)),
                        )
                        # TODO: think on how can we improve logging failures in selene, e.g. reverse msg and stacktrace
                        # stacktrace = getattr(reason, 'stacktrace', None)
                        # TODO: should we have an option to turn on stacktrace logging?
                        timeout = self._timeout
                        entity = self.entity

                        # TODO: consider using Query.full_description_for(fn)
                        # TODO: consider customizing what to use on __init__
                        fn_name = Query.full_name_for(fn) or str(fn)

                        failure = TimeoutException(
                            f'\n'
                            f'\nTimed out after {timeout}s, while waiting for:'
                            f'\n{entity}.{fn_name}'
                            f'\n'
                            f'\nReason: {reason_string}'
                        )

                        raise self._hook_failure(failure)

        return self._decorator(self)(logic)(fn)

    def until(self, fn: Callable[[E], R]) -> bool:
        try:
            self.for_(fn)
            return True
        except TimeoutException:
            return False

    # TODO: do we really need these aliases?
    def command(self, name: str, fn: Callable[[E], None]) -> None:
        self.for_(Command(name, fn))

    def query(self, name: str, fn: Callable[[E], R]) -> Optional[R]:
        return self.for_(Query(name, fn))
