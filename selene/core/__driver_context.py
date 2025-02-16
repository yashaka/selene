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

from typing_extensions import Optional, Callable, Sequence, TypeVar, Generic

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from selene.core._actions import _Actions
from selene.core._elements import All
from selene.core._elements_context import _ElementsContext, _SearchContext
from selene.core.configuration import Config
from selene.core._entity import _DriverEntity, _Entity, _WaitingConfiguredEntity
from selene.core._element import Element
from selene.core.locator import Locator

# TODO: does not work... do we even need it? isn't _DriverEntity enough?

EC = TypeVar('EC', bound=_ElementsContext)
A = TypeVar('A')
SC = TypeVar('SC', bound=WebDriver)  # , default=WebDriver)
"""Reflects Search Context, e.g. WebDriver"""
SR = TypeVar('SR', bound=WebElement)  # , default=WebElement)
"""Reflects Search Result, e.g. WebElement"""


# TODO: Should we name it _drived_context.DrivedContext?
#       technically... config is so far also driver-based
#       thus, any _ConfiguredEntity sub-class is drived out of the box
#       so, maybe DriverContext is still a better way...
# TODO: should we make it generic on Element and Collection?
# TODO: de we need a one generic base class for all client-like classes?
#       so we can build corresponding queries/commands/conditions based on them?
#       because currently we have to use something
#       that will accept also elements...
#       i.e. allowing something like
#       element.perform(command.switch_to_next_tab) o_O
# TODO: Client does not need .cached but gets it... :( should we fix it?
class __DriverContext(
    _ElementsContext[SC, SR, EC, A],
    _WaitingConfiguredEntity,
    _DriverEntity,
    Generic[EC, A, SC, SR],
    # Generic[EC, A, SC, SR],
):
    def __init__(
        self,
        config: Optional[Config] = None,
        *,
        _Element: Callable[[Locator[SR], Config], EC],
        _All: Callable[
            [
                Locator[Sequence[SR]],
                Config,
                Callable[[Locator[SR], Config], EC],
            ],
            A,
        ],
        **kwargs,
    ):
        config = (
            Config()
            if (maybe_config := kwargs.get('config', config)) is None
            else maybe_config
        )

        super().__init__(
            locator=Locator('context', lambda: self.config.driver),  # type: ignore
            config=config,
            _Element=_Element,
            _All=_All,
            **kwargs,
        )

    @property
    def _actions(self) -> _Actions:
        return _Actions(self.config)
