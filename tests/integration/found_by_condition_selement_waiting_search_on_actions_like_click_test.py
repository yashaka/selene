import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from selene import config
from selene.conditions import css_class, exact_text
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


def test_waits_for_visibility():
    GIVEN_PAGE\
        .opened_with_body(
            '''
            <a href="#second" style="display:none">go to Heading 2</a>
            <h2 id="second">Heading 2</h2>''')\
        .execute_script_with_timeout(
            'document.getElementsByTagName("a")[0].style = "display:block";',
            500)

    driver.all('a').element_by(exact_text('go to Heading 2')).click()
    assert ("second" in driver.current_url()) is True


def test_waits_for_present_in_dom_and_visibility():
    GIVEN_PAGE.opened_with_body(
            '''
            <h2 id="second">Heading 2</h2>''')
    WHEN.load_body_with_timeout(
            '''
            <a href="#second">go to Heading 2</a>
            <h2 id="second">Heading 2</h2>''',
            500)

    driver.all('a').element_by(exact_text('go to Heading 2')).click()
    assert ("second" in driver.current_url()) is True


def test_waits_first_for_present_in_dom_then_visibility():
    GIVEN_PAGE.opened_with_body(
            '''
            <h2 id="second">Heading 2</h2>''')
    WHEN.load_body_with_timeout(
            '''
            <a href="#second" style="display:none">go to Heading 2</a>
            <h2 id="second">Heading 2</h2>''',
            250)\
        .execute_script_with_timeout(
            'document.getElementsByTagName("a")[0].style = "display:block";',
            500)

    driver.all('a').element_by(exact_text('go to Heading 2')).click()
    assert ("second" in driver.current_url()) is True


# todo: there should be each such test method for each "passing" test from above...
def test_fails_on_timeout_during_waiting_for_visibility():
    config.timeout = 0.25
    GIVEN_PAGE\
        .opened_with_body(
            '''
            <a href='#second' style='display:none'>go to Heading 2</a>
            <h2 id='second'>Heading 2</h2>''')\
        .execute_script_with_timeout(
            'document.getElementsByTagName("a")[0].style = "display:block";',
            500)

    with pytest.raises(TimeoutException):
        driver.all('a').element_by(exact_text('go to Heading 2')).click()
    assert ("second" in driver.current_url()) is False

