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

import warnings
from typing import Optional, Union, Tuple

from selenium.webdriver.remote.switch_to import SwitchTo
from selenium.webdriver.remote.webdriver import WebDriver

from selene.core._actions import _Actions
from selene.core.configuration import Config
from selene.core.entity import WaitingEntity, Element, Collection
from selene.core.locator import Locator
from selene.support.webdriver import WebHelper


class Browser(WaitingEntity['Browser']):
    def __init__(self, config: Optional[Config] = None):
        config = Config() if config is None else config
        super().__init__(config)

    def with_(self, config: Optional[Config] = None, **config_as_kwargs) -> Browser:
        return (
            Browser(config)
            if config
            else Browser(self.config.with_(**config_as_kwargs))
        )

    def __str__(self):
        return 'browser'

    # todo: consider not just building driver but also adjust its size according to config
    @property
    def driver(self) -> WebDriver:
        return self.config.driver

    # TODO: consider making it callable (self.__call__() to be shortcut to self.__raw__ ...)

    @property
    def __raw__(self):
        return self.config.driver

    # @property
    # def actions(self) -> ActionChains:
    #     """
    #     It's kind of just a shortcut for pretty low level actions from selenium webdriver
    #     Yet unsure about this property here:)
    #     comparing to usual high level Selene API...
    #     Maybe later it would be better to make own Actions with selene-style retries, etc.
    #     """
    #     return ActionChains(self.config.driver)

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

    def open(self, relative_or_absolute_url: Optional[str] = None) -> Browser:
        # TODO: should we keep it less pretty but more KISS? like:
        # self.config._driver_get_url_strategy(self.config)(relative_or_absolute_url)
        self.config._executor.get_url(relative_or_absolute_url)

        return self

    # TODO: should we deprecate all switch_to_* methods?
    def switch_to_next_tab(self) -> Browser:
        from selene.core import query

        self.driver.switch_to.window(query.next_tab(self))

        # TODO: should we use waiting version here (and in other similar cases)?
        # self.perform(Command(
        #     'open next tab',
        #     lambda browser: browser.driver.switch_to.window(query.next_tab(self))))

        return self

    def switch_to_previous_tab(self) -> Browser:
        from selene.core import query

        self.driver.switch_to.window(query.previous_tab(self))
        return self

    def switch_to_tab(self, index_or_name: Union[int, str]) -> Browser:
        if isinstance(index_or_name, int):
            index = index_or_name
            from selene.core import query

            self.driver.switch_to.window(query.tab(index)(self))
        else:
            self.driver.switch_to.window(index_or_name)

        return self

    # TODO: consider deprecating
    @property
    def switch_to(self) -> SwitchTo:
        return self.driver.switch_to

    # TODO: should we add also a shortcut for self.driver.switch_to.alert ?
    #       if we don't need to switch_to.'back' after switch to alert - then for sure we should...
    #       question is - should we implement our own alert as waiting entity?

    def quit(self) -> None:
        """
        Quits the driver.

        If the driver was not even set, will build it just to quit it:D.

        Will fail if the driver was already quit or crashed.
        """
        self.driver.quit()

    # TODO: consider deprecating, it does not close browser, it closes current tab/window
    def close(self) -> Browser:
        self.driver.close()
        return self

    # --- Deprecated --- #

    # TODO: should we keep it?
    def execute_script(self, script, *args):
        warnings.warn(
            'consider using browser.driver.execute_script '
            'instead of browser.execute_script',
            PendingDeprecationWarning,
        )
        return self.driver.execute_script(script, *args)

    # TODO: should we move it to query.* and/or command.*?
    #       like `browser.get(query.screenshot)` ?
    #       like `browser.perform(command.save_screenshot)` ?
    # TODO: deprecate file name, use path
    #       because we can path folder path not file path and it will work
    def save_screenshot(self, file: Optional[str] = None):
        warnings.warn(
            'browser.save_screenshot is deprecated, '
            'use browser.get(query.screenshot_saved())',
            DeprecationWarning,
        )

        from selene.core import query  # type: ignore

        return self.get(query.screenshot_saved())  # type: ignore

    @property
    def last_screenshot(self) -> str:
        warnings.warn(
            'browser.last_screenshot is deprecated, '
            'use browser.config.last_screenshot',
            DeprecationWarning,
        )
        return self.config.last_screenshot  # type: ignore

    def save_page_source(self, file: Optional[str] = None) -> Optional[str]:
        warnings.warn(
            'browser.save_page_source is deprecated, '
            'use browser.get(query.page_source_saved())',
            DeprecationWarning,
        )

        if file is None:
            file = self.config._generate_filename(suffix='.html')  # type: ignore

        saved_file = WebHelper(self.driver).save_page_source(file)

        self.config.last_page_source = saved_file  # type: ignore

        return saved_file

    @property
    def last_page_source(self) -> str:
        warnings.warn(
            'browser.last_page_source is deprecated, '
            'use browser.config.last_page_source',
            DeprecationWarning,
        )
        return self.config.last_page_source  # type: ignore

    def close_current_tab(self) -> Browser:
        warnings.warn(
            'deprecated because the «tab» term is not relevant for mobile; '
            'use a `browser.close()` or `browser.driver.close()` instead',
            DeprecationWarning,
        )
        self.driver.close()
        return self

    def clear_local_storage(self) -> Browser:
        warnings.warn(
            'deprecated because of js nature and not-relevance for mobile; '
            'use `browser.perform(command.js.clear_local_storage)` instead',
            DeprecationWarning,
        )
        from selene.core import command

        self.perform(command.js.clear_local_storage)
        return self

    def clear_session_storage(self) -> Browser:
        warnings.warn(
            'deprecated because of js nature and not-relevance for mobile; '
            'use `browser.perform(command.js.clear_session_storage)` instead',
            DeprecationWarning,
        )
        from selene.core import command

        self.perform(command.js.clear_session_storage)
        return self
