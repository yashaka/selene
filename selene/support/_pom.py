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

from typing_extensions import Tuple

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
# todo: consider having _Element(selector, _context) as class, then element(selector) as alias
class element:  # todo: consider implementing LocationContext interface
    def __init__(self, selector: str | Tuple[str, str], _context=None):
        # TODO: should we set _name on init too?
        #       at least to None, if value was not provided...
        self._selector = selector
        self._instantiated_as_descriptor = False

        # todo: should we wrap lambda below into lru_cache?
        self._context = lambda instance: (
            (_context(instance) if callable(_context) else _context)
            or getattr(  # todo: refactor to one-liner via helper
                instance,
                'context',
                getattr(
                    instance,
                    '_context',
                    getattr(
                        instance,
                        'browser',
                        getattr(
                            instance,
                            '_browser',
                            selene.browser,
                        ),
                    ),
                ),
            )
        )

    def _as_context(self, instance) -> selene.Element:
        return (
            # # todo: one day we gonna pass a name to element ;)
            # #       once selene entities support naming
            # context_of_self.element(self._selector, _name=self._name)
            context_of_self.element(self._selector)
            if isinstance(
                context_of_self := self._context(instance),
                (selene.Browser, selene.Element),
            )
            # => self._context is a descriptor:
            else context_of_self._as_context(instance).element(self._selector)
        )

    def within(self, context, /):
        return element(self._selector, _context=context)

    @property
    def within_browser(self):
        return self.within(
            lambda instance: getattr(
                instance,
                'browser',
                getattr(
                    instance,
                    '_browser',
                    selene.browser,
                    # # currently disabled to leave at least one option to for end user
                    # # to disable this feature
                    # getattr(
                    #     instance,
                    #     f'_{instance.__class__.__name__}__browser',
                    #     selene.browser,
                    # ),
                ),
            )
        )

    def element(self, selector: str | Tuple[str, str]) -> element:
        return element(
            selector,
            _context=lambda instance: (  # todo: should we lru_cache it?
                (
                    getattr(instance, self._name),  # ← resolving descriptors chain –
                    self,  # – before returning the actual context :P
                    # otherwise any descriptor built on top of previously defined
                    # can be resolved improperly, because previous one
                    # might be not accessed yet, thus we have to simulate such assess
                    # on our own by forcing getattr
                )[1]
                # if hasattr(self, '_name')
                if self._instantiated_as_descriptor
                # => self if a "pass-through"-descriptor)
                else self._as_context(instance)
            ),
        )

    def all(self, selector: str | Tuple[str, str]) -> all_:
        return all_(
            selector,
            _context=lambda instance: (
                (
                    getattr(instance, self._name),
                    self,
                )[1]
                if self._instantiated_as_descriptor
                else self._as_context(instance)
            ),
        )

    # --- Descriptor --- #

    def __set_name__(self, owner, name):
        self._name = name  # TODO: use it
        self._instantiated_as_descriptor = True

    def __get__(self, instance, owner):
        # # this if is not needed, because unless we define __set__ on the descriptor
        # # on dot access, after we setattr on instance, python will first look in __dict__
        # # and only then in __get__ (of a non-data-descriptor
        # # – the one without __set__ or __del__)
        # if hasattr(instance, self._name):
        #     return getattr(instance, self._name)
        # else:
        as_context = self._as_context(instance)
        setattr(instance, self._name, as_context)
        return as_context

    # --- LocationContext ---
    # prev impl. was completely wrong, cause store "as_context" snapshot on self
    # but had to store it on instance...


class all_:
    def __init__(self, selector: str | Tuple[str, str], _context=None):
        self._selector = selector
        self._instantiated_as_descriptor = False

        self._context = lambda instance: (
            (_context(instance) if callable(_context) else _context)
            or getattr(  # todo: refactor to one-liner via helper
                instance,
                'context',
                getattr(
                    instance,
                    '_context',
                    getattr(
                        instance,
                        'browser',
                        getattr(
                            instance,
                            '_browser',
                            selene.browser,
                        ),
                    ),
                ),
            )
        )

    def _as_context(self, instance) -> selene.Collection:
        return (
            context_of_self.all(self._selector)
            if isinstance(
                context_of_self := self._context(instance),
                (selene.Browser, selene.Element, selene.Collection),
            )
            # => self._context is a descriptor:
            else context_of_self._as_context(instance).all(self._selector)
        )

    def within(self, context, /):
        return all_(self._selector, _context=context)

    # todo: think on better name... within_page?
    @property
    def within_browser(self):
        return self.within(
            lambda instance: getattr(
                instance,
                'browser',
                getattr(
                    instance,
                    '_browser',
                    selene.browser,
                    # # currently disabled to leave at least one option to for end user
                    # # to disable this feature
                    # getattr(
                    #     instance,
                    #     f'_{instance.__class__.__name__}__browser',
                    #     selene.browser,
                    # ),
                ),
            )
        )

    # --- Descriptor --- #

    def __set_name__(self, owner, name):
        self._name = name  # TODO: use it
        self._instantiated_as_descriptor = True

    def __get__(self, instance, owner):
        as_context = self._as_context(instance)
        setattr(instance, self._name, as_context)
        return as_context

    # --- FilteringContext --- #
    # todo: do we need it?


# todo: consider aliases...
# S = _Element
# SS = _All
