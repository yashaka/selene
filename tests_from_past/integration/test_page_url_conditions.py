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

import pytest
from selenium.common.exceptions import TimeoutException

from selene.support.past import config
from selene.support.past.conditions import url, url_containing
from selene.support.past.browser import open_url, driver
from selene.support.past.browser import wait_to

start_page = 'file://' + os.path.abspath(os.path.dirname(__file__)) + '/../resources/start_page.html'


original_timeout = config.timeout


def setup_module(m):
    config.browser_name = "chrome"


def teardown_function(f):
    config.timeout = original_timeout


def test_can_wait_for_exact_url():
    open_url(start_page)
    wait_to(url(driver().current_url))


def test_can_wait_for_part_of_url():
    open_url(start_page)
    wait_to(url_containing("start_page.html"))


def test_should_wait_and_fail_for_incorrect_url():
    config.timeout = 0.1
    with pytest.raises(TimeoutException):
        open_url(start_page)
        wait_to(url("xttp:/"))
