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

from selenium.webdriver.remote.switch_to import SwitchTo
from selenium.webdriver.remote.webdriver import WebDriver

from selene.common.helpers import as_dict, to_by, is_absolute_url
from selene import query
from selene.collection import Collection
from selene.config import Config
from selene.element import Element
from selene.entity import WaitingEntity
from selene.locator import Locator


class Browser(WaitingEntity):
    def __init__(self, config: Config):
        super().__init__(config)

    # todo: consider implement it as context manager too...
    def with_(self, config: Config) -> Browser:
        return Browser(self.config.with_(config))

    def __str__(self):
        return 'browser'

    @property
    def driver(self) -> WebDriver:
        return self.config.driver

    # --- Element builders --- #

    def element(self, css_or_xpath_or_by: Union[str, tuple]) -> Element:
        by = to_by(css_or_xpath_or_by)

        return Element(
            Locator(f'{self}.element({by})',
                    lambda: self.driver.find_element(*by)),
            self.config)

    def all(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        by = to_by(css_or_xpath_or_by)

        return Collection(
            Locator(f'{self}.all({by})',
                    lambda: self.driver.find_elements(*by)),
            self.config)

    # --- High Level Commands--- #

    def open(self, relative_or_absolute_url: str) -> Browser:
        width = self.config.window_width
        height = self.config.window_height

        if width and height:
            self.driver.set_window_size(int(width), int(height))

        is_absolute = is_absolute_url(relative_or_absolute_url)
        base_url = self.config.base_url
        url = relative_or_absolute_url if is_absolute else base_url + relative_or_absolute_url

        self.driver.get(url)
        self.driver.switch_to.window()

        return self

    def switch_to_next_tab(self) -> Browser:
        self.driver.switch_to.window(query.next_tab(self))

        # todo: should we user waiting version here (and in other similar cases)?
        # self.perform(Command(
        #     'open next tab',
        #     lambda browser: browser.driver.switch_to.window(query.next_tab(self))))

        return self

    def switch_to_previous_tab(self) -> Browser:
        self.driver.switch_to.window(query.previous_tab(self))
        return self

    def switch_to_tab(self, index_or_name: Union[int, str]) -> Browser:
        if isinstance(index_or_name, int):
            self.driver.switch_to(query.tab(index_or_name)(self))
        else:
            self.driver.switch_to.window(index_or_name)

        return self

    @property
    def switch_to(self) -> SwitchTo:
        return self.driver.switch_to.alert

    # todo: should we add also a shortcut for self.driver.switch_to.alert ?
    #       if we don't need to switch_to.'back' after switch to alert - then for sure we should...
    #       question is - should we implement our own alert as waiting entity?

    def close_current_tab(self) -> Browser:
        self.driver.close()
        return self

    def quit(self) -> None:
        self.driver.quit()

    def clear_local_storage(self) -> Browser:
        self.driver.execute_script('window.localStorage.clear();') # todo: should we catch and ignore errors?
        return self

    def clear_session_storage(self) -> Browser:
        self.driver.execute_script('window.sessionStorage.clear();')
        return self


# --- Deprecated --- #  todo: remove in future versions


class SeleneDriver(Browser):
    pass

