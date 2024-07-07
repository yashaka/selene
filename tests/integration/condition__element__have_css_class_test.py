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

from selene import have
from selene.core import match
from tests.integration.helpers.givenpage import GivenPage


# todo: consider breaking it down into separate tests


def test_should_have_css_class__passed_and_failed(session_browser):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>
        <!--<li id="absent"></li>-->
        <li id="hidden-empty" style="display: none"></li>
        <li id="hidden" class="one two three" style="display: none"> One  !!!
        </li>
        <li id="visible-empty" style="display: block"></li>
        <li id="visible" class="one two three" style="display: block"> One  !!!
        </li>
        </ul>
        '''
    )

    # THEN

    # have css class?
    # - visible and correct expected passes
    s('#visible').should(match.css_class('one'))
    s('#visible').should(have.css_class('one'))
    s('#visible').should(have.css_class('one').not_.not_)
    # - visible and incorrect expected fails
    try:
        s('#visible').should(have.css_class('One'))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible')).has css class 'One'\n"
            '\n'
            'Reason: ConditionMismatch: actual class attribute value: one two three\n'
            'Screenshot: '
        ) in str(error)
    # - visible & empty and incorrect expected fails
    try:
        s('#visible-empty').should(have.css_class('one'))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible-empty')).has css class 'one'\n"
            '\n'
            'Reason: ConditionMismatch: actual class attribute value: \n'
        ) in str(error)
    # - visible & empty and empty expected passes  # todo: ok, right?
    s('#visible-empty').should(have.css_class(''))
    # - hidden & empty with always '' expected passes
    s('#hidden-empty').should(have.css_class(''))
    # - hidden and incorrect expected fails
    '''skipped (pw)'''
    # - absent and expected '' fails with failure
    try:
        s('#absent').should(have.css_class(''))
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).has css class ''\n"
            '\n'
            'Reason: NoSuchElementException: no such element: Unable to locate element: '
            '{"method":"css selector","selector":"#absent"}\n'
            '  (Session info: '  # 'chrome=126.0.6478.127); For documentation on this error, '
            # 'please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
            # 'Screenshot: '
        ) in str(error)
    # - absent and expected '' + double inversion fails with failure
    '''skipped (pw)'''


def test_should_have_css_class__ignore_case__passed_and_failed(session_browser):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>
        <!--<li id="absent"></li>-->
        <li id="hidden-empty" style="display: none"></li>
        <li id="hidden" class="one two three" style="display: none"> One  !!!
        </li>
        <li id="visible-empty" style="display: block"></li>
        <li id="visible" class="one two three" style="display: block"> One  !!!
        </li>
        </ul>
        '''
    )

    # THEN

    # have css class ignore case?
    # - visible and correct expected passes
    s('#visible').should(match.css_class('ONE').ignore_case)
    s('#visible').should(have.css_class('ONE').ignore_case)
    s('#visible').should(have.css_class('ONE').ignore_case.not_.not_)
    # - visible and incorrect expected fails
    try:
        s('#visible').should(have.css_class('o-n-e').ignore_case)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible')).has css class ignoring case: 'o-n-e'\n"
            '\n'
            'Reason: ConditionMismatch: actual class attribute value: one two three\n'
            'Screenshot: '
        ) in str(error)
    # - visible & empty and incorrect expected fails
    try:
        s('#visible-empty').should(have.css_class('o-n-e').ignore_case)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible-empty')).has css class ignoring case: 'o-n-e'\n"
            '\n'
            'Reason: ConditionMismatch: actual class attribute value: \n'
        ) in str(error)
    # - visible & empty and empty expected passes  # todo: ok, right?
    s('#visible-empty').should(have.css_class('').ignore_case)
    # - hidden & empty with always '' expected passes
    s('#hidden-empty').should(have.css_class('').ignore_case)
    # - hidden and incorrect expected fails
    '''skipped (pw)'''
    # - absent and expected '' fails with failure
    try:
        s('#absent').should(have.css_class('').ignore_case)
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).has css class ignoring case: ''\n"
            '\n'
            'Reason: NoSuchElementException: no such element: Unable to locate element: '
            '{"method":"css selector","selector":"#absent"}\n'
            '  (Session info: '  # 'chrome=126.0.6478.127); For documentation on this error, '
            # 'please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
            # 'Screenshot: '
        ) in str(error)
    # - absent and expected '' + double inversion fails with failure
    '''skipped (pw)'''


