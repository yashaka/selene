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

from selene.core.exceptions import TimeoutException
from tests.integration.helpers.givenpage import GivenPage


def test_waits_for_inner_visibility(session_browser):
    (
        GivenPage(session_browser.driver)
        .opened_with_body(
            '''
            <p>
                <a href="#second" style="display:none">go to Heading 2</a>
                <h2 id="second">Heading 2</h2>
            </p>
            '''
        )
        .execute_script_with_timeout(
            'document.getElementsByTagName("a")[0].style = "display:block";',
            250,
        )
    )

    session_browser.element('p').element('a').click()

    assert "second" in session_browser.driver.current_url


def test_waits_for_inner_presence_in_dom_and_visibility(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_with_body(
        '''
        <p>
             <h2 id="second">Heading 2</h2>
        </p>'''
    )
    page.load_body_with_timeout(
        '''
        <p>
            <a href="#second">go to Heading 2</a>
            <h2 id="second">Heading 2</h2>
        </p>''',
        250,
    )

    session_browser.element('p').element('a').click()

    assert "second" in session_browser.driver.current_url


def test_waits_first_for_inner_presence_in_dom_then_visibility(
    session_browser,
):
    page = GivenPage(session_browser.driver)
    page.opened_with_body(
        '''
        <p>
            <h2 id="second">Heading 2</h2>
        </p>'''
    )
    page.load_body_with_timeout(
        '''
        <p>
            <a href="#second" style="display:none">go to Heading 2</a>
            <h2 id="second">Heading 2</h2>
        </p>''',
        250,
    ).execute_script_with_timeout(
        'document.getElementsByTagName("a")[0].style = "display:block";', 500
    )

    session_browser.element('p').element('a').click()

    assert "second" in session_browser.driver.current_url


def test_waits_first_for_parent_in_dom_then_inner_in_dom_then_visibility(
    session_browser,
):
    page = GivenPage(session_browser.driver)
    page.opened_empty()
    page.load_body_with_timeout(
        '''
        <p>
            <h2 id="second">Heading 2</h2>
        </p>''',
        250,
    )
    page.load_body_with_timeout(
        '''
        <p>
            <a href="#second" style="display:none">go to Heading 2</a>
            <h2 id="second">Heading 2</h2>
        </p>''',
        500,
    ).execute_script_with_timeout(
        'document.getElementsByTagName("a")[0].style = "display:block";', 750
    )

    session_browser.element('p').element('a').click()

    assert "second" in session_browser.driver.current_url


def test_waits_for__hidden_parent_then_visible_then_inner_hidden_then_visible(
    session_browser,
):
    page = GivenPage(session_browser.driver)
    page.opened_empty()
    page.load_body_with_timeout(
        '''
        <p style="display:none">
            <h2 id="second">Heading 2</h2>
        </p>''',
        250,
    ).execute_script_with_timeout(
        'document.getElementsByTagName("p")[0].style = "display:block";', 500
    )
    page.load_body_with_timeout(
        '''
        <p>
            <a href="#second" style="display:none">go to Heading 2</a>
            <h2 id="second">Heading 2</h2>
        </p>''',
        750,
    ).execute_script_with_timeout(
        'document.getElementsByTagName("a")[0].style = "display:block";', 1000
    )

    session_browser.element('p').element('a').click()

    assert "second" in session_browser.driver.current_url


def test_fails_on_timeout_during_waiting_for_inner_visibility(session_browser):
    browser = session_browser.with_(timeout=0.25)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <p>
            <a href='#second' style='display:none'>go to Heading 2</a>
            <h2 id='second'>Heading 2</h2>
        </p>'''
    ).execute_script_with_timeout(
        'document.getElementsByTagName("a")[0].style = "display:block";', 500
    )

    with pytest.raises(TimeoutException):
        browser.element('p').element('a').click()

    assert "second" not in browser.driver.current_url


def test_fails_on_timeout_during_waiting_for_inner_in_dom_and_visibility(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <p>
             <h2 id="second">Heading 2</h2>
        </p>'''
    )
    page.load_body_with_timeout(
        '''
        <p>
            <a href="#second">go to Heading 2</a>
            <h2 id="second">Heading 2</h2>
        </p>''',
        250,
    )

    with pytest.raises(TimeoutException):
        browser.element('p').element('a').click()

    assert "second" not in browser.driver.current_url


def test_fails_on_timeout_during_waiting_first_for_inner_in_dom_then_visibility(
    session_browser,
):
    browser = session_browser.with_(timeout=0.25)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
        <p>
            <h2 id="second">Heading 2</h2>
        </p>'''
    )
    page.load_body_with_timeout(
        '''
        <p>
            <a href="#second" style="display:none">go to Heading 2</a>
            <h2 id="second">Heading 2</h2>
        </p>''',
        250,
    ).execute_script_with_timeout(
        'document.getElementsByTagName("a")[0].style = "display:block";', 500
    )

    with pytest.raises(TimeoutException):
        browser.element('p').element('a').click()

    assert "second" not in browser.driver.current_url


def test_fails_on_timeout_when_waiting_parent_in_dom_then_inner_in_dom_then_visible(
    session_browser,
):
    browser = session_browser.with_(timeout=0.25)
    page = GivenPage(browser.driver)
    page.opened_empty()
    page.load_body_with_timeout(
        '''
        <p>
            <h2 id="second">Heading 2</h2>
        </p>''',
        250,
    )
    page.load_body_with_timeout(
        '''
        <p>
            <a href="#second" style="display:none">go to Heading 2</a>
            <h2 id="second">Heading 2</h2>
        </p>''',
        500,
    ).execute_script_with_timeout(
        'document.getElementsByTagName("a")[0].style = "display:block";', 750
    )

    with pytest.raises(TimeoutException):
        browser.element('p').element('a').click()

    assert "second" not in browser.driver.current_url


def test_fails_on_timeout_when_waiting_parent_in_dom_then_visible_then_inner_in_dom_then_visible(
    session_browser,
):
    browser = session_browser.with_(timeout=0.25)
    page = GivenPage(browser.driver)
    page.opened_empty()
    page.load_body_with_timeout(
        '''
        <p style="display:none">
            <h2 id="second">Heading 2</h2>
        </p>''',
        250,
    ).execute_script_with_timeout(
        'document.getElementsByTagName("p")[0].style = "display:block";', 500
    )
    page.load_body_with_timeout(
        '''
        <p>
            <a href="#second" style="display:none">go to Heading 2</a>
            <h2 id="second">Heading 2</h2>
        </p>''',
        750,
    ).execute_script_with_timeout(
        'document.getElementsByTagName("a")[0].style = "display:block";', 1000
    )

    with pytest.raises(TimeoutException):
        browser.element('p').element('a').click()

    assert "second" not in browser.driver.current_url
