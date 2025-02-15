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

from typing_extensions import Optional, Callable, Sequence

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from selene.core._actions import _Actions
from selene.core._elements import All
from selene.core._elements_context import _ElementsContext
from selene.core.configuration import Config
from selene.core._entity import _WaitingConfiguredEntity
from selene.core._element import Element
from selene.core.locator import Locator


# TODO: should we make it generic on Element and Collection?
# TODO: Client does not need .cached but gets it... :( should we fix it?
class Client(
    _ElementsContext[WebDriver, WebElement, Element, All[Element]],
    _WaitingConfiguredEntity,
):
    def __init__(
        self,
        config: Optional[Config] = None,
        *,
        _Element: Callable[[Locator[WebElement], Config], Element] = Element,
        _All: Callable[
            [
                Locator[Sequence[WebElement]],
                Config,
                Callable[[Locator[WebElement], Config], Element],
            ],
            All[Element],
        ] = All,
        **kwargs,
    ):
        config = (
            Config()
            if (maybe_config := kwargs.get('config', config)) is None
            else maybe_config
        )
        super().__init__(
            locator=Locator('client', lambda: self.config.driver),
            config=config,
            _Element=_Element,
            _All=_All,
            **kwargs,
        )

    # todo: consider adjusting driver size according to config here
    @property
    def driver(self) -> WebDriver:
        return self.config.driver

    @property
    def _actions(self) -> _Actions:
        return _Actions(self.config)

    # --- High Level Commands--- #

    # # TODO: do we need it as part of a most general search context?
    # def open(self, relative_or_absolute_url: Optional[str] = None) -> Context:
    #     # TODO: should we keep it less pretty but more KISS? like:
    #     # self.config._driver_get_url_strategy(self.config)(relative_or_absolute_url)
    #     self.config._executor.get_url(relative_or_absolute_url)
    #
    #     return self
