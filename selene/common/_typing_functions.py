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

import inspect
import re

from typing_extensions import (
    TypeVar,
    Callable,
    Generic,
    Optional,
    overload,
    Type,
    Iterable,
    Protocol,
    runtime_checkable,
)

from selene.common.fp import thread_last

T = TypeVar('T')
E = TypeVar('E')
R = TypeVar('R')

# TODO: not sure, if we need all these Lambda, Proc, Query, Command in python
# TODO: they was added just to quickly port selenidejs waiting mechanism
# TODO: let's consider removing them... or moving them e.g. to fp

Lambda = Callable[[T], R]
Proc = Callable[[T], None]
Predicate = Callable[[T], bool]  # todo: should we return bool or Optional[bool]?
Fn = Callable[[T], R]


@runtime_checkable
class _SupportsNameForEntity(Protocol):
    def _name_for(self, entity: E | None) -> str: ...


class Query(Generic[E, R]):
    def __init__(
        self,
        name: str | Callable[[E | None], str],
        /,
        fn: Callable[[E], R | None],
    ):
        self._name = name
        self._fn = fn

    def __call__(self, entity: E) -> R | None:  # todo: do we really need None here?
        return self._fn(entity)

    def __str__(self):
        return self._name if not callable(self._name) else self._name(None)

    def _name_for(self, entity: E) -> str:
        return self._name(entity) if callable(self._name) else self._name

    @staticmethod
    def _full_name_for(
        callable_: Optional[Callable],
        _entity: E | None = None,
    ) -> str | None:
        if callable_ is None:
            return None

        if isinstance(callable_, _SupportsNameForEntity):
            return callable_._name_for(_entity)

        # callable_ has its own __str__ implementation in its class
        if type(callable_).__str__ != object.__str__:
            return str(callable_)

        # callable has its own __str__ implementation on the object itself
        # TODO: do we even need to bother? And how should it property be done?
        # TODO: should it override previous?
        maybe_obj__str__ = getattr(callable_, '__str__', None)
        if maybe_obj__str__ and 'at 0x' not in (obj_as_str := maybe_obj__str__()):
            return obj_as_str

        callable_ = (
            callable_
            if inspect.isfunction(callable_)
            else (getattr(callable_, '__class__', None) or callable_)
        )

        qualname = getattr(callable_, '__qualname__', None)
        if qualname is not None and not qualname.endswith('<lambda>'):
            return (
                qualname
                if '<locals>.' not in qualname
                else qualname.split('<locals>.')[1]
            )

        return None

    # todo: would not human_readable_name_for be a better name for this helper?
    @staticmethod
    def _full_description_for(
        callable_: Optional[Callable],
        _entity: E | None = None,
    ) -> str | None:
        full_name = Query._full_name_for(callable_, _entity)
        return (
            thread_last(
                full_name,
                (re.sub, r'([a-z0-9])([A-Z])', r'\1 \2'),
                (re.sub, r'(\w)\.(\w)', r'\1 \2'),
                (re.sub, r'(^_+|_+$)', ''),
                (re.sub, r'_+', ' '),
                (re.sub, r'(\s)+', r'\1'),
                str.lower,
            )
            if full_name
            else None
        )

    @staticmethod
    def _full_description_or(
        alternative: str,
        /,
        *,
        for_: Optional[Callable],
        _with_prefix: str = '',
        _entity: E | None = None,
    ) -> str:
        return (
            _with_prefix + desc
            if (desc := Query._full_description_for(for_, _entity))
            else alternative
        )

    # @staticmethod
    # @overload
    # def _inverted(
    #     predicate: Predicate[E],
    #     _truthy_exceptions: Iterable[Type[Exception]] = (),
    # ) -> Predicate[E]: ...
    #
    # @staticmethod
    # @overload
    # def _inverted(
    #     predicate: Query[E, bool],
    #     _truthy_exceptions: Iterable[Type[Exception]] = (),
    # ) -> Query[E, bool]: ...

    @staticmethod
    def _inverted(
        predicate: Callable[[E], bool | None],
        _truthy_exceptions: Iterable[Type[Exception]] = (),
    ) -> Callable[[E], bool | None]:
        # TODO: ensure it works correctly:) e.g. unit test it

        def not_predicate(entity: E) -> bool:
            try:
                return not predicate(entity)
            except Exception as reason:
                if any(
                    isinstance(reason, exception) for exception in _truthy_exceptions
                ):
                    return True
                raise reason

        if isinstance(predicate, Query):
            return Query(
                f'not {predicate}',
                not_predicate,
            )

        # todo: consider refactoring to getattr(predicate, '__module__', None)
        not_predicate.__module__ = predicate.__module__
        not_predicate.__annotations__ = predicate.__annotations__

        predicate_name = getattr(predicate, '__name__', None)
        predicate_qualname = getattr(predicate, '__qualname__', None)
        if not predicate_name or not predicate_qualname:
            return not_predicate

        if '<lambda>' in predicate_name:
            not_predicate.__name__ = predicate_name
            not_predicate.__qualname__ = predicate_qualname
        else:
            not_predicate.__name__ = f'not_{predicate_name}'
            not_predicate.__qualname__ = f'not_{predicate_name}'.join(
                predicate_qualname.split(predicate_name)
            )

        return not_predicate

    # TODO: should we define __name__ and __qualname__ on it?


# TODO: should we change it to Query[E, None | Any]?
#       so it will be easier to define inline conditions where lambda returns not None
class Command(Query[E, None]):
    pass
