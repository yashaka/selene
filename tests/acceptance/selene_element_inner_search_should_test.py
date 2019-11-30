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

from selene.support.conditions import have
from selene.support.past.support.jquery_style_selectors import s
from tests.acceptance.helpers.helper import get_test_driver

__author__ = 'yashaka'

from selene.support.past.browser import *
from tests.acceptance.helpers.todomvc import given_active


def setup_module(m):
    set_driver(get_test_driver())


def teardown_module(m):
    driver().quit()


def test_search_inner_selement():
    given_active("a", "b")
    s("#todo-list").s("li").should(have.exact_text("a"))


def test_search_inner_selene_collection():
    given_active("a", "b")
    s("#todo-list").all("li").should(have.exact_texts("a", "b"))
