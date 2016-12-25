from selenium import webdriver

from selene import config
from selene.conditions import css_class, exact_text
from selene.selene_driver import SeleneDriver
from tests.atomic.helpers.givenpage import GivenPage

__author__ = 'yashaka'

driver = SeleneDriver(webdriver.Firefox())
GIVEN_PAGE = GivenPage(driver)
WHEN = GIVEN_PAGE
original_timeout = config.timeout


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
