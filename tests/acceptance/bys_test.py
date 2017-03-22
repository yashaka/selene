from tests.acceptance.helpers.helper import get_test_driver

__author__ = 'yashaka'

from selene.browser import *
from tests.acceptance.helpers.todomvc import given_active
from selene.bys import *


def setup_module(m):
    set_driver(get_test_driver())


def teardown_module(m):
    driver().quit()


def test_by_text_with_single_and_double_quotes():
    given_active("""Fred's last name is "Li".""")
    assert find_element(by_text("""Fred's last name is "Li".""")).is_displayed()


def find_element(locator):
    return driver().find_element(*locator)
