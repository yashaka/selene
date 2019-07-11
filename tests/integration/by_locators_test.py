import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

from selene import config
from selene.common.none_object import NoneObject
from selene.driver import SeleneDriver
from selene.support import by
from tests.integration.helpers.givenpage import GivenPage

__author__ = 'yashaka'

driver = NoneObject('driver')  # type: SeleneDriver
GIVEN_PAGE = NoneObject('GivenPage')  # type: GivenPage
WHEN = GIVEN_PAGE  # type: GivenPage
original_timeout = config.timeout


def setup_module(m):
    global driver
    driver = SeleneDriver.wrap(webdriver.Chrome(ChromeDriverManager().install()))
    global GIVEN_PAGE
    GIVEN_PAGE = GivenPage(driver)
    global WHEN
    WHEN = GIVEN_PAGE


def teardown_module(m):
    global original_timeout
    config.timeout = original_timeout
    driver.quit()


def setup_function(fn):
    config.timeout = original_timeout



def test_complex_locator_based_on_by_locators():
    GIVEN_PAGE\
        .opened_with_body(
            '''
            <div id="container">
                <div>
                    <div>
                        <label>First</label>
                    </div>
                    <div>
                        <a href="#first">go to Heading 1</a>
                    </div>
                </div>
                <div>
                    <div>
                        <label>Second</label>
                    </div>
                    <div>
                        <a href="#second">go to Heading 2</a>
                    </div>
                </div>
            </div>
            <h1 id="first">Heading 1</h2>
            <h2 id="second">Heading 2</h2>
            ''')

    driver.element('#container')\
        .element(by.text('Second'))\
        .element(by.be_parent())\
        .element(by.be_following_sibling())\
        .element(by.be_first_child())\
        .click()
    assert ('second' in driver.current_url) is True


def test_complex_locator_based_on_selene_element_relative_elements():
    GIVEN_PAGE\
        .opened_with_body(
            '''
            <div id="container">
                <div>
                    <div>
                        <label>First</label>
                    </div>
                    <div>
                        <a href="#first">go to Heading 1</a>
                    </div>
                </div>
                <div>
                    <div>
                        <label>Second</label>
                    </div>
                    <div>
                        <a href="#second">go to Heading 2</a>
                    </div>
                </div>
            </div>
            <h1 id="first">Heading 1</h2>
            <h2 id="second">Heading 2</h2>
            ''')

    driver.element('#container')\
        .element(by.partial_text('Sec'))\
        .parent_element\
        .following_sibling\
        .first_child\
        .click()
    assert ('second' in driver.current_url) is True
