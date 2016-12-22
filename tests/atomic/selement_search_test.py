import pytest
from selenium.common.exceptions import TimeoutException

from tests.atomic.helpers.givenpage import GivenPage
from selenium import webdriver
from selene.tools import *

__author__ = 'yashaka'


def setup_module(m):
    driver = webdriver.Firefox()
    global GIVEN_PAGE
    GIVEN_PAGE = GivenPage(driver)
    global WHEN
    WHEN = GIVEN_PAGE
    global original_timeout
    original_timeout = config.timeout
    set_driver(driver)


def teardown_module(m):
    get_driver().quit()


def setup_function(fn):
    global original_timeout;
    config.timeout = original_timeout


def test_selement_search_is_postponed_until_actual_action_like_questioining_displayed():
    GIVEN_PAGE.opened_empty()

    element = s('#will-be-existing-element-id')
    WHEN.load_body('<h1 id="will-be-existing-element-id">Hello kitty:*</h1>')
    assert element.is_displayed() is True


def test_selement_search_is_updated_on_next_actual_action_like_questioning_displayed():
    GIVEN_PAGE.opened_empty()

    element = s('#will-be-existing-element-id')
    WHEN.load_body('<h1 id="will-be-existing-element-id">Hello kitty:*</h1>')
    assert element.is_displayed() is True

    WHEN.load_body('<h1 id="will-be-existing-element-id" style="display:none">Hello kitty:*</h1>')
    assert element.is_displayed() is False


def test_selement_search_waits_for_visibility_on_actions_like_click():
    GIVEN_PAGE\
        .loaded_with_body(
            """
            <a href="#second" style="display:none">go to Heading 2</a>
            <h2 id="second">Heading 2</h2>""")\
        .execute_script_with_timeout(
            'document.getElementsByTagName("a")[0].style = "display:block";',
            500)

    s('a').click()
    assert ("second" in get_driver().current_url) is True


def test_selement_search_fails_on_timeout_during_waiting_for_visibility_on_actions_like_click():
    config.timeout = 0.25
    GIVEN_PAGE\
        .loaded_with_body(
            """
            <a href='#second' style='display:none'>go to Heading 2</a>
            <h2 id='second'>Heading 2</h2>""")\
        .execute_script_with_timeout(
            'document.getElementsByTagName("a")[0].style = "display:block";',
            500)

    with pytest.raises(TimeoutException):
        s("a").click()
    assert ("second" in get_driver().current_url) is False

