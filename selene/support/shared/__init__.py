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

import functools
import os
import warnings

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver

from selene.core.configuration import Hooks, WaitHooks
from selene.support.shared.browser import SharedBrowser
from selene.support.shared.config import SharedConfig

config = SharedConfig()


def _take_screenshot():
    path = config.reports_folder
    next_id = next(config.counter)
    filename = f'screen_{next_id}'
    driver = config.driver
    screenshot_path = os.path.join(path, f'{filename}.png')
    folder = os.path.dirname(screenshot_path)

    if not os.path.exists(folder):
        os.makedirs(folder)

    # todo: refactor to catch errors smartly in get_screenshot_as_file
    return screenshot_path if driver.get_screenshot_as_file(screenshot_path) else 'None'


def _save_and_log_screenshot(error: TimeoutException) -> Exception:
    path = _take_screenshot()
    return TimeoutException(
        error.msg + f'''
Screenshot: file://{path}''',
        error.screen,
        error.stacktrace)


def _take_html_dump():
    path = config.reports_folder
    next_id = next(config.counter)
    filename = f'source_{next_id}'
    driver: WebDriver = config.driver
    page_source_path = os.path.join(path, f'{filename}.html')
    folder = os.path.dirname(page_source_path)

    if not os.path.exists(folder):
        os.makedirs(folder)

    # todo: refactor to catch errors smartly in get_screenshot_as_file

    # todo: consider moving this to browser query._page_source_as_file(filename)
    def _get_page_source_as_file(filename) -> bool:
        if not filename.lower().endswith('.html'):
            warnings.warn("name used for saved pagesource does not match file "
                          "type. It should end with an `.html` extension", UserWarning)

        html = driver.page_source
        try:
            with open(filename, 'w') as f:
                f.write(html)
        except IOError:
            return False
        finally:
            del html
        return True

    return page_source_path if _get_page_source_as_file(page_source_path) else 'None'


def _save_and_log_html_dump(error: TimeoutException) -> Exception:
    path = _take_html_dump()
    return TimeoutException(
        error.msg + f'''
Page Source: file://{path}''',
        error.screen,
        error.stacktrace)


def _compose(*functions):
    return functools.reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)


# todo: consider more flat style: Hooks(wait_failure=_save_and_log_screenshot)
# todo: consider making screenshots configurable (turn on/off)
config.hooks = Hooks(wait=WaitHooks(failure=_compose(
    _save_and_log_html_dump,
    _save_and_log_screenshot)))

browser = SharedBrowser(config)
