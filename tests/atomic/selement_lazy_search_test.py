import pytest
from selenium.common.exceptions import TimeoutException

from tests.atomic.helpers.givenpage import GivenPage
from selenium import webdriver
from selene.tools import *

__author__ = 'yashaka'

driver = webdriver.Firefox()
GIVEN_PAGE = GivenPage(driver)
WHEN = GIVEN_PAGE
original_timeout = config.timeout


def setup_module(m):
    set_driver(driver)


def teardown_module(m):
    get_driver().quit()


def setup_function(fn):
    global original_timeout
    config.timeout = original_timeout


def test_selement_search_is_lazy_and_does_not_start_on_creation():
    GIVEN_PAGE.opened_empty()
    non_existent_element = s('#not-existing-element-id')
    assert str(non_existent_element)


def test_selement_search_is_postponed_until_actual_action_like_questioining_displayed():
    GIVEN_PAGE.opened_empty()

    element = s('#will-be-existing-element-id')
    WHEN.load_body('<h1 id="will-be-existing-element-id">Hello kitty:*</h1>')
    assert element.is_displayed() is True


def test_selement_search_is_updated_on_next_actual_action_like_questioning_displayed():
    GIVEN_PAGE.opened_empty()

    element = s('#will-be-existing-element-id')
    WHEN.load_body('<h1 id="will-be-existing-element-id">Hello kitty:*</h1>')
    assert element.is_displayed() is True

    WHEN.load_body('<h1 id="will-be-existing-element-id" style="display:none">Hello kitty:*</h1>')
    assert element.is_displayed() is False
