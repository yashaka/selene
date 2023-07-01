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

import sys
import typing
from typing import List, TypeVar, Generic, Iterable, Tuple, Optional

from selene.core.exceptions import ConditionNotMatchedError
from selene.core.wait import Predicate, Lambda

if sys.version_info >= (3, 10):
    from collections.abc import Callable
else:
    from typing import Callable


E = TypeVar('E')
R = TypeVar('R')


class Condition(Generic[E]):
    """
    Class for objects that are `Callable[[E], None]` like
    and represent the "condition that can pass or fail".
    """

    @classmethod
    def by_and(cls, *conditions):
        def func(entity):
            for condition in conditions:
                condition.call(entity)

        return cls(' and '.join(map(str, conditions)), func)

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

        return cls(' or '.join(map(str, conditions)), fn)

    @classmethod
    def for_each(cls, condition) -> Condition[Iterable[E]]:
        def fn(entity):
            items_with_error: List[Tuple[str, str]] = []
            index = None
            for index, item in enumerate(entity):
                try:
                    condition.call(item)
                except Exception as error:
                    items_with_error.append((str(item), str(error)))
            if items_with_error:
                raise AssertionError(
                    f'Not matched elements among all with indexes from 0 to {index}:\n'
                    + '\n'.join(
                        [f'{item}: {error}' for item, error in items_with_error]
                    )
                )

        return typing.cast(Condition[Iterable[E]], cls(f' each {condition}', fn))

    @classmethod
    def as_not(
        cls, condition: Condition[E], description: Optional[str] = None
    ) -> Condition[E]:
        # TODO: how will it work composed conditions?
        condition_words = str(condition).split(' ')
        is_or_have = condition_words[0]
        name = ' '.join(condition_words[1:])
        no_or_not = 'not' if is_or_have == 'is' else 'no'
        new_description = description or f'{is_or_have} {no_or_not} ({name})'

        def fn(entity):
            try:
                condition.call(entity)
            except Exception:
                return
            raise ConditionNotMatchedError()  # TODO: try to handle printing actual values here too...

        return cls(new_description, fn)

    # function throwIfNot<E>(predicate: (entity: E) => Promise<boolean>): Lambda<E, void> {
    #     return async (entity: E) => {
    #         if (!await predicate(entity)) {
    #             throw new ConditionNotMatchedError();
    #         }
    #     };
    # }

    @classmethod
    def raise_if_not(cls, description: str, predicate: Predicate[E]) -> Condition[E]:
        def fn(entity: E) -> None:
            if not predicate(entity):
                raise ConditionNotMatchedError()

        # TODO: consider the following style as one more option:
        #
        # @condition(description)  # or: @Condition.describe(description)
        # def fn(entity: E) -> None:
        #    if not predicate(entity):
        #        raise ConditionNotMatchedError()
        #
        # return fn

        return cls(description, fn)

    @classmethod
    def raise_if_not_actual(
        cls, description: str, query: Lambda[E, R], predicate: Predicate[R]
    ) -> Condition[E]:
        def fn(entity: E) -> None:
            query_to_str = str(query)
            result = (
                query.__name__ if query_to_str.startswith('<function') else query_to_str
            )
            actual = query(entity)
            if not predicate(actual):
                raise AssertionError(f'actual {result}: {actual}')

        return cls(description, fn)

    def __init__(self, description: str, fn: Lambda[E, None]):
        self._description = description
        self._fn = fn

    def call(self, entity: E) -> None:
        self.__call__(entity)

    @property
    def predicate(self) -> Lambda[E, bool]:
        def fn(entity):
            try:
                self.call(entity)
                return True
            except Exception as e:
                return False

        return fn

    # TODO: fix typing issues when passing to should explicitly
    @property
    def not_(self) -> Condition[E]:  # TODO: better name?
        return self.__class__.as_not(self)

    def __call__(self, entity: E) -> None:
        return self._fn(entity)

    def __str__(self):
        # TODO: consider changing has to have on the fly for CollectionConditions
        # TODO: or changing in collection locator rendering `all` to `collection`
        # TODO: or changing in match.* names from collection_has_* to all_have_*
        return self._description

    def and_(self, condition: Condition[E]) -> Condition[E]:
        return Condition.by_and(self, condition)

    def or_(self, condition: Condition[E]) -> Condition[E]:
        return Condition.by_or(self, condition)

    @property
    def each(self) -> Condition[Iterable[E]]:
        return Condition.for_each(self)


def not_(condition_to_be_inverted: Condition):  # TODO: do we really need it?
    return condition_to_be_inverted.not_
