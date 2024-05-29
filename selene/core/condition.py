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
import warnings

from typing_extensions import (
    List,
    TypeVar,
    Generic,
    Iterable,
    Tuple,
    Optional,
    Self,
    override,
    cast,
)

from selene.core.exceptions import ConditionMismatch
from selene.common._typing_functions import Lambda, Predicate

# TODO: shouldn't we just import if from typing_extensions?
if sys.version_info >= (3, 10):
    from collections.abc import Callable
else:
    from typing import Callable


E = TypeVar('E')
R = TypeVar('R')


class Condition(Generic[E]):
    """Class to build, invert and compose "callable matcher" objects,
    that match to `Callable[[E], None | <RAISED ERROR>]` interface
    and represent the "conditions that can pass or fail when tested against an entity".
    So, once called on some entity of type E
    such condition object should test if the entity matches the condition object,
    and then simply pass if matched or raise AssertionError otherwise.

    Examples of constructing a new condition:

    ```python
    # These are dead simple "kind of standalone" callable conditions...

    # A function-based named condition
    def is_positive(x):
        if not x > 0:
            raise AssertionError(f'Expected positive number, but got {x}')
    # A predicate-function-based named condition
    def _is_positive(x):
        return x > 0
    is_positive = ConditionMismatch.to_raise_if_not(_is_positive)
    # Fully anonymous condition (i.e. no name will be rendered on failure)
    is_positive = ConditionMismatch.to_raise_if_not(lambda x: x > 0)

    # Now the Condition class allows to build conditions
    # that can be inverted via `.not_` and composed with each other via `and_` and `or_`
    is_positive = Condition('is positive', ConditionMismatch.to_raise_if_not(lambda x: x > 0))
    is_positive = Condition(ConditionMismatch.to_raise_if_not(Query('is positive', lambda x: x > 0)))
    is_not_positive = Condition('is positive', ConditionMismatch.to_raise_if_not(lambda x: x > 0), _inverted=True)
    is_not_positive = Condition('is positive', ConditionMismatch.to_raise_if_not(lambda x: x > 0)).not_

    # 💬 this does not make sense because we can't get _inverted from result of to_raise_if_not
    has_positive_decrement_by = lambda amount: Condition(
        ConditionMismatch.to_raise_if_not(
            Query('has positive', lambda res: res > 0),
            Query(f'decrement by {amount}', lambda x: x - amount),
            _inverted=False  # == DEFAULT
        ),
    )
    # 💬 this does not make sense cause we can't get descriptions
    has_positive_decrement_by = lambda amount: Condition(
        ConditionMismatch.to_raise_if_not(
            Query('has positive', lambda res: res > 0),
            Query(f'decrement by {amount}', lambda x: x - amount),
        ),
        _inverted=False  # == DEFAULT
    )
    # 💬 Here we have both description and _inverted for further inversion and customized rendering
    #    but we can can't customly render the actual value in case of inverted condition afterwards
    has_positive_decrement_by = lambda amount: Condition(
        f'has positive decrement by {amount}',
        test=ConditionMismatch.to_raise_if_not_actual(lambda x: x - amount, lambda res: res > 0),
        _inverted=False  # == DEFAULT
    )
    # 💬 but we could do this if to_raise_if_not_actual can accept _inverted too...
    #    but then we have to accept actual and predicate fns separately...
    #    like here:
    has_positive_decrement_by = lambda amount: Condition(
        f'has positive decrement by {amount}',
        actual=lambda x: x - amount,
        test_by=lambda res: res > 0,
        _inverted=False  # == DEFAULT
    )
    #    or:
    has_positive_decrement_by = lambda amount: Condition(
        actual=Query('has positive', lambda res: res > 0),
        test_by=Query(f'decrement by {amount}', lambda x: x - amount),
        _inverted=False  # == DEFAULT
    )
    #    what about this?
    has_positive_decrement_by = lambda amount: Condition(
        f'has positive decrement by {amount}',
        test=(lambda actual: actual - amount, lambda res: res > 0),
        _inverted=False  # == DEFAULT
    )
    ```
    """

    @classmethod
    def by_and(cls, *conditions):
        def func(entity):
            for condition in conditions:
                condition.__call__(entity)

        return cls(' and '.join(map(str, conditions)), func)

    @classmethod
    def by_or(cls, *conditions):
        def fn(entity):
            errors: List[Exception] = []
            for condition in conditions:
                try:
                    condition.__call__(entity)
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
                    condition.__call__(item)
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
    def as_not(  # TODO: ENSURE ALL USAGES ARE NOW CORRECT
        cls, condition: Condition[E], description: Optional[str] = None
    ) -> Condition[E]:
        # TODO: how will it work composed conditions?

        if description:
            return cls(
                # now we provide the new description that counts inversion
                description,
                # specifying already an inverted fn
                condition.__fn_inverted,
                # thus, no need to mark condition for further inversion:
                _inverted=False,
            )
        else:
            return condition.not_

    # function throwIfNot<E>(predicate: (entity: E) => Promise<boolean>): Lambda<E, void> {
    #     return async (entity: E) => {
    #         if (!await predicate(entity)) {
    #             throw new ConditionNotMatchedError();
    #         }
    #     };
    # }

    @classmethod
    def raise_if_not(cls, description: str, predicate: Predicate[E]) -> Condition[E]:
        return cls(description, ConditionMismatch._to_raise_if_not(predicate))

    @classmethod
    def raise_if_not_actual(
        cls, description: str, query: Lambda[E, R], predicate: Predicate[R]
    ) -> Condition[E]:
        return cls(description, ConditionMismatch._to_raise_if_not(predicate, query))

    # TODO: should we make the description type as Callable[[Condition], str]
    # instead of Callable[[], str]...
    # to be able to pass condition itself...
    # when we pass in child classes we pass self.__str__
    # that doesn't need to receive self, it already has it
    # but what if we want to pass some crazy lambda for description from outside
    # to kind of providing a "description self-based strategy" for condition?
    # maybe at least we can define it as varagrs? like Callable[..., str]
    def __init__(
        self,
        description: str | Callable[[], str],
        fn: Lambda[E, None],
        _inverted=False,
    ):
        self.__description = description
        self.__fn = fn
        self.__inverted = _inverted

    # TODO: rethink not_ naming...
    #       if condition is builder-like, for example:
    #       have.text('foo').ignore_case
    #       then, while semi-ok here:
    #       have.text('foo').ignore_case.not_
    #       it becomes totally confusing here:
    #       have.text('foo').not_.ignore_case
    #       but we can reduce incorrect usage just by limiting to -> Condition[E]
    #       – is it enough?
    @property
    def not_(self) -> Condition[E]:
        return self.__class__(
            self.__description,
            self.__fn,
            _inverted=not self.__inverted,
        )

    def __describe_inverted(self) -> str:
        condition_words = str(
            self.__description
            if not callable(self.__description)
            else self.__description()
        ).split(' ')
        is_or_have = condition_words[0]
        name = ' '.join(condition_words[1:])
        no_or_not = 'not' if is_or_have == 'is' else 'no'
        return f'{is_or_have} {no_or_not} ({name})'

    @property
    def __fn_inverted(self) -> Lambda[E, None]:

        def inverted_fn(entity: E) -> None:
            try:
                self.__fn(entity)
            except Exception:  # TODO: should we check only AssertionError here?
                return
            raise ConditionMismatch()

        return inverted_fn

    # TODO: consider changing has to have on the fly for CollectionConditions
    # TODO: or changing in collection locator rendering `all` to `collection`
    def __str__(self):
        return (
            (
                self.__description()
                if callable(self.__description)
                else self.__description
            )
            if not self.__inverted
            else self.__describe_inverted()
        )

    # TODO: we already have entity.matching for Callable[[E], bool]
    #       is it a good idea to use same term for Callable[[E], None] raising error?
    #       but is match vs matchING distinction clear enough?
    #       like "Match it!" says "execute the order!"
    #       and "Matching it?" says "give an answer (True/False) is it matched?"
    #       should we then add one more method to distinguish them? self.matching?
    #       or self.is_matched? (but this will contradict with entity.matching)
    #       still, self.match contradicts with pattern.match(string) that does not raise
    # TODO: would a `test` be a better name?
    #       kind of test term relates to testing in context of assertions...
    #       though naturally it does not feel like "assertion"...
    #       more like "predicate" returning bool (True/False), not raising exception
    def _match(self, entity: E) -> None:
        return self.__fn(entity) if not self.__inverted else self.__fn_inverted(entity)

    def _matching(self, entity: E) -> bool:
        return self.predicate(entity)

    def __call__(self, entity: E) -> None:
        return self._match(entity)

    def call(self, entity: E) -> None:
        warnings.warn(
            'condition.call(entity) is deprecated,'
            ' use condition(entity) or condition.__call__(entity) instead',
            DeprecationWarning,
        )
        self.__call__(entity)

    @property
    def predicate(self) -> Lambda[E, bool]:  # TODO: should we count inverted here too?
        def fn(entity):
            try:
                self.__call__(entity)
                return True
            except Exception:  # TODO: should we check only for AssertionError here?
                return False

        return fn

    # --- Condition builders (via self) ---

    def and_(self, condition: Condition[E]) -> Condition[E]:
        return Condition.by_and(self, condition)

    def or_(self, condition: Condition[E]) -> Condition[E]:
        return Condition.by_or(self, condition)

    @property
    def each(self) -> Condition[Iterable[E]]:
        return Condition.for_each(self)


