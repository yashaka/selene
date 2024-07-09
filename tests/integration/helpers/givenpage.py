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

from selenium.webdriver.remote.webdriver import WebDriver

from selene import Browser
from tests import resources
from tests.helpers import convert_sec_to_ms

EMPTY_PAGE_URL = resources.url('empty.html')


class LoadingHtmlPage:
    def __init__(self, timeout=0, body=''):
        self._body = body
        self._timeout = timeout

    def load_in(self, driver_or_browser: WebDriver | Browser):
        driver = (
            driver_or_browser.driver
            if isinstance(driver_or_browser, Browser)
            else driver_or_browser
        )
        (
            driver_or_browser.open(EMPTY_PAGE_URL)
            if isinstance(driver_or_browser, Browser)
            else driver.get(EMPTY_PAGE_URL)
        )
        return LoadedHtmlPage(driver).render_body(self._body, self._timeout)


class LoadedHtmlPage:
    def __init__(self, driver):
        self._driver = driver

    def render_body(self, body, timeout=0):
        self._driver.execute_script(
            'setTimeout(function() { document.getElementsByTagName("body")[0].innerHTML = "'
            + body.replace('\n', ' ').replace('"', '\\"')
            + '";}, '
            + str(convert_sec_to_ms(timeout))
            + ');'
        )
        return self

    def execute_script(self, script):
        self._driver.execute_script(script)
        return self

    def execute_script_with_timeout(self, script, timeout):
        self._driver.execute_script(
            'setTimeout(function() { '
            + script.replace('\n', ' ')
            + ' }, '
            + str(convert_sec_to_ms(timeout))
            + ');'
        )
        return self

    def render_body_with_timeout(self, body, timeout):
        return self.render_body(body, timeout)


class GivenPage:
    def __init__(self, driver_or_browser: WebDriver | Browser):
        self._driver_or_browser = driver_or_browser

    @property
    def _driver(self):
        return (
            self._driver_or_browser.driver
            if isinstance(self._driver_or_browser, Browser)
            else self._driver_or_browser
        )

    def load_body_with_timeout(self, body, timeout):
        return LoadedHtmlPage(self._driver).render_body_with_timeout(body, timeout)

    def opened_with_body_with_timeout(self, body, timeout):
        return LoadingHtmlPage(timeout, body).load_in(self._driver_or_browser)

    def opened_with_body(self, body):
        return self.opened_with_body_with_timeout(body, 0)

    def opened_empty(self):
        return LoadingHtmlPage().load_in(self._driver_or_browser)

    def load_body(self, body):
        return LoadedHtmlPage(self._driver).render_body(body)

    def execute_script_with_timeout(self, script, timeout):
        LoadedHtmlPage(self._driver).execute_script_with_timeout(script, timeout)

    def execute_script(self, script):
        LoadedHtmlPage(self._driver).execute_script(script)

    def add_style_to_head(self, text_node):
        self.execute_script(
            f"""
            var style = document.createElement('style')
            style.appendChild(document.createTextNode(`{text_node}`))
            document.getElementsByTagName('head')[0].appendChild(style)
            """
        )
        return self

    def add_script_to_head(self, text_node):
        self.execute_script(
            f"""
            var script = document.createElement('script')
            script.appendChild(document.createTextNode(`{text_node}`))
            document.getElementsByTagName('head')[0].appendChild(script)
            """
        )
        return self
