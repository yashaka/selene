from selenium import webdriver

from core.none_object import NoneObject
from selene import config
from selene.driver import SeleneDriver
from tests.acceptance.helpers.helper import get_test_driver
from tests.integration.helpers.givenpage import GivenPage

__author__ = 'yashaka'

driver = NoneObject('driver')  # type: SeleneDriver
GIVEN_PAGE = NoneObject('GivenPage')  # type: GivenPage
WHEN = GIVEN_PAGE  # type: GivenPage
original_timeout = config.timeout


def setup_module(m):
    global driver
    driver = SeleneDriver.wrap(get_test_driver())
    global GIVEN_PAGE
    GIVEN_PAGE = GivenPage(driver)
    global WHEN
    WHEN = GIVEN_PAGE


def teardown_module(m):
    driver.quit()


def setup_function(fn):
    global original_timeout
    config.timeout = original_timeout


def test_search_is_lazy_and_does_not_start_on_creation():
    GIVEN_PAGE.opened_empty()
    non_existent_element = driver.element('#not-existing-element-id')
    assert str(non_existent_element)


def test_search_is_postponed_until_actual_action_like_questioning_displayed():
    GIVEN_PAGE.opened_empty()

    element = driver.element('#will-be-existing-element-id')
    WHEN.load_body('<h1 id="will-be-existing-element-id">Hello kitty:*</h1>')
    assert element.is_displayed() is True


def test_search_is_updated_on_next_actual_action_like_questioning_displayed():
    GIVEN_PAGE.opened_empty()

    element = driver.element('#will-be-existing-element-id')
    WHEN.load_body('<h1 id="will-be-existing-element-id">Hello kitty:*</h1>')
    assert element.is_displayed() is True

    WHEN.load_body('<h1 id="will-be-existing-element-id" style="display:none">Hello kitty:*</h1>')
    assert element.is_displayed() is False
