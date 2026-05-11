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

from selene import have, be
from selene.core import match
from tests.integration.helpers.givenpage import GivenPage


# todo: consider breaking it down into separate tests


def test_should_be_blank__passed_and_failed(session_browser):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>
        <!--<li id="absent"></li>-->
        <li id="hidden-empty" style="display: none"></li>
        <li id="hidden" style="display: none"> One  !!!
        </li>
        <li id="visible-empty" style="display: block"></li>
        <li id="visible" style="display: block"> One  !!!
        </li>
        </ul>
        <!--<input id="absent"></li>-->
        <input id="hidden-empty" style="display: none">
        <input id="hidden" style="display: none" value=" One  !!!">
        <input id="visible-empty" style="display: block" value="">
        <input id="visible" style="display: block" value=" One  !!!">
        '''
    )

    # THEN

    # be blank?
    # - visible empty non-input passes
    s('li#visible-empty').should(match.blank)
    s('li#visible-empty').should(be.blank)
    s('li#visible-empty').should(be.blank.not_.not_)
    # - visible empty input passes
    s('input#visible-empty').should(match.blank)
    s('input#visible-empty').should(be.blank)
    s('input#visible-empty').should(be.blank.not_.not_)
    # - visible non-empty non-input fails
    try:
        s('li#visible').should(be.blank)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', 'li#visible')).is blank\n"
            '\n'
            'Reason: ConditionMismatch: actual text: One !!!\n'
            'Screenshot: '
        ) in str(error)
    # - visible non-empty input fails
    try:
        s('input#visible').should(be.blank)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', 'input#visible')).is blank\n"
            '\n'
            'Reason: ConditionMismatch: actual value:  One  !!!\n'
            'Screenshot: '
        ) in str(error)
    # - hidden empty non-input passes
    s('li#hidden-empty').should(match.blank)
    s('li#hidden-empty').should(be.blank)
    s('li#hidden-empty').should(be.blank.not_.not_)
    # - hidden empty input passes
    s('input#hidden-empty').should(match.blank)
    s('input#hidden-empty').should(be.blank)
    s('input#hidden-empty').should(be.blank.not_.not_)
    # - hidden non-empty non-input passes
    #   (because checks text that is empty for hidden)
    s('li#hidden').should(match.blank)
    s('li#hidden').should(be.blank)
    s('li#hidden').should(be.blank.not_.not_)
    # - hidden non-empty input fails
    #   (because value can be get from hidden element and is not blank)
    try:
        s('input#hidden').should(be.blank)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', 'input#hidden')).is blank\n"
            '\n'
            'Reason: ConditionMismatch: actual value:  One  !!!\n'
            'Screenshot: '
        ) in str(error)
    # - absent fails with failure
    try:
        s('#absent').should(be.blank)
        pytest.fail('expect FAILURE')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).is blank\n"
            '\n'
            'Reason: NoSuchElementException: no such element: Unable to locate element: '
            '{"method":"css selector","selector":"#absent"}\n'
            '  (Session info: '  # 'chrome=126.0.6478.127); For documentation on this error, '
            # 'please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
        ) in str(error)


def test_should_be_not_blank__passed_and_failed(session_browser):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>
        <!--<li id="absent"></li>-->
        <!--<input id="absent">-->
        <li id="hidden-empty" style="display: none"></li>
        <li id="hidden" style="display: none"> One  !!!
        </li>
        <li id="visible-empty" style="display: block"></li>
        <li id="visible" style="display: block"> One  !!!
        </li>
        </ul>
        <!--<input id="absent"></li>-->
        <input id="hidden-empty" style="display: none">
        <input id="hidden" style="display: none" value=" One  !!!">
        <input id="visible-empty" style="display: block" value="">
        <input id="visible" style="display: block" value=" One  !!!">
        '''
    )

    # THEN

    # be not blank?
    # - visible empty non-input fails
    try:
        # s('li#visible-empty').should(match.blank.not_)
        s('li#visible-empty').should(be.not_.blank)
        # s('li#visible-empty').should(be.not_.blank.not_.not_)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', 'li#visible-empty')).is not (blank)\n"
            '\n'
            'Reason: ConditionMismatch: actual text: \n'
            'Screenshot: '
        ) in str(error)
    # - visible empty input fails
    try:
        # s('input#visible-empty').should(match.blank.not_)
        s('input#visible-empty').should(be.not_.blank)
        # s('input#visible-empty').should(be.not_.blank.not_.not_)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', 'input#visible-empty')).is not (blank)\n"
            '\n'
            'Reason: ConditionMismatch: actual value: \n'
            'Screenshot: '
        ) in str(error)
    # - visible non-empty non-input passes
    s('li#visible').should(match.blank.not_)
    s('li#visible').should(be.not_.blank)
    s('li#visible').should(be.not_.blank.not_.not_)
    # - visible non-empty input fails
    s('input#visible').should(be.not_.blank)
    # - hidden empty non-input fails
    try:
        s('li#hidden-empty').should(be.not_.blank)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', 'li#hidden-empty')).is not (blank)\n"
            '\n'
            'Reason: ConditionMismatch: actual text: \n'
            'Screenshot: '
        ) in str(error)
    # - hidden empty input passes
    try:
        s('input#hidden-empty').should(be.not_.blank)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', 'input#hidden-empty')).is not (blank)\n"
            '\n'
            'Reason: ConditionMismatch: actual value: \n'
            'Screenshot: '
        ) in str(error)
    # - hidden non-empty non-input passes
    #   (because checks text that is empty for hidden)
    try:
        s('li#hidden').should(be.not_.blank)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', 'li#hidden')).is not (blank)\n"
            '\n'
            'Reason: ConditionMismatch: actual text: \n'
            'Screenshot: '
        ) in str(error)
    # - hidden non-empty input passes
    #   (because value can be got from hidden element and is not blank)
    s('input#hidden').should(be.not_.blank)
    # - absent fails with failure
    try:
        s('#absent').should(be.not_.blank)
        pytest.fail('expect FAILURE')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).is not (blank)\n"
            '\n'
            'Reason: NoSuchElementException: no such element: Unable to locate element: '
            '{"method":"css selector","selector":"#absent"}\n'
            '  (Session info: '  # 'chrome=126.0.6478.127); For documentation on this error, '
            # 'please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
        ) in str(error)
