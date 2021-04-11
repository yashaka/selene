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
__author__ = 'yashaka'

from selene import be
from selene.support.conditions.be import hidden, existing
from selene.support.shared import browser
from tests.acceptance.helpers.helper import get_test_driver
from tests.acceptance.helpers.todomvc import (
    given_active,
    given_at_other_page,
    given_empty_tasks,
    given,
    task,
)


def setup_module():
    browser.set_driver(get_test_driver())


def teardown_module():
    browser.quit()


def test_assure_and_alias_methods():
    given_active("a")
    browser.element("#clear-completed").assure(be.hidden)
    browser.element("#clear-completed").should(be.hidden)  # alias
    browser.element("#clear-completed").should_be(hidden)  # alias
    browser.element("#clear-completed").should_have(hidden)  # alias


def test_assure_not_and_alias_methods():
    given_at_other_page()
    browser.element("#new-todo").should(be.not_.existing)
    browser.element("#new-todo").should_not(existing)  # alias
    browser.element("#new-todo").should_not_be(existing)  # alias
    browser.element("#new-todo").should_not_have(existing)  # alias


def test_is_displayed_returns_value_with_no_wait_for_visibility():
    given_empty_tasks()
    assert not browser.element("#clear-completed").is_displayed()


def test_is_displayed_returns_true():
    given(task("a"), task("b", is_completed=True))
    assert browser.element("#clear-completed").is_displayed()
