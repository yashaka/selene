import pytest
from selenium.common.exceptions import TimeoutException

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


def test_selement_search_waits_for_visibility_on_actions_like_click():
    GIVEN_PAGE\
        .opened_with_body(
            '''
            <a href="#second" style="display:none">go to Heading 2</a>
            <h2 id="second">Heading 2</h2>''')\
        .execute_script_with_timeout(
            'document.getElementsByTagName("a")[0].style = "display:block";',
            500)

    s('a').click()
    assert ("second" in get_driver().current_url) is True


def test_selement_search_waits_for_present_in_dom_and_visibility_on_actions_like_click():
    GIVEN_PAGE.opened_with_body(
            '''
            <h2 id="second">Heading 2</h2>''')
    WHEN.load_body_with_timeout(
            '''
            <a href="#second">go to Heading 2</a>
            <h2 id="second">Heading 2</h2>''',
            500)

    s('a').click()
    assert ("second" in get_driver().current_url) is True


def test_selement_search_waits_first_for_present_in_dom_then_visibility_on_actions_like_click():
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

    s('a').click()
    assert ("second" in get_driver().current_url) is True


def test_selement_search_fails_on_timeout_during_waiting_for_visibility_on_actions_like_click():
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
        s("a").click()
    assert ("second" in get_driver().current_url) is False

