from selenium import webdriver

from core.none_object import NoneObject
from selene import config
from selene.driver import SeleneDriver
from tests.integration.helpers.givenpage import GivenPage

__author__ = 'yashaka'

driver = NoneObject('driver')  # type: SeleneDriver
GIVEN_PAGE = NoneObject('GivenPage')  # type: GivenPage
WHEN = GIVEN_PAGE  # type: GivenPage
original_timeout = config.timeout


def setup_module(m):
    global driver
    driver = SeleneDriver.wrap(webdriver.Firefox())
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
    non_existent_collection = driver.element('ul').all('.not-existing')
    assert str(non_existent_collection)


def test_search_is_postponed_until_actual_action_like_questioning_count():
    GIVEN_PAGE.opened_empty()
    elements = driver.element('ul').all('.will-appear')

    WHEN.load_body('''
                   <ul>Hello to:
                       <li class='will-appear'>Bob</li>
                       <li class='will-appear'>Kate</li>
                   </ul>''')
    assert len(elements) == 2


def test_search_is_updated_on_next_actual_action_like_questioning_count():
    GIVEN_PAGE.opened_empty()
    elements = driver.element('ul').all('.will-appear')

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


def test_searches_exactly_inside_parent():
    GIVEN_PAGE.opened_empty()
    elements = driver.element('ul').all('.will-appear')

    WHEN.load_body('''
                   <ul>Hello to:
                       <li class='will-appear'>Bob</li>
                       <li class='will-appear'>Kate</li>
                   </ul>
                   <li class='forgotten'>Joe</li>''')

    assert len(elements) == 2

