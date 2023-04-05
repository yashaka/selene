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
import functools
from typing import TypeVar, Callable, Any, Tuple, Optional

# T = TypeVar('T', bound=Callable[..., Any])
T = TypeVar('T')
'''
A generic TypeVar to identify a Function Type, i.e. a function
but to be imported and used as fp.T so you can guess from full name,
that it is "function type", i.e. a function ;)
'''
F = TypeVar('F')
'''
A generic TypeVar to identify a Function Type, i.e. a function
can be imported and used as F directly, no need of `fp.F` version...,
you still can guess a shortcut F = Function)
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


def identity(it: T) -> T:
    return it


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


def thread(arg, *functions):
    return pipe(*functions)(arg)


def do(function: Callable[[T], Any]) -> Callable[[T], T]:
    def func(arg: T) -> T:
        function(arg)
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
