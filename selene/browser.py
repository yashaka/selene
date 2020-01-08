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

from selene.core.entity import Collection, Element
from selene.core.configuration import Config
from selene.support.shared import config, browser


# todo: just remove this file, once deprecation is totally applied


def driver() -> WebDriver:
    warnings.warn(
        'deprecated; use explicit browser.* style when browser is imported from selene.support.shared',
        DeprecationWarning)

    return browser.config.driver


def quit():
    warnings.warn(
        'deprecated; use explicit browser.* style when browser is imported from selene.support.shared',
        DeprecationWarning)
    browser.quit()


def quit_driver():
    warnings.warn(
        'deprecated; use explicit browser.* style when browser is imported from selene.support.shared',
        DeprecationWarning)
    browser.quit()


def close():
    warnings.warn(
        'deprecated; use explicit browser.* style when browser is imported from selene.support.shared',
        DeprecationWarning)
    browser.close_current_tab()


def set_driver(webdriver: WebDriver):
    warnings.warn(
        'deprecated; use explicit browser.* style when browser is imported from selene.support.shared',
        DeprecationWarning)

    # noinspection PyDataclass
    browser.config.driver = webdriver  # todo: test it


def open(absolute_or_relative_url):
    warnings.warn(
        'deprecated; use explicit browser.* style when browser is imported from selene.support.shared',
        DeprecationWarning)
    return browser.open(absolute_or_relative_url)


def open_url(absolute_or_relative_url):
    warnings.warn(
        'deprecated; use explicit browser.* style when browser is imported from selene.support.shared',
        DeprecationWarning)
    return browser.open(absolute_or_relative_url)


def element(css_or_xpath_or_by: Union[str, tuple]) -> Element:
    warnings.warn(
        'deprecated; use explicit browser.* style when browser is imported from selene.support.shared',
        DeprecationWarning)
    return browser.element(css_or_xpath_or_by)


def elements(css_or_xpath_or_by: Union[str, tuple]) -> Collection:
    warnings.warn(
        'deprecated; use explicit browser.* style when browser is imported from selene.support.shared',
        DeprecationWarning)
    return browser.all(css_or_xpath_or_by)


def all(css_or_xpath_or_by: Union[str, tuple]) -> Collection:
    warnings.warn(
        'deprecated; use explicit browser.* style when browser is imported from selene.support.shared',
        DeprecationWarning)
    return browser.all(css_or_xpath_or_by)


def take_screenshot(path=None, filename=None):
    warnings.warn(
        'deprecated; use explicit browser.* style when browser is imported from selene.support.shared',
        DeprecationWarning)
    if not path:
        path = browser.config.reports_folder
    if not filename:
        id = next(config.counter)
        filename = f'screen_{id}'

    screenshot_path = os.path.join(path, f'{filename}.png')

    folder = os.path.dirname(screenshot_path)
    if not os.path.exists(folder):
        os.makedirs(folder)

    browser.driver.save_screenshot(screenshot_path)

    browser._latest_screenshot = screenshot_path

    return screenshot_path


def latest_screenshot():
    warnings.warn(
        'deprecated; use explicit browser.* style when browser is imported from selene.support.shared',
        DeprecationWarning)
    return browser._latest_screenshot


def wait_to(webdriver_condition, timeout=None, polling=None):
    warnings.warn(
        'deprecated; use explicit browser.* style when browser is imported from selene.support.shared',
        DeprecationWarning)
    tuned_browser = browser if timeout is None else browser.with_(Config(timeout=timeout))

    return tuned_browser.should(webdriver_condition)


def should(webdriver_condition, timeout=None, polling=None):
    warnings.warn(
        'deprecated; use explicit browser.* style when browser is imported from selene.support.shared',
        DeprecationWarning)
    tuned_browser = browser if timeout is None else browser.with_(Config(timeout=timeout))

    return tuned_browser.should(webdriver_condition)


def execute_script(script, *args):
    warnings.warn(
        'deprecated; use explicit browser.* style when browser is imported from selene.support.shared',
        DeprecationWarning)
    return browser.driver.execute_script(script, *args)


def title():
    warnings.warn(
        'deprecated; use explicit browser.* style when browser is imported from selene.support.shared',
        DeprecationWarning)
    return browser.driver.title
