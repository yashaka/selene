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
from typing_extensions import Tuple, cast

import selene
from selene.core.entity import Element, Collection


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
class _Element:  # todo: consider implementing LocationContext interface
    def __init__(self, selector: str | Tuple[str, str], _context=None):
        self.__selector = selector
        self.__context = _context

    def Element(self, selector: str | Tuple[str, str]) -> _Element:
        return _Element(selector, _context=self)

    def All(self, selector: str | Tuple[str, str]) -> _All:
        return _All(selector, _context=self)

    # --- Descriptor --- #

    def __set_name__(self, owner, name):
        self.__name = name  # TODO: use it

    # TODO: consider caching
    def __get__(self, instance, owner):
        self.__context = self.__context or getattr(instance, 'context', selene.browser)
        self.__as_context = cast(Element, self.__context.element(self.__selector))

        return self.__as_context

    # --- LocationContext --- #

    def element(self, selector: str | Tuple[str, str]):
        return self.__as_context.element(selector)

    def all(self, selector: str | Tuple[str, str]) -> Collection:
        return self.__as_context.all(selector)


class _All:

    def __init__(self, selector: str | Tuple[str, str], _context=None):
        self.__selector = selector
        self.__context = _context

    # --- Descriptor --- #

    def __set_name__(self, owner, name):
        self.__name = name  # TODO: use it

    # TODO: consider caching
    def __get__(self, instance, owner) -> Element:
        self.__context = self.__context or getattr(instance, 'context', selene.browser)
        self.__as_context = self.__context.all(self.__selector)

        return self.__as_context

    # --- FilteringContext --- #

    # TODO: implement...


S = _Element
SS = _All
