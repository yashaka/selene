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

import typing_extensions as typing
from typing_extensions import Callable, Union, Tuple, TypeVar

from selene.core._entity import _Entity, _CachedLocatableEntity, _ConfiguredEntity
from selene.core.configuration import Config
from selene.core.locator import Locator

E = TypeVar('E', bound=_Entity)
A = TypeVar('A')
W = TypeVar('W')


@typing.runtime_checkable
class _SearchContext(typing.Protocol[W]):
    def find_element(self, by: str, value: str | None = None) -> W: ...

    def find_elements(self, by: str, value: str | None = None) -> typing.List[W]: ...


SC = TypeVar('SC', bound=_SearchContext)
"""Reflects Search Context, e.g. WebDriver"""
SR = TypeVar('SR', bound=_SearchContext)
"""Reflects Search Result, e.g. WebElement"""


# TODO: won't it work also for Browser? – probably yes...
# todo: should we rename it to at least _LocatableElementsContext?
#       probably no, because it's not possible to have "non-locatable" version...
class _ElementsContext(
    _CachedLocatableEntity[SC],
    _ConfiguredEntity,
    typing.Generic[SC, SR, E, A],
):
    """An Elements-root-like class that serves as pure context to "describe" its
    relatively locatable elements via `element(selector_or_by)` or
    `all(selector_or_by)` methods"""

    def __init__(
        self,
        *,
        locator: Locator[SC],
        config: Config,
        _Element: Callable[[Locator[SR], Config], E],
        _All: Callable[
            [
                Locator[typing.Sequence[SR]],
                Config,
                Callable[[Locator[SR], Config], E],
            ],
            A,
        ],
        **kwargs,
    ):
        super().__init__(
            locator=locator,
            config=config,
            _Element=_Element,
            _All=_All,
            **kwargs,
        )
        self._Element = _Element
        self._All = _All

    # TODO: consider None by default,
    #       and *args, **kwargs to be able to pass custom things
    #       to be processed by config.location_strategy
    #       and by default process none as "element to skip all actions on it"
    #       see examples in Device.element|all implementations
    def element(
        self,
        selector_or_by_or_locator: Union[str, Tuple[str, str], Locator[SR]],
        /,
    ) -> E:

        if isinstance(selector_or_by_or_locator, Locator):
            locator = selector_or_by_or_locator
            return self._Element(
                locator,
                self.config,
            )
        selector_or_by = selector_or_by_or_locator

        by = self.config._selector_or_by_to_by(selector_or_by)

        return self._Element(
            Locator(
                f'{self}.element({by})',
                lambda: self.locate().find_element(*by),
            ),
            self.config,
        )

    def all(
        self,
        selector_or_by_or_locator: Union[
            str, Tuple[str, str], Locator[typing.Sequence[SR]]
        ],
        /,
    ) -> A:

        if isinstance(selector_or_by_or_locator, Locator):
            locator = selector_or_by_or_locator
            return self._All(
                locator,
                self.config,
                self._Element,
            )
        selector_or_by = selector_or_by_or_locator

        by = self.config._selector_or_by_to_by(selector_or_by)

        return self._All(
            Locator(
                f'{self}.all({by})',
                lambda: self.locate().find_elements(*by),
            ),
            self.config,
            self._Element,
        )
