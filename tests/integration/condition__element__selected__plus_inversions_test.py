# MIT License
#
# Copyright (c) 2015-2022 Iakiv Kramarenko
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

from selene import be
from selene.core import match
from selene.core.condition import Match
from tests.integration.helpers.givenpage import GivenPage


# todo: consider covering radio buttons too...


def test_should_be_selected__passed_and_failed(session_browser):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <!--<input type="checkbox" id="absent">-->
        <input type="checkbox" id="hidden-selected" checked style="display: none">
        <input type="checkbox" id="hidden" style="display: none">
        <input type="checkbox" id="visible-selected" checked style="display: block">
        <input type="checkbox" id="visible" style="display: block">
        <p>Just a comment</p>
        '''
    )

    # THEN

    # selected?
    # - visible & selected passes
    s('#visible-selected').should(be.selected)
    s('#visible-selected').should(be.selected.not_.not_)
    # - visible & not selected fails with mismatch
    try:
        s('#visible').should(be.selected)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible')).is selected\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
            'Screenshot: '
        ) in str(error)
    # - visible & non-selectable fails still just with mismatch
    try:
        s('p').should(be.selected)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', 'p')).is selected\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
            'Screenshot: '
        ) in str(error)
    # - hidden & selected passes
    s('#hidden-selected').should(be.selected)
    # - hidden & not selected fails with mismatch
    try:
        s('#hidden').should(be.selected)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).is selected\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
            'Screenshot: '
        ) in str(error)
    # - absent fails with failure
    try:
        s('#absent').should(be.selected)
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).is selected\n"
            '\n'
            'Reason: NoSuchElementException: Message: no such element: Unable to locate '
            'element: {"method":"css selector","selector":"#absent"}\n'
            '  (Session info:'  # ' chrome=126.0.6478.62); For documentation on this error, '
            # 'please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
            # ':\n'
            # 'condition not matched\n'
        ) in str(error)


def test_should_be_not_selected__passed_and_failed(
    session_browser,
):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <!--<input type="checkbox" id="absent">-->
        <input type="checkbox" id="hidden-selected" checked style="display: none">
        <input type="checkbox" id="hidden" style="display: none">
        <input type="checkbox" id="visible-selected" checked style="display: block">
        <input type="checkbox" id="visible" style="display: block">
        <p>Just a comment</p>
        '''
    )

    # THEN

    # not selected?
    # - visible & selected fails with mismatch
    try:
        s('#visible-selected').should(be.not_.selected)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible-selected')).is not (selected)\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
            'Screenshot: '
        ) in str(error)
    # - visible & not-selectable passes
    s('p').should(match.selected.not_)
    # - visible & not-selected passes
    s('#visible').should(match.selected.not_)
    s('#visible').should(be.not_.selected)
    # - hidden & selected fails with mismatch
    try:
        s('#hidden-selected').should(be.not_.selected)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden-selected')).is not (selected)\n"
            '\n'
            'Reason: ConditionMismatch: condition not matched\n'
            'Screenshot: '
        ) in str(error)
    # - hidden & not-selected passed
    s('#hidden').should(be.not_.selected)
    # - absent fails with failure
    try:
        s('#absent').should(be.not_.selected)
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).is not (selected)\n"
            '\n'
            'Reason: NoSuchElementException: Message: no such element: Unable to locate '
            'element: {"method":"css selector","selector":"#absent"}\n'
            '  (Session info:'  # ' chrome=126.0.6478.62); For documentation on this error, '
            # 'please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
            # ':\n'
            # 'condition not matched\n'
        ) in str(error)