# TODO: Should we merge this class with Condition?
#       see `x_test_not_match__of_constructed_via_factory__raise_if_not_actual` test
class _ConditionRaisingIfNotActual(Condition[E]):
    def __init__(
        self,
        # TODO: do we really need Self passed to callable below?
        #       in case we provide describing fn in subclass's init
        #       we definitely has access to self via closure...
        #       so the only need for Self here is to be able
        #       to pass it outside of class definition
        #       i.e. when building new condition directly calling
        #       this class init
        description: str,
        query: Lambda[E, R],
        predicate: Predicate[R],
        _inverted: bool = False,
    ):
        def match(entity: E) -> None:
            query_to_str = str(query)
            result = (
                query.__name__ if query_to_str.startswith('<function') else query_to_str
            )
            actual = query(entity)

            answer = None
            error_on_predicate = None
            try:
                answer = predicate(actual)
            except Exception as error:
                error_on_predicate = error

            describe_not_match = lambda: f'actual {result}: {actual}'

            if error_on_predicate:  # regardless of inverted or not
                raise AssertionError(
                    f'InvalidCompareError: {error_on_predicate}:\n'
                    + describe_not_match()
                )

            if answer if _inverted else not answer:  # now taking inverted into account
                raise AssertionError(describe_not_match())

        if _inverted:
            condition_words = description.split(' ')
            is_or_have = condition_words[0]
            name = ' '.join(condition_words[1:])
            no_or_not = 'not' if is_or_have == 'is' else 'no'
            description = f'{is_or_have} {no_or_not} ({name})'

        self.__description = description
        self.__query = query
        self.__predicate = predicate
        self.__inverted = _inverted

        super().__init__(
            description,
            match,
        )

    @override
    @property
    def not_(self):
        return _ConditionRaisingIfNotActual(
            self.__description,
            self.__query,
            self.__predicate,
            _inverted=not self.__inverted,
        )


def not_(condition_to_be_inverted: Condition):
    return condition_to_be_inverted.not_
