import pytest
from selenium.common.exceptions import TimeoutException
from webdriver_manager.firefox import GeckoDriverManager

from selene.support.conditions import have
from selene.browser import *
from tests.acceptance.helpers.helper import get_test_driver
from tests.acceptance.helpers.todomvc import given_active


def setup_module(m):
    set_driver(get_test_driver())


def teardown_module(m):
    driver().quit()


def test_assure_passes():
    given_active("a", "b")
    ss("#todo-list>li").should(have.exact_texts("a", "b"))


def test_assure_fails():
    given_active("a", "b")
    with pytest.raises(TimeoutException):
        ss("#todo-list>li").should(have.exact_texts("a.", "b."), timeout=0.1)
