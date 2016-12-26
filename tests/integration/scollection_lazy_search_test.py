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
    non_existent_collection = driver.all('.not-existing')
    assert str(non_existent_collection)


def test_search_is_postponed_until_actual_action_like_questioning_count():
    GIVEN_PAGE.opened_empty()
    elements = driver.all('.will-appear')

    WHEN.load_body('''
                   <ul>Hello to:
                       <li class='will-appear'>Bob</li>
                       <li class='will-appear'>Kate</li>
                   </ul>''')
    assert len(elements) == 2


def test_search_is_updated_on_next_actual_action_like_questioning_count():
    GIVEN_PAGE.opened_empty()
    elements = driver.all('.will-appear')

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