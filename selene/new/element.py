# MIT License
#
# Copyright (c) 2015-2019 Iakiv Kramarenko
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

from typing import Union

from selenium.webdriver.remote.webelement import WebElement

from selene.common.helpers import as_dict
from selene.new.config import Config
from selene.new.entity import WaitingEntity
from selene.new.locators import Locator


class Element(WaitingEntity):
    def __init__(self, locator: Locator[WebElement], config: Config):
        self._locator = locator
        super().__init__(config)

    def with_(self, config: Config):
        return Element(self._locator, Config(**{**as_dict(self.config), **config}))

    def __str__(self):
        return str(self._locator)

    def __call__(self) -> WebElement:
        return self._locator.find()

    # --- Commands --- #

    def set_value(self, value: Union[str, int]) -> Element:
        def fn(element: Element):
            webelement = element()
            webelement.clear()  # todo: change to impl based not on clear, because clear generates post-events...
            webelement.send_keys(str(value))

        fn.__str__ = lambda: f'set value: {value}'  # todo: refactor to pass description in wait.command

        self.wait.command(fn if self.config.set_value_by_js
                          else fn)  # todo: change to jsCommand

        return self

    def type(self, keys: Union[str, int]) -> Element:
        def fn(element: Element):
            webelement = element()
            webelement.send_keys(str(keys))

        fn.__str__ = lambda: f'type: {keys}'

        self.wait.command(fn if self.config.type_by_js
                          else fn)  # todo: change to jsCommand

        return self


SeleneElement = Element  # todo: consider deprecating this name
