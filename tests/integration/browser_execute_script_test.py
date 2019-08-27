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

import logging
import os

from selene import config
from selene import browser
from selene.support.jquery_style_selectors import s

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'


def setup_module(m):
    config.browser_name = "chrome"


def test_can_scroll_to_via_js():
    browser.open_url(start_page)
    # logging.warning(browser.driver().current_url)
    # browser.driver().set_window_size(300, 400)
    link = s("#invisible_link")
    # browser.driver().execute_script("arguments[0].scrollIntoView();", link)
    # - this code does not work because SeleneElement is not JSON serializable, and I don't know the way to fix it
    #   - because all available in python options needs a change to json.dumps call - adding a second parameter to it
    #     and specify a custom encoder, but we can't change this call inside selenium webdriver implementation
    browser.driver().execute_script("arguments[0].scrollIntoView();", link.get_actual_webelement())
    link.click()
    assert "header" in browser.driver().current_url
