import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from selene.conditions import exact_texts, visible, text
from selene.tools import *
from tests.acceptance.helpers.todomvc import given_active, given_at_other_page


def setup_module(m):
    set_driver(webdriver.Firefox())


def teardown_module(m):
    get_driver().quit()


def test_assure_passes():
    given_active("a", "b")
    ss("#todo-list>li").assure(exact_texts("a", "b"))


def test_assure_fails():
    given_active("a", "b")
    with pytest.raises(TimeoutException):
        ss("#todo-list>li").assure(exact_texts("a.", "b."), timeout=0.1)


def test_lazy_ss():
    given_at_other_page()
    tasks = ss("#todo-list>li")


def test_lazy_filter():
    given_at_other_page()
    visibleTasks = ss("#todo-list>li").filtered_by(visible)


def test_lazy_getitem():
    given_at_other_page()
    firstTask = ss("#todo-list>li")[0]


def test_lazy_find():
    given_at_other_page()
    task_a = ss("#todo-list>li").element_by(text("a"))










