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

import pytest
from selenium.common.exceptions import TimeoutException

from selene.browser import *
from selene.support.conditions import have
from selene.support.jquery_style_selectors import ss
from tests.acceptance.helpers.helper import get_test_driver
from tests.acceptance.helpers.todomvc import given_active


def setup_module(m):
    set_driver(get_test_driver())


def teardown_module(m):
    driver().quit()


def test_should_passes():
    given_active("a", "b")
    ss("#todo-list>li").should(have.exact_texts("a", "b"))


def test_should_fails():
    given_active("a", "b")
    with pytest.raises(TimeoutException):
        ss("#todo-list>li").should(have.exact_texts("a.", "b."), timeout=0.1)
