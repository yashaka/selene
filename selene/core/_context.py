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

from typing import Optional, Union, Tuple

from selenium.webdriver.remote.webdriver import WebDriver

from selene.core._actions import _Actions
from selene.core.configuration import Config
from selene.core.entity import WaitingEntity, Element, Collection
from selene.core.locator import Locator


# TODO: reconsider naming it as Context, because seems like our Config - is more context than something else
# TODO: add _context.pyi
# TODO: should we make it generic on Element and Collection?
class Context(WaitingEntity['Context']):
    def __init__(self, config: Optional[Config] = None):
        config = Config() if config is None else config
        super().__init__(config)

    def with_(self, config: Optional[Config] = None, **config_as_kwargs) -> Context:
        return (
            Context(config)
            if config
            else Context(self.config.with_(**config_as_kwargs))
        )

    def __str__(self):
        return 'context'

    # todo: consider not just building driver but also adjust its size according to config
    @property
    def driver(self) -> WebDriver:
        return self.config.driver

    # TODO: consider making it callable (self.__call__() to be shortcut to self.__raw__ ...)

    @property
    def __raw__(self):
        return self.config.driver

    @property
    def _actions(self) -> _Actions:
        return _Actions(self.config)

    # --- Element builders --- #

    # TODO: consider None by default,
    #       and *args, **kwargs to be able to pass custom things
    #       to be processed by config.location_strategy
    #       and by default process none as "element to skip all actions on it"
    def element(
        self, css_or_xpath_or_by: Union[str, Tuple[str, str], Locator]
    ) -> Element:
        if isinstance(css_or_xpath_or_by, Locator):
            return Element(css_or_xpath_or_by, self.config)

        by = self.config._selector_or_by_to_by(css_or_xpath_or_by)
        # todo: do we need by_to_locator_strategy?

        return Element(
            Locator(f'{self}.element({by})', lambda: self.driver.find_element(*by)),
            self.config,
        )

    def all(
        self, css_or_xpath_or_by: Union[str, Tuple[str, str], Locator]
    ) -> Collection:
        if isinstance(css_or_xpath_or_by, Locator):
            return Collection(css_or_xpath_or_by, self.config)

        by = self.config._selector_or_by_to_by(css_or_xpath_or_by)

        return Collection(
            Locator(f'{self}.all({by})', lambda: self.driver.find_elements(*by)),
            self.config,
        )

    # --- High Level Commands--- #

    # # TODO: do we need it as part of a most general search context?
    # def open(self, relative_or_absolute_url: Optional[str] = None) -> Context:
    #     # TODO: should we keep it less pretty but more KISS? like:
    #     # self.config._driver_get_url_strategy(self.config)(relative_or_absolute_url)
    #     self.config._executor.get_url(relative_or_absolute_url)
    #
    #     return self
