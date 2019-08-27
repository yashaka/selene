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

from selene import config
from selene.conditions import hidden, exist
from selene.support.jquery_style_selectors import s
from tests.acceptance.helpers.helper import get_test_driver

__author__ = 'yashaka'

from selene.browser import *
from tests.acceptance.helpers.todomvc import given_active, given_at_other_page, given_empty_tasks, given, task


def setup_module(m):
    set_driver(get_test_driver())


def teardown_module(m):
    driver().quit()


def test_assure_and_alias_methods():
    given_active("a")
    s("#clear-completed").assure(hidden)
    s("#clear-completed").should(hidden)  # alias
    s("#clear-completed").should_be(hidden)  # alias
    s("#clear-completed").should_have(hidden)  # alias


def test_assure_not_and_alias_methods():
    given_at_other_page()
    s("#new-todo").should_not(exist)
    s("#new-todo").should_not(exist)  # alias
    s("#new-todo").should_not_be(exist)  # alias
    s("#new-todo").should_not_have(exist)  # alias


def test_is_displayed_fails_with_waiting_if_element_not_exist():
    given_at_other_page()
    original_timeout = config.timeout  # todo: switch to something like s("#todo-list").with_timeout(0.1).is_displayed()
    config.timeout = 0.1
    with pytest.raises(TimeoutException):
        s("#todo-list").is_displayed()
    config.timeout = original_timeout


def test_is_displayed_returns_value_with_no_wait_for_visibility():
    given_empty_tasks()
    assert not s("#clear-completed").is_displayed()


def test_is_displayed_returns_true():
    given(task("a"), task("b", is_completed=True))
    assert s("#clear-completed").is_displayed()
