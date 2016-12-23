from selene.conditions import exact_text
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


def test_search_is_lazy_and_does_not_start_on_creation_for_both_collection_and_indexed():
    GIVEN_PAGE.opened_empty()
    non_existent_element = ss('.non-existing').findBy(exact_text('Kate'))
    assert str(non_existent_element)


def test_search_is_postponed_until_actual_action_like_questioning_displayed():
    GIVEN_PAGE.opened_empty()
    element = ss('.will-appear').findBy(exact_text('Kate'))

    WHEN.load_body('''
                   <ul>Hello to:
                       <li class="will-appear">Bob</li>
                       <li class="will-appear">Kate</li>
                   </ul>''')
    assert element.is_displayed() is True


def test_search_is_updated_on_next_actual_action_like_questioning_displayed():
    GIVEN_PAGE.opened_empty()
    element = ss('.will-appear').findBy(exact_text('Kate'))

    WHEN.load_body('''
                   <ul>Hello to:
                       <li class="will-appear">Bob</li>
                       <li class="will-appear">Kate</li>
                   </ul>''')
    assert element.is_displayed() is True

    WHEN.load_body('''
                   <ul>Hello to:
                       <li class="will-appear">Bob</li>
                       <li class="will-appear" style="display:none">Kate</li>
                   </ul>''')
    assert element.is_displayed() is False
