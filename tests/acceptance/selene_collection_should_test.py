import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from selene.conditions import exact_texts, visible, text
from selene.support.conditions import have
from selene.tools import *
from tests.acceptance.helpers.todomvc import given_active, given_at_other_page


def setup_module(m):
    set_driver(webdriver.Firefox())


def teardown_module(m):
    get_driver().quit()


def test_assure_passes():
    given_active("a", "b")
    ss("#todo-list>li").should(have.exact_texts("a", "b"))


def test_assure_fails():
    given_active("a", "b")
    with pytest.raises(TimeoutException):
        ss("#todo-list>li").should(have.exact_texts("a.", "b."), timeout=0.1)










