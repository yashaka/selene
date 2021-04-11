# MIT License
#
# Copyright (c) 2015-2021 Iakiv Kramarenko
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

EMPTY_PAGE_URL = (
    'file://'
    + os.path.abspath(os.path.dirname(__file__))
    + '/../../resources/empty.html'
)


class LoadingHtmlPage(object):
    def __init__(self, timeout=0, body=''):
        self._body = body
        self._timeout = timeout

    def load_in(self, driver):
        driver.get(EMPTY_PAGE_URL)
        return LoadedHtmlPage(driver).render_body(self._body, self._timeout)


class LoadedHtmlPage(object):
    def __init__(self, driver):
        self._driver = driver

    def render_body(self, body, timeout=0):
        self._driver.execute_script(
            'setTimeout(function() { document.getElementsByTagName("body")[0].innerHTML = "'
            + body.replace('\n', ' ').replace('"', '\\"')
            + '";}, '
            + str(timeout)
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
            + str(timeout)
            + ');'
        )
        return self

    def render_body_with_timeout(self, body, timeout):
        return self.render_body(body, timeout)


class GivenPage(object):
    def __init__(self, driver):
        self._driver = driver

    def load_body_with_timeout(self, body, timeout):
        return LoadedHtmlPage(self._driver).render_body_with_timeout(
            body, timeout
        )

    def opened_with_body_with_timeout(self, body, timeout):
        return LoadingHtmlPage(timeout, body).load_in(self._driver)

    def opened_with_body(self, body):
        return self.opened_with_body_with_timeout(body, 0)

    def opened_empty(self):
        return LoadingHtmlPage().load_in(self._driver)

    def load_body(self, body):
        return LoadedHtmlPage(self._driver).render_body(body)

    def execute_script_with_timeout(self, script, timeout):
        LoadedHtmlPage(self._driver).execute_script_with_timeout(
            script, timeout
        )
