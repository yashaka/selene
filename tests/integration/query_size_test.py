import pytest

from selene import Browser, query, by
from tests.integration.helpers.givenpage import GivenPage


def test_query_size_of_browser(session_browser):

    size = session_browser.get(query.size)

    assert size == session_browser.driver.get_window_size()


def test_query_size_of_collection(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_empty()
    elements = session_browser.all('.will-appear')
    page.load_body(
        '''
        <ul>Hello to:
            <li class='will-appear'>Bob</li>
            <li class='will-appear' style='display:none'>Kate</li>
        </ul>
        '''
    )

    count = elements.get(query.size)

    assert count == 2


def test_query_size_of_element(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_empty()
    page.load_body(
        '''
        <ul>Hello to:
            <li class='will-appear'>Bob</li>
            <li class='will-appear' style='display:none'>Kate</li>
        </ul>
        '''
    )

    size = session_browser.element('ul').get(query.size)

    assert size == session_browser.driver.find_element(*by.css('ul')).size