def test_should_have_no_css_class__passed_and_failed(session_browser):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>
        <!--<li id="absent"></li>-->
        <li id="hidden-empty" style="display: none"></li>
        <li id="hidden" class="one two three" style="display: none"> One  !!!
        </li>
        <li id="visible-empty" style="display: block"></li>
        <li id="visible" class="one two three" style="display: block"> One  !!!
        </li>
        </ul>
        '''
    )

    # THEN

    # have no css class?
    # - visible and correct expected fails
    try:
        s('#visible').should(have.no.css_class('one'))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible')).has no (css class 'one')\n"
            '\n'
            'Reason: ConditionMismatch: actual class attribute value: one two three\n'
            'Screenshot: '
        ) in str(error)
    # - visible and incorrect expected passes
    s('#visible').should(match.css_class('One').not_)
    s('#visible').should(have.no.css_class('One'))
    s('#visible').should(have.no.css_class('One').not_.not_)
    # - visible & empty and incorrect expected passes
    s('#visible-empty').should(have.no.css_class('one'))
    # - visible & empty and empty expected fails  # todo: ok, right?
    try:
        s('#visible-empty').should(have.no.css_class(''))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible-empty')).has no (css class '')\n"
            '\n'
            'Reason: ConditionMismatch: actual class attribute value: \n'
            'Screenshot: '
        ) in str(error)
    # - hidden & empty with always '' expected fails
    '''skipped (pw)'''
    # - hidden and incorrect expected passes
    s('#hidden').should(have.no.css_class('One'))
    # - absent and expected '' fails with failure
    try:
        s('#absent').should(have.no.css_class(''))
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).has no (css class '')\n"
            '\n'
            'Reason: NoSuchElementException: no such element: Unable to locate element: '
            '{"method":"css selector","selector":"#absent"}\n'
            '  (Session info: '  # 'chrome=126.0.6478.127); For documentation on this error, '
            # 'please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
            # 'Screenshot: '
        ) in str(error)
    # - absent and expected '' + double inversion fails with failure
    '''skipped (pw)'''


def test_should_have_no_css_class__ignore_case__passed_and_failed(session_browser):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>
        <!--<li id="absent"></li>-->
        <li id="hidden-empty" style="display: none"></li>
        <li id="hidden" class="one two three" style="display: none"> One  !!!
        </li>
        <li id="visible-empty" style="display: block"></li>
        <li id="visible" class="one two three" style="display: block"> One  !!!
        </li>
        </ul>
        '''
    )

    # THEN

    # have no css class?
    # - visible and correct expected fails
    try:
        s('#visible').should(have.no.css_class('ONE').ignore_case)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible')).has no (css class ignoring case: 'ONE')\n"
            '\n'
            'Reason: ConditionMismatch: actual class attribute value: one two three\n'
            'Screenshot: '
        ) in str(error)
    # - visible and incorrect expected passes
    s('#visible').should(match.css_class('o-n-e').ignore_case.not_)
    s('#visible').should(have.no.css_class('o-n-e').ignore_case)
    s('#visible').should(have.no.css_class('o-n-e').ignore_case.not_.not_)
    # - visible & empty and incorrect expected passes
    s('#visible-empty').should(have.no.css_class('o-n-e').ignore_case)
    # - visible & empty and empty expected fails  # todo: ok, right?
    try:
        s('#visible-empty').should(have.no.css_class('').ignore_case)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible-empty')).has no (css class ignoring case: '')\n"
            '\n'
            'Reason: ConditionMismatch: actual class attribute value: \n'
            'Screenshot: '
        ) in str(error)
    # - hidden & empty with always '' expected fails
    '''skipped (pw)'''
    # - hidden and incorrect expected passes
    s('#hidden').should(have.no.css_class('o-n-e').ignore_case)
    # - absent and expected '' fails with failure
    try:
        s('#absent').should(have.no.css_class('').ignore_case)
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).has no (css class ignoring case: '')\n"
            '\n'
            'Reason: NoSuchElementException: no such element: Unable to locate element: '
            '{"method":"css selector","selector":"#absent"}\n'
            '  (Session info: '  # 'chrome=126.0.6478.127); For documentation on this error, '
            # 'please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
            # 'Screenshot: '
        ) in str(error)
    # - absent and expected '' + double inversion fails with failure
    '''skipped (pw)'''
