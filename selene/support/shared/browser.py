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
import os
import warnings
from functools import lru_cache
from typing import Union, Optional

from selenium.webdriver.remote.webdriver import WebDriver

from selene.common.fp import pipe, identity
from selene.common.helpers import is_absolute_url
from selene.core.entity import Browser, Collection
from selene.core.configuration import Config
from selene.common.none_object import _NoneObject
from selene.core.exceptions import TimeoutException
from selene.core.wait import Wait
from selene.support.shared.config import SharedConfig
from selene.support.webdriver import WebHelper


class SharedBrowser(Browser):
    def __init__(self, config: SharedConfig):
        self._latest_screenshot = _NoneObject(
            'selene.SharedBrowser._latest_screenshot'
        )
        self._latest_page_source = _NoneObject(
            'selene.SharedBrowser._latest_page_source'
        )
        super().__init__(config)

    @property
    def config(self) -> SharedConfig:
        return self._config

    def with_(self, config: Config = None, **config_as_kwargs) -> Browser:
        return SharedBrowser(self.config.with_(config, **config_as_kwargs))

    def open(self, relative_or_absolute_url: str):
        # this -->
        width = self.config.window_width
        height = self.config.window_height

        if width and height:
            self.config.get_or_create_driver().set_window_size(
                int(width), int(height)
            )

        is_absolute = is_absolute_url(relative_or_absolute_url)
        base_url = self.config.base_url
        url = (
            relative_or_absolute_url
            if is_absolute
            else base_url + relative_or_absolute_url
        )
        # <-- part is duplicated,
        # --- originally defined in Browser
        # --- todo: consider refactoring

        self.config.get_or_create_driver().get(url)

        return self

    # --- deprecated --- #

    @property
    def driver(self) -> WebDriver:
        webdriver: WebDriver = self.config.driver

        def return_driver(this) -> WebDriver:
            warnings.warn(
                'deprecated; use `browser.driver` over `browser.driver()`',
                DeprecationWarning,
            )
            return webdriver

        webdriver.__class__.__call__ = return_driver

        return webdriver

    def save_screenshot(self, file: str = None):
        # warnings.warn('browser.save_screenshot might be deprecated', FutureWarning)

        if not file:
            file = self.config.generate_filename(suffix='.png')
        if file and not file.lower().endswith('.png'):
            file = os.path.join(file, f'{next(self.config.counter)}.png')
        folder = os.path.dirname(file)
        if not os.path.exists(folder) and folder:
            os.makedirs(folder)
        # todo: refactor to catch errors smartly in get_screenshot_as_file. or not needed?
        self.config.last_screenshot = WebHelper(self.driver).save_screenshot(
            file
        )

        return self.config.last_screenshot

    @property
    def last_screenshot(self) -> str:
        return self.config.last_screenshot

    @property
    def latest_screenshot(self) -> str:
        warnings.warn(
            'deprecated, use browser.last_screenshot property',
            DeprecationWarning,
        )

        class CallableString(str):
            def __new__(cls, value):
                obj = str.__new__(cls, value)
                obj._value = value
                return obj

            def __call__(self, *args, **kwargs):
                warnings.warn(
                    'browser.latest_screenshot() is deprecated, '
                    'use browser.last_screenshot as a property. ',
                    DeprecationWarning,
                )
                return self[:]

            def __bool__(self):
                return bool(self._value)

        return CallableString(self.last_screenshot)

    # todo: consider moving this to browser command.save_page_source(filename)
    def save_page_source(self, file: str = None) -> Optional[str]:
        # warnings.warn('browser.save_page_source(file) might be deprecated in future', FutureWarning)

        if not file:
            file = self.config.generate_filename(suffix='.html')

        saved_file = WebHelper(self.driver).save_page_source(file)

        self.config.last_page_source = saved_file

        return saved_file

    @property
    def last_page_source(self) -> str:
        return self.config.last_page_source

    @property
    def latest_page_source(self):
        warnings.warn(
            'browser.latest_page_source prop is deprecated, use browser.last_page_source',
            DeprecationWarning,
        )
        return self.config.last_page_source

    def quit(self) -> None:
        self.config.reset_driver()

    def quit_driver(self):
        warnings.warn(
            'deprecated; use browser.quit() instead', DeprecationWarning
        )
        self.quit()

    def close(self):
        warnings.warn(
            'deprecated; use browser.close_current_tab() instead',
            DeprecationWarning,
        )
        self.close_current_tab()

    def set_driver(self, webdriver: WebDriver):
        warnings.warn(
            'use config.driver = webdriver '
            'or '
            'config.set_driver = lambda: webdriver '
            'instead',
            DeprecationWarning,
        )

        # noinspection PyDataclass
        self.config.driver = webdriver  # todo: test it

    def open_url(self, absolute_or_relative_url):
        warnings.warn(
            'use browser.open instead of browser.open_url or open_url',
            DeprecationWarning,
        )
        return self.open(absolute_or_relative_url)

    def elements(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        warnings.warn(
            'use browser.all instead of browser.elements or elements',
            DeprecationWarning,
        )
        return self.all(css_or_xpath_or_by)

    def wait_to(self, webdriver_condition, timeout=None, polling=None):
        warnings.warn(
            'use browser.should instead of browser.wait_to or wait_to',
            DeprecationWarning,
        )
        tuned_self = (
            self if timeout is None else self.with_(Config(timeout=timeout))
        )

        return tuned_self.should(webdriver_condition)

    def execute_script(self, script, *args):
        warnings.warn(
            'use browser.driver.execute_script instead of execute_script',
            DeprecationWarning,
        )
        return self.driver.execute_script(script, *args)

    def title(self):
        warnings.warn(
            'use browser.driver.title or browser.get(query.title) instead',
            DeprecationWarning,
        )
        return self.driver.title

    def take_screenshot(self, path=None, filename=None):
        warnings.warn(
            'deprecated; use browser.save_screenshot(filename) instead',
            DeprecationWarning,
        )
        return self.save_screenshot(
            os.path.join(path, filename)
            if path and filename
            else filename or path
        )
