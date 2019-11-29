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

from selenium.webdriver import ActionChains
from selenium.webdriver.android.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from selene.common.helpers import as_dict
from selene.new import command
from selene.new.config import Config
from selene.new.entity import WaitingEntity
from selene.new.locator import Locator
from selene.new.wait import Command


class Element(WaitingEntity):

    # todo: should we move locator based init and with_ to Located base abstract class?

    def __init__(self, locator: Locator[WebElement], config: Config):
        self._locator = locator
        super().__init__(config)

    def with_(self, config: Config) -> Element:
        return Element(self._locator, Config(**{**as_dict(self.config), **config}))

    def __str__(self):
        return str(self._locator)

    def __call__(self) -> WebElement:
        return self._locator()

    # --- Commands --- #

    def execute_script(self, script_on_self: str, *extra_args):
        driver: WebDriver = self.config.driver
        webelement = self()
        # todo: should we wrap it in wait or not?
        return driver.execute_script(script_on_self, webelement, *extra_args)

    def set_value(self, value: Union[str, int]) -> Element:
        # todo: should we move all commands like following or queries like in conditions - to separate py modules?
        # todo: should we make them webelement based (Callable[[WebElement], None]) instead of element based?
        def fn(element: Element):
            webelement = element()
            webelement.clear()  # todo: change to impl based not on clear, because clear generates post-events...
            webelement.send_keys(str(value))

        self.wait.for_(command.js.set_value(value) if self.config.set_value_by_js
                       else Command(f'set value: {value}', fn))

        return self

    def type(self, keys: Union[str, int]) -> Element:
        def fn(element: Element):
            webelement = element()
            webelement.send_keys(str(keys))

        self.wait.for_(command.js.type(keys) if self.config.type_by_js
                          else Command(f'type: {keys}', fn))

        return self

    def press_enter(self) -> Element:
        return self.type(Keys.ENTER)

    def press_escape(self) -> Element:
        return self.type(Keys.ESCAPE)

    def press_tab(self) -> Element:
        return self.type(Keys.TAB)

    def clear(self) -> Element:
        self.wait.command('clear', lambda element: element().clear())
        return self

    # todo: do we need config.click_by_js?
    # todo: add offset args with defaults, or add additional method, think on what is better
    def click(self) -> Element:
        """Just a normal click:)

        You might ask, why don't we have config.click_by_js?
        Because making all clicks js based is not a "normal case".
        You might need to speed up all "set value" in your tests, but command.js.click will not speed up anything.
        Yet, sometimes, it might be useful as workaround.
        In such cases - use

            element.perform(command.js.click)

        to achieve the goal in less concise way,
        thus, identifying by this "awkwardness" that it is really a workaround;)
        """
        self.wait.command('click', lambda element: element().click())
        return self

    def double_click(self) -> Element:
        actions: ActionChains = ActionChains(self.config.driver)
        self.wait.command('double click', lambda element: actions.double_click(element()).perform())
        return self

    def context_click(self) -> Element:
        actions: ActionChains = ActionChains(self.config.driver)
        self.wait.command('context click', lambda element: actions.context_click(element()).perform())
        return self

    def hover(self) -> Element:
        actions: ActionChains = ActionChains(self.config.driver)
        self.wait.command('hover', lambda element: actions.move_to_element(element()).perform())
        return self

    # todo: should we reflect queries as self methods? or not...
    # pros: faster to query element attributes
    # cons: queries are not test oriented. test is steps + asserts
    #       so queries will be used only occasionally, then why to make a heap from Element?
    #       hence, occasionally it's enough to have them called as
    #           query.outer_html(element)  # non-waiting version
    #       or
    #           element.get(query.outer_html)  # waiting version
    # def outer_html(self) -> str:
    #     return self.wait.for_(query.outer_html)


class SeleneElement(Element):  # todo: consider deprecating this name
    pass
