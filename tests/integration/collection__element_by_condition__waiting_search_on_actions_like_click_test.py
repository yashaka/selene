# MIT License
#
# Copyright (c) 2015-2021 Iakiv Kramarenko
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import pytest

from selene import have
from selene.core.exceptions import TimeoutException
from tests.integration.helpers.givenpage import GivenPage


def test_waits_for_visibility(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_with_body(
        '''
        <a href="#second" style="display:none">go to Heading 2</a>
        <h2 id="second">Heading 2</h2>'''
    ).execute_script_with_timeout(
        'document.getElementsByTagName("a")[0].style = "display:block";', 500
    )

    element = session_browser.all('a').element_by(
        have.exact_text('go to Heading 2')
    )
    element.click()

    assert "second" in session_browser.driver.current_url


def test_waits_for_present_in_dom_and_visibility(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_with_body(
        '''
        <h2 id="second">Heading 2</h2>'''
    )
    page.load_body_with_timeout(
        '''
        <a href="#second">go to Heading 2</a>
        <h2 id="second">Heading 2</h2>''',
        500,
    )

    element = session_browser.all('a').element_by(
        have.exact_text('go to Heading 2')
    )
    element.click()

    assert "second" in session_browser.driver.current_url


def test_waits_first_for_present_in_dom_then_visibility(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_with_body(
        '''
        <h2 id="second">Heading 2</h2>'''
    )
    page.load_body_with_timeout(
        '''
        <a href="#second" style="display:none">go to Heading 2</a>
        <h2 id="second">Heading 2</h2>''',
        250,
    ).execute_script_with_timeout(
        'document.getElementsByTagName("a")[0].style = "display:block";', 500
    )

    element = session_browser.all('a').element_by(
        have.exact_text('go to Heading 2')
    )
    element.click()

    assert "second" in session_browser.driver.current_url


def test_fails_on_timeout_during_waiting_for_visibility(session_browser):
    browser = session_browser.with_(timeout=0.25)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <a href='#second' style='display:none'>go to Heading 2</a>
        <h2 id='second'>Heading 2</h2>'''
    ).execute_script_with_timeout(
        'document.getElementsByTagName("a")[0].style = "display:block";', 500
    )

    with pytest.raises(TimeoutException):
        browser.all('a').element_by(have.exact_text('go to Heading 2')).click()

    assert "second" not in session_browser.driver.current_url


def test_fails_on_timeout_during_waits_for_present_in_dom_and_visibility(
    session_browser,
):
    browser = session_browser.with_(timeout=0.25)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <h2 id="second">Heading 2</h2>'''
    )
    page.load_body_with_timeout(
        '''
        <a href="#second">go to Heading 2</a>
        <h2 id="second">Heading 2</h2>''',
        500,
    )

    with pytest.raises(TimeoutException):
        browser.all('a').element_by(have.exact_text('go to Heading 2')).click()

    assert "second" not in session_browser.driver.current_url


def test_fails_on_timeout_during_waits_first_for_present_in_dom_then_visibility(
    session_browser,
):
    browser = session_browser.with_(timeout=0.25)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <h2 id="second">Heading 2</h2>'''
    )
    page.load_body_with_timeout(
        '''
        <a href="#second" style="display:none">go to Heading 2</a>
        <h2 id="second">Heading 2</h2>''',
        250,
    ).execute_script_with_timeout(
        'document.getElementsByTagName("a")[0].style = "display:block";', 500
    )

    with pytest.raises(TimeoutException):
        browser.all('a').element_by(have.exact_text('go to Heading 2')).click()

    assert "second" not in session_browser.driver.current_url
