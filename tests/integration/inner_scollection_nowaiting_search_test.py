from selenium import webdriver

from selene import config
from selene.common.none_object import NoneObject
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


def test_does_not_wait_inner():
    GIVEN_PAGE.opened_empty()
    elements = driver.element('ul').all('.will-appear')

    WHEN.load_body('''
                   <ul>Hello to:
                       <li class='will-appear'>Bob</li>
                       <li class='will-appear' style='display:none'>Kate</li>
                   </ul>''')
    assert len(elements) == 2

    WHEN.load_body_with_timeout('''
                                <ul>Hello to:
                                    <li class='will-appear'>Bob</li>
                                    <li class='will-appear' style='display:none'>Kate</li>
                                    <li class='will-appear'>Joe</li>
                                </ul>''',
                                500)
    assert len(elements) == 2


def test_waits_for_parent_in_dom_then_visible():
    GIVEN_PAGE.opened_empty()
    elements = driver.element('ul').all('.will-appear')

    WHEN.load_body('''
                   <li class='will-appear'>Bob</li>
                   <li class='will-appear' style='display:none'>Kate</li>''')

    WHEN.load_body_with_timeout('''
                                <ul style="display:none">Hello to:
                                    <li class='will-appear'>Bob</li>
                                    <li class='will-appear' style='display:none'>Kate</li>
                                </ul>''',
                                250)\
        .execute_script_with_timeout(
            'document.getElementsByTagName("ul")[0].style = "display:block";',
            500)
    assert len(elements) == 2