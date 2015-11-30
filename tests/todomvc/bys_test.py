__author__ = 'ayia'

from selenium import webdriver

from selene.tools import *
from tests.todomvc.helpers.todomvc import given_active
from selene.bys import *


def setup_module(m):
    set_driver(webdriver.Firefox())


def teardown_module(m):
    get_driver().quit()


def test_by_text_with_single_and_double_quotes():
    given_active("""Fred's last name is "Li".""")
    assert find_element(by_text("""Fred's last name is "Li".""")).is_displayed()


def find_element(locator):
    return get_driver().find_element(*locator)
