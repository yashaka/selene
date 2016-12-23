from tests.atomic.helpers.givenpage import GivenPage
from selenium import webdriver
from selene.tools import *

__author__ = 'yashaka'

driver = webdriver.Firefox()
GIVEN_PAGE = GivenPage(driver)
WHEN = GIVEN_PAGE


def setup_module(m):
    set_driver(driver)


def teardown_module(m):
    get_driver().quit()


def test_does_not_wait_inner():
    GIVEN_PAGE.opened_empty()
    elements = s('ul').find_all('.will-appear')

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
    elements = s('ul').find_all('.will-appear')

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