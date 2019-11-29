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

from typing import List, TypeVar

from selene.exceptions import ConditionNotMatchedError
from selene.new.wait import Fn, Predicate, Lambda


E = TypeVar('E')
R = TypeVar('R')


class Condition(Fn[E, None]):

    @classmethod
    def by_and(cls, *conditions):
        def fn(entity):
            for condition in conditions:
                condition.call(entity)

        return Condition(' and '.join(map(str, conditions)), fn)

    @classmethod
    def by_or(cls, *conditions):
        def fn(entity):
            errors: List[Exception] = []
            for condition in conditions:
                try:
                    condition.call(entity)
                    return
                except Exception as e:
                    errors.append(e)
            raise AssertionError('; '.join(map(str, errors)))

        return Condition(' or '.join(map(str, conditions)), fn)

    @classmethod
    def as_not(cls, condition: Condition[E], description: str = None) -> Condition[E]:
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
    def raise_if_not(cls,
                     description: str,
                     predicate: Predicate[E]) -> Condition[E]:
        def fn(entity: E) -> None:
            if not predicate(entity):
                raise ConditionNotMatchedError()

        return Condition(description, fn)

    @classmethod
    def raise_if_not_actual(cls,
                            description: str,
                            query: Lambda[E, R],
                            predicate: Predicate[R]) -> Condition[E]:

        def fn(entity: E) -> None:
            actual = query(entity)
            if not predicate(actual):
                raise AssertionError('actual {query}: {actual}'.format(**vars()))

        return Condition(description, fn)

    def __init__(self, description: str, fn: Lambda[E, None]):
        self._description = description
        self._fn = fn

    def call(self, entity: E) -> None:
        self._fn(entity)

    @property
    def predicate(self) -> Lambda[E, bool]:
        def fn(entity):
            try:
                self.call(entity)
                return True
            except Exception as e:
                return False

        return fn

    def __str__(self):
        return self._description

    def and_(self, condition: Condition[E]) -> Condition[E]:
        return Condition.by_and(self, condition)

    def or_(self, condition: Condition[E]) -> Condition[E]:
        return Condition.by_or(self, condition)