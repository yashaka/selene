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
from abc import ABCMeta, abstractmethod

import six
import time

from future.utils import with_metaclass
from typing import TypeVar, Callable, Generic, Optional
from selenium.common.exceptions import TimeoutException

from selene.abctypes.conditions import IEntityCondition

# todo: deprecate wait_for
from selene.common.fp import identity
from selene.exceptions import ConditionNotMatchedError


def wait_for(entity, condition, timeout=4, polling=0.1):
    # type: (object, IEntityCondition, int) -> object
    end_time = time.time() + timeout
    while True:
        try:
            return condition.fn(entity)
        except Exception as reason:
            reason_message = str(reason)
            # reason_message = getattr(reason, 'msg',  # todo: is the previous line enough?
            #                          getattr(reason, 'message',
            #                                  getattr(reason, 'args', '')))

            if six.PY2:
                if isinstance(reason_message, unicode):
                    reason_message = reason_message.encode('unicode-escape')
            reason_string = '{name}: {message}'.format(name=reason.__class__.__name__, message=reason_message)
            screen = getattr(reason, 'screen', None)
            stacktrace = getattr(reason, 'stacktrace', None)

            if time.time() > end_time:
                raise TimeoutException('''
            failed while waiting {timeout} seconds
            to assert {condition}
            for {entity}

            reason: {reason}'''.format(
                    timeout=timeout,
                    condition=condition.description(),
                    entity=entity,
                    reason=reason_string), screen, stacktrace)

            time.sleep(polling)


def satisfied(entity, condition):
    try:
        value = condition(entity)
        return value if value is not None else False
    except Exception as exc:
        return False


# --- New version of waiting mechanism --- #


T = TypeVar("T")
R = TypeVar("R")
E = TypeVar("E")

# todo: not sure, if we need all these Lambda, Proc, Query, Command in python
# todo: they was added just to quickly port selenidejs waiting mechanism
# todo: let's consider removing them...

Lambda = Callable[[T], R]
Predicate = Callable[[T], bool]

Proc = Callable[[T], None]


class IFn(with_metaclass(ABCMeta, Generic[T, R])):  # todo: consider using Callable[[T], R] instead

    @abstractmethod
    def call(self, entity):
        # type: (T) -> R
        pass


# todo: consider renaming to DescribedFn or DescribedQuery
class Query(IFn[T, R]):

    def __init__(self, description, fn):
        # type: (str, Lambda[T, R]) -> None

        self._description = description
        self._fn = fn

    def call(self, entity):
        # type: (T) -> R
        return self._fn(entity)

    def __str__(self):
        return self._description


Command = Query[T, None]


# class Command(IFn):
#
#     def __init__(self, description, fn):
#         # type: (str, Proc) -> None
#
#         self._description = description
#         self._fn = fn
#
#     def call(self, entity):
#         # type: (T) -> None
#         self._fn(entity)
#
#     def __str__(self):
#         return self._description


class Condition(IFn[E, None]):

    @classmethod
    def by_and(cls, *conditions):
        def fn(entity):
            for condition in conditions:
                condition.call(entity)

        return Condition(' and '.join(map(str, conditions)), fn)

    @classmethod
    def by_or(cls, *conditions):
        def fn(entity):
            errors = []  # type: List[Exception]
            for condition in conditions:
                try:
                    condition.call(entity)
                    return
                except Exception as e:
                    errors.append(e)
            raise AssertionError('; '.join(map(str, errors)))

        return Condition(' or '.join(map(str, conditions)), fn)

    @classmethod
    def as_not(cls, condition, description=None):
        # type: (Condition[E], str) -> Condition[E]
        condition_words = str(condition).split(' ')
        is_or_have = condition_words[1]
        name = ' '.join(condition_words[1:])
        no_or_not = 'not' if is_or_have == 'is' else 'no'
        new_description = description or '{is_or_have} {no_or_not} {name}'.format(**vars())

        def fn(entity):
            try:
                condition.call(entity)
            except Exception:
                return
            raise ConditionNotMatchedError()

        return Condition(new_description, fn)

    # function throwIfNot<E>(predicate: (entity: E) => Promise<boolean>): Lambda<E, void> {
    #     return async (entity: E) => {
    #         if (!await predicate(entity)) {
    #             throw new ConditionNotMatchedError();
    #         }
    #     };
    # }

    @classmethod
    def raise_if_not(cls, description, predicate):
        # type: (str, Predicate[E]) -> Condition[E]

        def fn(entity):
            # type: (E) -> None
            if not predicate(entity):
                raise ConditionNotMatchedError()

        return Condition(description, fn)

    @classmethod
    def raise_if_not_actual(cls, description, query, predicate):
        # type: (str, Lambda[E, R], Predicate[R]) -> Condition[E]

        def fn(entity):
            # type: (E) -> None
            actual = query(entity)
            if not predicate(actual):
                raise AssertionError('actual {query}: {actual}'.format(**vars()))

        return Condition(description, fn)

    def __init__(self, description, fn):
        # type: (str, Lambda[E, None]) -> None

        self._description = description
        self._fn = fn

    def call(self, entity):
        # type: (E) -> None
        self._fn(entity)

    def __str__(self):
        return self._description

    def and_(self, condition):
        # type: (Condition[E]) -> Condition[E]
        return Condition.by_and(self, condition)

    def or_(self, condition):
        # type: (Condition[E]) -> Condition[E]
        return Condition.by_or(self, condition)

    def to_predicate(self):
        # type: () -> Lambda[E, bool]

        def fn(entity):
            try:
                self.call(entity)
                return True
            except Exception as e:
                return False

        return fn


# todo: provide sexy fluent implementation via builder, i.e. Wait.the(element).atMost(3).orFailWith(hook)
class Wait(Generic[E]):

    # todo: provide the smallest possible timeout default, something like 1ms
    def __init__(self, entity: E, at_most: int, or_fail_with: Callable[[TimeoutException], Exception] = identity):
        self._entity = entity
        self._timeout = at_most
        self._hook_failure = or_fail_with

    def to(self, fn: IFn[E, R]) -> R:
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
