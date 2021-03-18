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

import re

import pytest

from selene import have
from selene.core.exceptions import TimeoutException
from tests.integration.helpers.givenpage import GivenPage


def exception_message(ex):
    msg_simplified = re.sub(
        r'\(Session info: .*\)', '(Session info: *)', str(ex.value.msg)
    )
    screenshot_pattern = (
        r'\s*screenshot: .*?/\.selene/screenshots/\d+?/screen_\d+\.png\s*'
    )
    return [
        line.strip()
        if not re.match(screenshot_pattern, line)
        else 'screenshot: //.selene/screenshots/*/screen_*.png'
        for line in msg_simplified.strip().splitlines()
    ]


def test_element_search_fails_with_message_when_explicitly_waits_for_condition(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <label id='element'>Hello world!</label>
        '''
    )

    with pytest.raises(TimeoutException) as ex:
        browser.element('#element').should(have.exact_text('Hello wor'))

    assert exception_message(ex) == [
        'Timed out after 0.1s, while waiting for:',
        "browser.element(('css selector', '#element')).has exact text Hello wor",
        '',
        'Reason: AssertionError: actual text: Hello world!',
    ]


def test_element_search_fails_with_message_when_implicitly_waits_for_condition(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
    <button id='hidden-button' style='display:none'>You can't click me, ha ha! :P</button>
    '''
    )

    with pytest.raises(TimeoutException) as ex:
        browser.element('#hidden-button').click()

    assert exception_message(ex) == [
        'Timed out after 0.1s, while waiting for:',
        "browser.element(('css selector', '#hidden-button')).click",
        '',
        'Reason: ElementNotInteractableException: Message: element not interactable',
        '(Session info: *)',
    ]


def test_inner_element_search_fails_with_message_when_implicitly_waits_for_condition_mismatch_on_inner_element(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
    <div id='container'>
        <button id='hidden-button' style='display:none'>You can't click me, ha ha! :P</button>
    </div>
    '''
    )

    with pytest.raises(TimeoutException) as ex:
        browser.element('#container').element('#hidden-button').click()

    assert exception_message(ex) == [
        'Timed out after 0.1s, while waiting for:',
        "browser.element(('css selector', '#container')).element(('css selector', "
        "'#hidden-button')).click",
        '',
        'Reason: ElementNotInteractableException: Message: element not interactable',
        '(Session info: *)',
    ]


def test_inner_element_search_fails_with_message_when_implicitly_waits_for_condition_mismatched_on_parent_element(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
    <div id='hidden-container' style='display:none'>
        <button id='button'>You still can't click me, ha ha! :P</button>
    </div>
    '''
    )

    with pytest.raises(TimeoutException) as ex:
        browser.element('#hidden-container').element('#button').click()

    assert exception_message(ex) == [
        'Timed out after 0.1s, while waiting for:',
        "browser.element(('css selector', '#hidden-container')).element(('css "
        "selector', '#button')).click",
        '',
        'Reason: ElementNotInteractableException: Message: element not interactable',
        '(Session info: *)',
    ]


def test_inner_element_search_fails_with_message_when_implicitly_waits_for_condition_failed_on_parent_element(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
    <div>
        <button id='button'>Try to click me</button>
    </div>
    '''
    )

    with pytest.raises(TimeoutException) as ex:
        browser.element('#not-existing').element('#button').click()

    assert exception_message(ex)[:10] == [
        'Timed out after 0.1s, while waiting for:',
        "browser.element(('css selector', '#not-existing')).element(('css selector', "
        "'#button')).click",
        '',
        'Reason: NoSuchElementException: Message: no such element: Unable to locate '
        'element: {"method":"css selector","selector":"#not-existing"}',
        '(Session info: *)',
    ]


def test_indexed_selement_search_fails_with_message_when_implicitly_waits_for_condition_failed_on_collection(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    page = GivenPage(browser.driver)
    page.opened_with_body(
        '''
    <div>
        <button id='button'>Try to click me</button>
    </div>
    '''
    )

    with pytest.raises(TimeoutException) as ex:
        browser.all('button')[1].click()

    assert exception_message(ex) == [
        'Timed out after 0.1s, while waiting for:',
        "browser.all(('css selector', 'button'))[1].click",
        '',
        'Reason: AssertionError: Cannot get element with index 1 from webelements '
        'collection with length 1',
    ]


# todo: uncomment when refactored conditions implementation
# def test_selement_search_fails_with_message_when_explicitly_waits_for_not_condition():
#     GIVEN_PAGE.opened_with_body('''
#     <label id='element'>Hello world!</label>
#     ''')
#     config.timeout = 0.1
#
#     s('#element').should_not(have.exact_text('Hello world!'))
#     with pytest.raises(TimeoutException) as ex:
#         s('#element').should_not(have.exact_text('Hello world!'))
#
#     assert exception_message(ex) == \
#            ['failed while waiting 0.1 seconds',
#             'to assert not ExactText',
#             "for first_by('css selector', '#element')",
#             '',
#             'reason: ConditionMismatchException: condition did not match',
#             'expected: not(Hello world!)',
#             'actual: Hello world!',
#             'screenshot: //.selene/screenshots/*/screen_*.png']
