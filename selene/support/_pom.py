# MIT License
#
# Copyright (c) 2024 Iakiv Kramarenko
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

from functools import lru_cache

from typing_extensions import Tuple, cast

import selene


# TODO: should we built these descriptors into Element and Collection classes?
#       or should we ship them in separate module? (kind of from selene.pom import By, AllBy)
# todo: choose best naming...
#       > ContextElement + ContextAll
#       > By + AllBy
#       > OneBy + AllBy
#       > By(...).one + By(...)
#       > Element + AllElements
#       > Element + AllElements
#       > Element + All
#       > The + All
#       > One + All
#       > S + SS
#       > Element.inside + AllElements.inside
#       > Element.inside + Collection.inside
#       > Element.inside + AllElements.inside
#       > Inner + InnerAll
#       > Inside + InsideAll
#       > InnerElement
#       > The
class Element:  # todo: consider implementing LocationContext interface
    def __init__(self, selector: str | Tuple[str, str], _context=None):
        self.__selector = selector
        self.__context = _context

    def within(self, context, /):
        return Element(self.__selector, _context=context)

    def Element(self, selector: str | Tuple[str, str]) -> Element:
        return Element(selector, _context=self)

    def All(self, selector: str | Tuple[str, str]) -> All:
        return All(selector, _context=self)

    # --- Descriptor --- #

    def __set_name__(self, owner, name):
        self.__name = name  # TODO: use it

    @lru_cache
    def __get__(self, instance, owner):
        self.__context = self.__context or getattr(
            instance,
            'context',
            getattr(
                instance,
                'browser',
                selene.browser,
            ),
        )

        self.__as_context = cast(
            selene.Element,
            (
                self.__context.element(self.__selector)
                if isinstance(self.__context, (selene.Browser, selene.Element))
                # self.__context is of type self.__class__ ;)
                else self.__context._element(self.__selector)
            ),
        )

        return self.__as_context

    # --- LocationContext --- #

    # currently protected from direct access on purpose to not missclick on it
    # when actually the .Element or .All is needed
    def _element(self, selector: str | Tuple[str, str]):
        return self.__as_context.element(selector)

    # def _all(self, selector: str | Tuple[str, str]) -> selene.Collection:
    #     return self.__as_context.all(selector)


class All:

    def __init__(self, selector: str | Tuple[str, str], _context=None):
        self.__selector = selector
        self.__context = _context

    def within(self, context, /):
        return All(self.__selector, _context=context)

    # --- Descriptor --- #

    def __set_name__(self, owner, name):
        self.__name = name  # TODO: use it

    @lru_cache
    def __get__(self, instance, owner) -> selene.Element:
        self.__context = self.__context or getattr(
            instance,
            'context',
            getattr(
                instance,
                'browser',
                selene.browser,
            ),
        )
        self.__as_context = self.__context.all(self.__selector)

        return self.__as_context

    # --- FilteringContext --- #

    # TODO: implement...


# todo: consider aliases...
# S = _Element
# SS = _All
