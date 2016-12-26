from selenium import webdriver

from selene import config
from selene.conditions import css_class
from selene.selene_driver import SeleneDriver
from selene.support.conditions import have
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
    non_existent_collection = driver.all('.not-existing').filtered_by(css_class('special'))
    assert str(non_existent_collection)


def test_search_is_postponed_until_actual_action_like_questioning_count():
    GIVEN_PAGE.opened_empty()
    elements = driver.all('li').filtered_by(css_class('will-appear'))

    WHEN.load_body('''
                   <ul>Hello to:
                       <li>Anonymous</li>
                       <li class='will-appear'>Bob</li>
                       <li class='will-appear'>Kate</li>
                   </ul>''')
    assert len(elements) == 2


def test_search_is_updated_on_next_actual_action_like_questioning_count():
    GIVEN_PAGE.opened_empty()
    elements = driver.all('li').filtered_by(css_class('will-appear'))

    WHEN.load_body('''
                   <ul>Hello to:
                       <li>Anonymous</li>
                       <li class='will-appear'>Bob</li>
                       <li class='will-appear'>Kate</li>
                   </ul>''')
    assert len(elements) == 2

    WHEN.load_body('''
                   <ul>Hello to:
                       <li>Anonymous</li>
                       <li class='will-appear'>Bob</li>
                       <li class='will-appear'>Kate</li>
                       <li class='will-appear'>Joe</li>
                   </ul>''')
    assert len(elements) == 3