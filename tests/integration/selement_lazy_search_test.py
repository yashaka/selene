from selenium import webdriver

from selene import config
from selene.selene_driver import SeleneDriver
from tests.integration.helpers.givenpage import GivenPage

__author__ = 'yashaka'

driver = SeleneDriver.wrap(webdriver.Firefox())
GIVEN_PAGE = GivenPage(driver)
WHEN = GIVEN_PAGE
original_timeout = config.timeout


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
