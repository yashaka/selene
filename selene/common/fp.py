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
import functools
import warnings

from typing_extensions import TypeVar, Callable, Any, Tuple, Optional, cast, Type

from selene.common.none_object import _NoneObject

# T = TypeVar('T', bound=Callable[..., Any])
T = TypeVar('T')
'''A generic TypeVar to identify a Function Type, i.e. a function
but to be imported and used as fp.T so you can guess from full name,
that it is "function type", i.e. a function ;)
'''
F = TypeVar('F')  # should we bound it as `bound=Callable[..., Any]`
'''A generic TypeVar to identify a Function Type, i.e. a function
can be imported and used as F directly, no need of `fp.F` version...,
you still can guess a shortcut F = Function)
'''

R = TypeVar('R')
'''A generic TypeVar to identify a Result Type, i.e. a type of result of a function
'''

_Decorator = Callable[[F], F]
_Decorator.__doc__ = """
    A type to represent a simple python decorator,
    defined here to type hint arguments and vars in a more readable way,
    so users can guess meaning from IDE autocompletion/other-hints...
    But it happened that e.g. PyCharm will yet render _Decorator simply to (F) -> F.
    Though, something like:
    # class Decorator(Callable[[F], F]):
    #     ...
    would be rendered like _Decorator...
    But is it even proper way in python to define types for type hints? (i.e. "subclassing" other types?)
    """

'''
# TODO: should we have something like?
_DecoratorFactory = Callable[..., Callable[[F], F]]
# pylint: disable=W2301
_DecoratorWithOptionalParameters = Callable[[Optional[F], ...], F]
# the last one even will not work for py3.7 :(
'''


def identity(it: R) -> R:
    return it


E = TypeVar('E', bound=Exception)


class AbsentResult(_NoneObject):
    pass


# todo: Should we also subclass Exception? in what order?
class AbsentError(_NoneObject):
    pass


# todo: some fns will return None.... So we have to use AbsentResult over AbsentError...
# todo: should we log actual error type in AbsentError description?
# todo: would the ... instead AbsentResult(str(fn)) or AbsentError be enough?
# todo: consider supporting exception_type as tuple of exception types
#       or should we create another helper for that?
def _either_res_or(
    exception_type: Type[E], fn: Callable[..., R], /, *args, **kwargs
) -> Tuple[R, Optional[E]]:
    try:
        return fn(*args, **kwargs), None
    except exception_type as failure:
        return cast(R, AbsentResult(str(fn))), failure


I = TypeVar('I')


def _maybeinstance(instance, type_: Type[I]) -> I | None:
    """An alternative to isinstance(type_instance:=instance, type_) to be used
    as maybe_type_instance = _maybeinstance(instance, type_)...

    Unfortunately will only work inside `if` clause with mypy...
    Yet mypy also may not work in `else` clause in some cases... :(

    Kind of, right now, there is no much need in this maybeinstance, because
    we can use `isinstance(type_instance:=instance, type_)` directly...
    """
    return cast(I, instance) if isinstance(instance, type_) else None


# todo: can we make the callable params generic too? (instead current ... as placeholder)
def _either(
    res: Callable[..., R], /, *, or_: Type[E]
) -> Callable[..., Tuple[R, Optional[E]]]:
    return functools.wraps(res)(
        lambda *args, **kwargs: _either_res_or(or_, res, *args, **kwargs)
    )


def raise_(exception: E) -> None:
    raise exception


def throw(exception: E) -> None:
    raise exception


def pipe(*functions) -> Optional[Callable[[Any], Any]]:
    """
    pipes functions one by one in the provided order
    i.e. applies arg1, then arg2, then arg3, and so on
    if any arg is None, just skips it
    """
    return (
        functools.reduce(
            lambda f, g: lambda x: f(g(x)) if g else f(x),
            functions[::-1],
            lambda x: x,
        )
        if functions
        else None
    )


def perform(*functions) -> Callable[[], None]:
    def one_by_one():
        for fn in functions:
            fn()

    return one_by_one


# TODO: support "detailed history of prev calls on failures"
# TODO: support tuple form of functions
# TODO: support ... as arg placeholder in tuple form of functions
#       or consider another custom object placeholder
#       Also consider numeric object placeholders,
#       like ~ fp.ARG1, fp.ARG2, etc. OR fp.ARG(1), fp.ARG(2), etc.
#       so if prev function returns iterable of results
#       they could be passed at corresponding positions
#       Also consider "spread object" placeholder (~ fp.SPREAD, or fp.ARG(...))
#       hm, actually ... can work as spread too...
#       hm, no, it can't... because if prev result was a list,
#       we have to know whether pass it in a spread form or as a single arg...
def thread(arg, *functions):
    return pipe(*functions)(arg)


# TODO: consider a separate function, similar to partial,
#       but with a placeholder for an argument(s)...
#       so we can write something like
#       map_with = partial_like(map, fn, ...)
#       where map_with is a function that accepts one arg (fn)
#       and returns a function of one arg,
#       that once passed will be placed as a last arg to map


def thread_first(arg, *iterable_of_fn_or_tuple):
    return (
        functools.reduce(
            lambda acc, fn_or_tuple: (
                fn_or_tuple(acc)
                if callable(fn_or_tuple)
                else fn_or_tuple[0](acc, *fn_or_tuple[1:])
            ),
            iterable_of_fn_or_tuple,
            arg,
        )
        if iterable_of_fn_or_tuple
        else arg
    )


def thread_last(arg, *iterable_of_fn_or_tuple):
    """Thread the first argument through a sequence of functions
    or tuples of functions with arguments in order to get rid of nested calls.
    Examples:
        >>> from selene.common.fp import thread_last, map_with
        >>> import re
        >>> result = thread_last(
        >>>     ['_have.special_number_', 10],
        >>>     map_with(str),
        >>>     ''.join,
        >>>     (re.sub, r'(^_+|_+$)', ''),
        >>>     (re.sub, r'_+', ' '),
        >>>     (re.sub, r'(\w)\.(\w)', r'\1 \2'),
        >>>     str.split,
        >>> )
        >>> assert result == ['have', 'special', 'number', '10']
    """
    return (
        functools.reduce(
            lambda acc, fn_or_tuple: (
                fn_or_tuple(acc)
                if callable(fn_or_tuple)
                else fn_or_tuple[0](*fn_or_tuple[1:], acc)
            ),
            iterable_of_fn_or_tuple,
            arg,
        )
        if iterable_of_fn_or_tuple
        else arg
    )


def do(function: Callable[[T], Any]) -> Callable[[T], T]:
    def func(arg: T) -> T:
        function(arg)
        return arg

    return func


def with_warn(*args, **kwargs):
    def func(arg: T) -> T:
        warnings.warn(*args, **kwargs)
        return arg

    return func


def write_silently(
    file: str, string: str, encoding: str = 'utf-8'
) -> Optional[Tuple[str, str]]:
    try:
        with open(file, 'w', encoding=encoding) as f:
            f.write(string)
            return file, string
    except OSError:
        return None


def map_with(fn: Callable):
    """Curried version of map function."""
    return lambda *iterables: map(fn, *iterables)
