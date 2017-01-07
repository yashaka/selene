from selenium import webdriver

from selene import config
from selene.conditions import css_class, exact_text
from selene.common.none_object import NoneObject
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


def test_search_is_lazy_and_does_not_start_on_creation_for_both_collection_and_indexed():
    GIVEN_PAGE.opened_empty()
    non_existent_element = driver.all('.non-existing').element_by(exact_text('Kate'))
    assert str(non_existent_element)


def test_search_is_postponed_until_actual_action_like_questioning_displayed():
    GIVEN_PAGE.opened_empty()
    element = driver.all('.will-appear').element_by(exact_text('Kate'))

    WHEN.load_body('''
                   <ul>Hello to:
                       <li class="will-appear">Bob</li>
                       <li class="will-appear">Kate</li>
                   </ul>''')
    assert element.is_displayed() is True


def test_search_is_updated_on_next_actual_action_like_questioning_displayed():
    GIVEN_PAGE.opened_empty()
    element = driver.all('.will-appear').element_by(css_class('special'))

    WHEN.load_body('''
                   <ul>Hello to:
                       <li class="will-appear">Bob</li>
                       <li class="will-appear special">Kate</li>
                   </ul>''')
    assert element.is_displayed() is True

    WHEN.load_body('''
                   <ul>Hello to:
                       <li class="will-appear">Bob</li>
                       <li class="will-appear special" style="display:none">Kate</li>
                   </ul>''')
    assert element.is_displayed() is False
