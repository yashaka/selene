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


def test_search_is_lazy_and_does_not_start_on_creation():
    GIVEN_PAGE.opened_empty()
    non_existent_collection = s('ul').all('.not-existing')
    assert str(non_existent_collection)


def test_search_is_postponed_until_actual_action_like_questioning_count():
    GIVEN_PAGE.opened_empty()
    elements = s('ul').all('.will-appear')

    WHEN.load_body('''
                   <ul>Hello to:
                       <li class='will-appear'>Bob</li>
                       <li class='will-appear'>Kate</li>
                   </ul>''')
    assert len(elements) == 2


def test_search_is_updated_on_next_actual_action_like_questioning_count():
    GIVEN_PAGE.opened_empty()
    elements = s('ul').all('.will-appear')

    WHEN.load_body('''
                   <ul>Hello to:
                       <li class='will-appear'>Bob</li>
                       <li class='will-appear'>Kate</li>
                   </ul>''')
    assert len(elements) == 2

    WHEN.load_body('''
                   <ul>Hello to:
                       <li class='will-appear'>Bob</li>
                       <li class='will-appear'>Kate</li>
                       <li class='will-appear'>Joe</li>
                   </ul>''')
    assert len(elements) == 3