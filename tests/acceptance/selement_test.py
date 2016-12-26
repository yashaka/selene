import pytest
from selenium.common.exceptions import TimeoutException

from selene.conditions import hidden, exist

__author__ = 'yashaka'

from selenium import webdriver

from selene.tools import *
from tests.acceptance.helpers.todomvc import given_active, given_at_other_page, given_empty_tasks, given, task


def setup_module(m):
    set_driver(webdriver.Firefox())


def teardown_module(m):
    get_driver().quit()


def test_assure_and_alias_methods():
    given_active("a")
    s("#clear-completed").assure(hidden)
    s("#clear-completed").insist(hidden)  # alias
    s("#clear-completed").should(hidden)  # alias
    s("#clear-completed").should_be(hidden)  # alias
    s("#clear-completed").should_have(hidden)  # alias


def test_assure_not_and_alias_methods():
    given_at_other_page()
    s("#new-todo").should_not(exist)
    s("#new-todo").insist_not(exist)  # alias
    s("#new-todo").should_not(exist)  # alias
    s("#new-todo").should_not_be(exist)  # alias
    s("#new-todo").should_not_have(exist)  # alias


def test_lazy_inner_s():
    given_at_other_page()
    s("#todo-list>li:nth-of-type(1)").s(".toggle")
    s("#todo-list>li:nth-of-type(1)").find(".toggle")  # alias


def test_lazy_inner_ss():
    given_at_other_page()
    s("#todo-list").ss("li")
    s("#todo-list").all("li")  # alias


def test_is_displayed_fails_with_waiting_if_element_not_exist():
    given_at_other_page()
    original_timeout = config.timeout  # todo: switch to s("#todo-list").during(0.1).is_displayed()
                                       # todo: once the feature available
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

