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
    config.timeout = original_timeout


def test_search_is_lazy_and_does_not_start_on_creation_for_both_parent_and_inner():
    GIVEN_PAGE.opened_empty()
    non_existent_element = s('#not-existing-element').find('.not-existing-inner')
    assert str(non_existent_element)


def test_search_is_postponed_until_actual_action_like_questioning_displayed():
    GIVEN_PAGE.opened_empty()

    element = s('#will-be-existing-element').find('.will-exist-inner')
    WHEN.load_body('''
        <h1 id="will-be-existing-element">
            <span class="will-exist-inner">Hello</span> kitty:*
        </h1>''')
    assert element.is_displayed() is True


def test_search_is_updated_on_next_actual_action_like_questioning_displayed():
    GIVEN_PAGE.opened_empty()

    element = s('#will-be-existing-element').find('.will-exist-inner')
    WHEN.load_body('''
        <h1 id="will-be-existing-element">
            <span class="will-exist-inner">Hello</span> kitty:*
        </h1>''')
    assert element.is_displayed() is True

    element = s('#will-be-existing-element').find('.will-exist-inner')
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

    s('p').find('a').click()
    assert ("second" in get_driver().current_url) is True
