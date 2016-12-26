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


def test_search_is_lazy_and_does_not_start_on_creation_for_both_parent_and_inner():
    GIVEN_PAGE.opened_empty()
    non_existent_element = driver.element('#not-existing-element').element('.not-existing-inner')
    assert str(non_existent_element)


def test_search_is_postponed_until_actual_action_like_questioning_displayed():
    GIVEN_PAGE.opened_empty()

    element = driver.element('#will-be-existing-element').element('.will-exist-inner')
    WHEN.load_body('''
        <h1 id="will-be-existing-element">
            <span class="will-exist-inner">Hello</span> kitty:*
        </h1>''')
    assert element.is_displayed() is True


def test_search_is_updated_on_next_actual_action_like_questioning_displayed():
    GIVEN_PAGE.opened_empty()

    element = driver.element('#will-be-existing-element').element('.will-exist-inner')
    WHEN.load_body('''
        <h1 id="will-be-existing-element">
            <span class="will-exist-inner">Hello</span> kitty:*
        </h1>''')
    assert element.is_displayed() is True

    element = driver.element('#will-be-existing-element').element('.will-exist-inner')
    WHEN.load_body('''
        <h1 id="will-be-existing-element">
            <span class="will-exist-inner" style="display:none">Hello</span> kitty:*
        </h1>''')
    assert element.is_displayed() is False


def test_search_finds_exactly_inside_parent():
    GIVEN_PAGE.opened_with_body('''
        <a href="#first">go to Heading 2</a>
        <p>
            <a href="#second">go to Heading 2</a>
            <h1 id="first">Heading 1</h1>
            <h2 id="second">Heading 2</h2>
        /p>''')

    driver.element('p').element('a').click()
    assert ("second" in driver.current_url()) is True
