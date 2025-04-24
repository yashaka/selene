import pytest

from selene import have
from selene.core.exceptions import TimeoutException
from tests.integration.helpers.givenpage import GivenPage


def test_click_waits_for_visibility(session_browser):
    # GIVEN
    page = GivenPage(session_browser.driver)
    page.opened_with_body(
        '''
        <a href="#second" style="display:none">go to Heading 2</a>
        <h2 id="second">Heading 2</h2>
        '''
    ).execute_script_with_timeout(
        'document.getElementsByTagName("a")[0].style = "display:block";', 0.5
    )

    # WHEN
    element = session_browser.all('a').element_by(have.exact_text('go to Heading 2'))
    element.click()

    # THEN
    assert "second" in session_browser.driver.current_url


def test_click_waits_for_dom_presence_and_visibility(session_browser):
    # GIVEN
    page = GivenPage(session_browser.driver)
    page.opened_with_body('<h2 id="second">Heading 2</h2>')
    page.load_body_with_timeout(
        '''
        <a href="#second">go to Heading 2</a>
        <h2 id="second">Heading 2</h2>
        ''',
        0.5,
    )

    # WHEN
    element = session_browser.all('a').element_by(have.exact_text('go to Heading 2'))
    element.click()

    # THEN
    assert "second" in session_browser.driver.current_url


def test_click_waits_for_dom_then_visibility(session_browser):
    # GIVEN
    page = GivenPage(session_browser.driver)
    page.opened_with_body('<h2 id="second">Heading 2</h2>')
    page.load_body_with_timeout(
        '''
        <a href="#second" style="display:none">go to Heading 2</a>
        <h2 id="second">Heading 2</h2>
        ''',
        0.25,
    ).execute_script_with_timeout(
        'document.getElementsByTagName("a")[0].style = "display:block";', 0.5
    )

    # WHEN
    element = session_browser.all('a').element_by(have.exact_text('go to Heading 2'))
    element.click()

    # THEN
    assert "second" in session_browser.driver.current_url


def test_click_fails_on_timeout_for_visibility(session_browser):
    # GIVEN
    browser = session_browser.with_(timeout=0.25)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <a href="#second" style="display:none">go to Heading 2</a>
        <h2 id="second">Heading 2</h2>
        '''
    ).execute_script_with_timeout(
        'document.getElementsByTagName("a")[0].style = "display:block";', 0.5
    )

    # WHEN / THEN
    with pytest.raises(TimeoutException):
        browser.all('a').element_by(have.exact_text('go to Heading 2')).click()

    assert "second" not in session_browser.driver.current_url


def test_click_fails_on_timeout_for_dom_and_visibility(session_browser):
    # GIVEN
    browser = session_browser.with_(timeout=0.25)
    page = GivenPage(browser.driver)
    page.opened_with_body('<h2 id="second">Heading 2</h2>')
    page.load_body_with_timeout(
        '''
        <a href="#second">go to Heading 2</a>
        <h2 id="second">Heading 2</h2>
        ''',
        0.5,
    )

    # WHEN / THEN
    with pytest.raises(TimeoutException):
        browser.all('a').element_by(have.exact_text('go to Heading 2')).click()

    assert "second" not in session_browser.driver.current_url


def test_click_fails_on_timeout_for_dom_then_visibility(session_browser):
    # GIVEN
    browser = session_browser.with_(timeout=0.25)
    page = GivenPage(browser.driver)
    page.opened_with_body('<h2 id="second">Heading 2</h2>')
    page.load_body_with_timeout(
        '''
        <a href="#second" style="display:none">go to Heading 2</a>
        <h2 id="second">Heading 2</h2>
        ''',
        0.25,
    ).execute_script_with_timeout(
        'document.getElementsByTagName("a")[0].style = "display:block";', 0.5
    )

    # WHEN / THEN
    with pytest.raises(TimeoutException):
        browser.all('a').element_by(have.exact_text('go to Heading 2')).click()

    assert "second" not in session_browser.driver.current_url
