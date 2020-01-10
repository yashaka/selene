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

from selene.common.fp import pipe
from selene.core.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver

from selene.support.shared.browser import SharedBrowser
from selene.support.shared.config import SharedConfig

config = SharedConfig()

browser = SharedBrowser(config)


def _save_and_log_screenshot(error: TimeoutException) -> Exception:
    path = browser.save_screenshot()
    return TimeoutException(error.msg + f'''
Screenshot: file://{path}''')


def _save_and_log_page_source(error: TimeoutException) -> Exception:
    filename = browser.latest_screenshot.replace('.png', '.html') if browser.latest_screenshot else None
    path = browser.save_page_source(filename)
    return TimeoutException(error.msg + f'''
PageSource: file://{path}''')


# todo: consider making screenshots configurable (turn on/off)
config.hook_wait_failure = pipe(
    _save_and_log_screenshot,
    _save_and_log_page_source
)
