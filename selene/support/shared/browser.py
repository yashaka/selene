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
import os
import warnings
from typing import Union

from selenium.webdriver.remote.webdriver import WebDriver

from selene.core.entity import Browser, Collection
from selene.core.configuration import Config
from selene.common.none_object import NoneObject
from selene.support.shared.config import SharedConfig
from selene.support.shared import config


class SharedBrowser(Browser):
    def __init__(self, config: SharedConfig):
        self._latest_screenshot = NoneObject('selene.SharedBrowser._latest_screenshot')
        super().__init__(config)

    @property
    def config(self) -> SharedConfig:
        return self._config

    def with_(self, config: Config = None, **config_as_kwargs) -> Browser:
        return Browser(self.config.with_(config, **config_as_kwargs))

    # --- deprecated --- #

    @property
    def driver(self) -> WebDriver:
        webdriver: WebDriver = self.config.driver

        def return_driver(this) -> WebDriver:
            warnings.warn('deprecated; use `browser.driver` over `browser.driver()`', DeprecationWarning)
            return webdriver

        webdriver.__class__.__call__ = return_driver

        return webdriver

    def quit_driver(self):
        warnings.warn('deprecated; use browser.quit() instead', DeprecationWarning)
        self.quit()

    def close(self):
        warnings.warn('deprecated; use browser.close_current_tab() instead', DeprecationWarning)
        self.close_current_tab()

    def set_driver(self, webdriver: WebDriver):
        warnings.warn('use config.driver = webdriver instead', DeprecationWarning)

        # noinspection PyDataclass
        self.config.driver = webdriver  # todo: test it

    def open_url(self, absolute_or_relative_url):
        warnings.warn('use browser.open = webdriver instead', DeprecationWarning)
        return self.open(absolute_or_relative_url)

    def elements(self, css_or_xpath_or_by: Union[str, tuple]) -> Collection:
        warnings.warn('use browser.all instead', DeprecationWarning)
        return self.all(css_or_xpath_or_by)

    def take_screenshot(self, path=None, filename=None):
        warnings.warn('might be deprecated', PendingDeprecationWarning)
        if not path:
            path = self.config.reports_folder
        if not filename:
            id = next(config.counter)
            filename = f'screen_{id}'

        screenshot_path = os.path.join(path,f'{filename}.png')

        folder = os.path.dirname(screenshot_path)
        if not os.path.exists(folder):
            os.makedirs(folder)

        self.driver.save_screenshot(screenshot_path)

        self._latest_screenshot = screenshot_path

        return screenshot_path

    def latest_screenshot(self):
        warnings.warn('might be deprecated', PendingDeprecationWarning)
        return self._latest_screenshot

    def wait_to(self, webdriver_condition, timeout=None, polling=None):
        warnings.warn('use browser.should instead', DeprecationWarning)
        tuned_self = self if timeout is None else self.with_(Config(timeout=timeout))

        return tuned_self.should(webdriver_condition)

    def execute_script(self, script, *args):
        warnings.warn('use browser.driver.execute_script instead', DeprecationWarning)
        return self.driver.execute_script(script, *args)

    def title(self):
        warnings.warn('use browser.driver.title or browser.get(query.title) instead', DeprecationWarning)
        return self.driver.title