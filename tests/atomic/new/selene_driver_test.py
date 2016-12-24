import pytest
from selenium.common.exceptions import TimeoutException

from selene import config
from selene.selene_driver import SeleneDriver
from tests.atomic.helpers.givenpage import GivenPage
from selenium import webdriver

__author__ = 'yashaka'

driver = webdriver.Firefox()
GIVEN_PAGE = GivenPage(driver)
browser = SeleneDriver(driver)
WHEN = GIVEN_PAGE
original_timeout = config.timeout


def s(css_selector):
    return browser.find(css_selector)


def teardown_module(m):
    driver.quit()


def setup_function(fn):
    global original_timeout
    config.timeout = original_timeout


def test_waits_for_visibility():
    GIVEN_PAGE\
        .opened_with_body(
            '''
            <a href="#second" style="display:none">go to Heading 2</a>
            <h2 id="second">Heading 2</h2>''')\
        .execute_script_with_timeout(
            'document.getElementsByTagName("a")[0].style = "display:block";',
            500)

    s('a').click()
    assert ("second" in driver.current_url) is True