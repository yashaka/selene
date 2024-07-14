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


def test_should_have_exact_text__passed_and_failed__with_text_to_trim(session_browser):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>
        <!--<li id="absent"></li>-->
        <li id="hidden-empty" checked style="display: none"></li>
        <li id="hidden" style="display: none"> One  !!!
        </li>
        <li id="visible-empty" checked style="display: block"></li>
        <li id="visible" style="display: block"> One  !!!
        </li>
        </ul>
        '''
    )

    # THEN

    # have exact text?
    # - visible and correct expected (normalized) passes
    s('#visible').should(match.exact_text('One !!!'))
    s('#visible').should(have.exact_text('One !!!'))
    s('#visible').should(have.exact_text('One !!!').not_.not_)
    s('#visible').should(have.no.exact_text('One !!!').not_)
    # - visible and incorrect expected (partial) fails
    try:
        s('#visible').should(have.exact_text('One'))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible')).has exact text 'One'\n"
            '\n'
            'Reason: ConditionMismatch: actual text: One !!!\n'
            'Screenshot: '
        ) in str(error)
    # - visible & empty and correct expected passes
    s('#visible-empty').should(have.exact_text(''))
    s('#visible-empty').should(have.exact_text('').not_.not_)
    # - visible & non-textable (like input) with always '' expected passes
    '''
    # let's just skip it:)
    '''
    # - hidden and with always '' expected passes
    s('#hidden').should(have.exact_text(''))
    # - hidden & empty with always '' expected passes
    s('#hidden-empty').should(have.exact_text(''))
    # - hidden and incorrect expected of actual exact text fails
    try:
        s('#hidden').should(have.exact_text('One !!!'))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).has exact text 'One !!!'\n"
            '\n'
            'Reason: ConditionMismatch: actual text: \n'
            'Screenshot: '  # ...
        ) in str(error)
    # - absent and expected '' fails with failure
    try:
        s('#absent').should(have.exact_text(''))
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).has exact text ''\n"
            '\n'
            'Reason: NoSuchElementException: no such element: Unable to locate element: '
            '{"method":"css selector","selector":"#absent"}\n'
            '  (Session info: '  # 'chrome=126.0.6478.114); For documentation on this error, '
            # 'please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
            # 'Screenshot: '
        ) in str(error)
    # - absent and expected '' + double inversion fails with failure
    try:
        s('#absent').should(have.exact_text('').not_.not_)
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).has exact text ''\n"
            '\n'
            'Reason: NoSuchElementException: no such element: Unable to locate element: '
            '{"method":"css selector","selector":"#absent"}\n'
            '  (Session info: '  # 'chrome=126.0.6478.114); For documentation on this error, '
            # 'please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
            # 'Screenshot: '
        ) in str(error)


def test_should_have_exact_text__passed_and_failed__with_text_to_trim__ignore_case(
    session_browser,
):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>
        <!--<li id="absent"></li>-->
        <li id="hidden-empty" checked style="display: none"></li>
        <li id="hidden" style="display: none"> One  !!!
        </li>
        <li id="visible-empty" checked style="display: block"></li>
        <li id="visible" style="display: block"> One  !!!
        </li>
        </ul>
        '''
    )

    # THEN

    # have exact text?
    # - visible and correct expected (normalized) passes
    s('#visible').should(match.exact_text('ONE !!!').ignore_case)
    s('#visible').should(have.exact_text('ONE !!!').ignore_case)
    s('#visible').should(have.exact_text('ONE !!!').ignore_case.not_.not_)
    s('#visible').should(have.no.exact_text('ONE !!!').ignore_case.not_)
    s('#visible').with_(_ignore_case=True).should(have.exact_text('ONE !!!'))
    # - visible and incorrect expected (partial) fails
    try:
        s('#visible').should(have.exact_text('ONE').ignore_case)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible')).has exact text ignoring case: "
            "'ONE'\n"
            '\n'
            'Reason: ConditionMismatch: actual text: One !!!\n'
        ) in str(error)
    try:
        s('#visible').with_(_ignore_case=True).should(have.exact_text('ONE'))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible')).has exact text ignoring case: "
            "'ONE'\n"
            '\n'
            'Reason: ConditionMismatch: actual text: One !!!\n'
        ) in str(error)
    # - visible & empty and correct expected passes
    s('#visible-empty').should(have.exact_text('').ignore_case)
    s('#visible-empty').should(have.exact_text('').ignore_case.not_.not_)

    s('#visible-empty').with_(_ignore_case=True).should(have.exact_text(''))
    # - visible & non-textable (like input) with always '' expected passes
    '''
    # let's just skip it:)
    '''
    # - hidden and with always '' expected passes
    s('#hidden').should(have.exact_text('').ignore_case)
    s('#hidden').with_(_ignore_case=True).should(have.exact_text(''))
    # - hidden & empty with always '' expected passes
    s('#hidden-empty').should(have.exact_text('').ignore_case)
    s('#hidden-empty').with_(_ignore_case=True).should(have.exact_text(''))
    # - hidden and incorrect expected of actual exact text fails
    '''
    # let's just skip it:)
    '''
    # - absent and expected '' fails with failure
    try:
        s('#absent').should(have.exact_text('').ignore_case)
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).has exact text ignoring case: "
            "''\n"
            '\n'
            'Reason: NoSuchElementException: no such element: Unable to locate element: '
            '{"method":"css selector","selector":"#absent"}\n'
        ) in str(error)
    try:
        s('#absent').with_(_ignore_case=True).should(have.exact_text(''))
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).has exact text ignoring case: "
            "''\n"
            '\n'
            'Reason: NoSuchElementException: no such element: Unable to locate element: '
            '{"method":"css selector","selector":"#absent"}\n'
        ) in str(error)
    # - absent and expected '' + double inversion fails with failure
    try:
        s('#absent').should(have.exact_text('').ignore_case.not_.not_)
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).has exact text ignoring case: "
            "''\n"
            '\n'
            'Reason: NoSuchElementException: no such element: Unable to locate element: '
            '{"method":"css selector","selector":"#absent"}\n'
        ) in str(error)
    try:
        s('#absent').with_(_ignore_case=True).should(have.exact_text('').not_.not_)
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).has exact text ignoring case: "
            "''\n"
            '\n'
            'Reason: NoSuchElementException: no such element: Unable to locate element: '
            '{"method":"css selector","selector":"#absent"}\n'
        ) in str(error)


def test_should_have_no_exact_text__passed_and_failed__with_text_to_trim(
    session_browser,
):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>
        <!--<li id="absent"></li>-->
        <li id="hidden-empty" checked style="display: none"></li>
        <li id="hidden" style="display: none"> One  !!!
        </li>
        <li id="visible-empty" checked style="display: block"></li>
        <li id="visible" style="display: block"> One  !!!
        </li>
        </ul>
        '''
    )

    # THEN

    # have no exact text?
    # - visible and incorrect expected (not normalized) passes
    s('#visible').should(match.exact_text(' One  !!!\n').not_)
    s('#visible').should(have.no.exact_text(' One  !!!\n'))
    s('#visible').should(have.no.exact_text(' One  !!!\n').not_.not_)
    # - visible and incorrect expected (partial) passes
    s('#visible').should(match.exact_text('One').not_)
    s('#visible').should(have.no.exact_text('One'))
    s('#visible').should(have.no.exact_text('One').not_.not_)
    # - visible and correct expected (normalized) fails
    try:
        s('#visible').should(have.no.exact_text('One !!!'))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible')).has no (exact text 'One !!!')\n"
            '\n'
            'Reason: ConditionMismatch: actual text: One !!!\n'
            'Screenshot: '  # ...
        ) in str(error)
    # - visible & empty and correct '' expected fails  # todo: improve empty text rendering
    try:
        s('#visible-empty').should(have.no.exact_text(''))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible-empty')).has no (exact text '')\n"
            '\n'
            'Reason: ConditionMismatch: actual text: \n'
            'Screenshot: '  # ...
        ) in str(error)
    # - visible & non-textable (like input) with always '' expected fails
    '''
    # let's just skip it:)
    '''
    # - hidden and with correct always '' expected fails
    try:
        s('#hidden').should(have.no.exact_text(''))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).has no (exact text '')\n"
            '\n'
            'Reason: ConditionMismatch: actual text: \n'
            'Screenshot: '  # ...
        ) in str(error)
    # - hidden & empty with always '' expected fails
    try:
        s('#hidden-empty').should(have.no.exact_text(''))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden-empty')).has no (exact text '')\n"
            '\n'
            'Reason: ConditionMismatch: actual text: \n'
            'Screenshot: '  # ...
        ) in str(error)
    # - hidden and incorrect expected of actual exact text passes
    s('#hidden').should(have.no.exact_text('One !!!'))
    # - hidden & empty and incorrect expected of actual exact text passes
    s('#hidden-empty').should(have.no.exact_text('One !!!'))
    # - absent and potentially correct expected '' fails with failure
    try:
        s('#absent').should(have.no.exact_text(''))
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).has no (exact text '')\n"
            '\n'
            'Reason: NoSuchElementException: no such element: Unable to locate element: '
            '{"method":"css selector","selector":"#absent"}\n'
            '  (Session info: '  # 'chrome=126.0.6478.114); For documentation on this error, '
            # 'please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
            # 'Screenshot: '
        ) in str(error)
    # - absent and potentially correct expected '' + double inversion fails with failure
    try:
        s('#absent').should(have.no.exact_text('').not_.not_)
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).has no (exact text '')\n"
            '\n'
            'Reason: NoSuchElementException: no such element: Unable to locate element: '
            '{"method":"css selector","selector":"#absent"}\n'
            '  (Session info: '  # 'chrome=126.0.6478.114); For documentation on this error, '
            # 'please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
            # 'Screenshot: '
        ) in str(error)
    # - absent and incorrect expected STILL fails with failure
    try:
        s('#absent').should(have.no.exact_text('One !!!'))
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).has no (exact text 'One !!!')\n"
            '\n'
            'Reason: NoSuchElementException: no such element: Unable to locate element: '
            '{"method":"css selector","selector":"#absent"}\n'
            '  (Session info: '  # 'chrome=126.0.6478.114); For documentation on this error, '
            # 'please visit: '
            # 'https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#no-such-element-exception\n'
            # 'Screenshot: '
        ) in str(error)


def test_should_have_no_exact_text__passed_and_failed__with_text_to_trim__ignore_case(
    session_browser,
):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>
        <!--<li id="absent"></li>-->
        <li id="hidden-empty" checked style="display: none"></li>
        <li id="hidden" style="display: none"> One  !!!
        </li>
        <li id="visible-empty" checked style="display: block"></li>
        <li id="visible" style="display: block"> One  !!!
        </li>
        </ul>
        '''
    )

    # THEN

    # have no exact text?
    # - visible and incorrect expected (not normalized) passes
    s('#visible').should(match.exact_text(' ONE  !!!\n').ignore_case.not_)
    s('#visible').should(have.no.exact_text(' ONE  !!!\n').ignore_case)
    s('#visible').should(have.no.exact_text(' ONE  !!!\n').ignore_case.not_.not_)
    s('#visible').with_(_ignore_case=True).should(match.exact_text(' ONE  !!!\n').not_)
    s('#visible').with_(_ignore_case=True).should(have.no.exact_text(' ONE  !!!\n'))
    s('#visible').with_(_ignore_case=True).should(
        have.no.exact_text(' ONE  !!!\n').not_.not_
    )
    # - visible and incorrect expected (partial) passes
    s('#visible').should(match.exact_text('ONE').ignore_case.not_)
    s('#visible').should(have.no.exact_text('ONE').ignore_case)
    s('#visible').should(have.no.exact_text('ONE').ignore_case.not_.not_)
    s('#visible').with_(_ignore_case=True).should(match.exact_text('ONE').not_)
    s('#visible').with_(_ignore_case=True).should(have.no.exact_text('ONE'))
    s('#visible').with_(_ignore_case=True).should(have.no.exact_text('ONE').not_.not_)
    # - visible and correct expected (normalized) fails
    try:
        s('#visible').should(have.no.exact_text('ONE !!!').ignore_case)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible')).has no (exact text ignoring "
            "case: 'ONE !!!')\n"
            '\n'
            'Reason: ConditionMismatch: actual text: One !!!\n'
        ) in str(error)
    try:
        s('#visible').with_(_ignore_case=True).should(have.no.exact_text('ONE !!!'))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible')).has no (exact text ignoring "
            "case: 'ONE !!!')\n"
            '\n'
            'Reason: ConditionMismatch: actual text: One !!!\n'
        ) in str(error)
    # - visible & empty and correct '' expected fails  # todo: improve empty text rendering
    try:
        s('#visible-empty').should(have.no.exact_text('').ignore_case)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible-empty')).has no (exact text "
            "ignoring case: '')\n"
            '\n'
            'Reason: ConditionMismatch: actual text: \n'
        ) in str(error)
    try:
        s('#visible-empty').with_(_ignore_case=True).should(have.no.exact_text(''))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible-empty')).has no (exact text "
            "ignoring case: '')\n"
            '\n'
            'Reason: ConditionMismatch: actual text: \n'
        ) in str(error)
    # - visible & non-textable (like input) with always '' expected fails
    '''
    # let's just skip it:)
    '''
    # - hidden and with correct always '' expected fails
    try:
        s('#hidden').should(have.no.exact_text('').ignore_case)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).has no (exact text ignoring "
            "case: '')\n"
            '\n'
            'Reason: ConditionMismatch: actual text: \n'
        ) in str(error)
    try:
        s('#hidden').with_(_ignore_case=True).should(have.no.exact_text(''))
        s('#hidden').with_(ignore_case=True).should(have.no.exact_text(''))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).has no (exact text ignoring "
            "case: '')\n"
            '\n'
            'Reason: ConditionMismatch: actual text: \n'
        ) in str(error)
    # - hidden & empty with always '' expected fails
    try:
        s('#hidden-empty').should(have.no.exact_text('').ignore_case)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden-empty')).has no (exact text "
            "ignoring case: '')\n"
            '\n'
            'Reason: ConditionMismatch: actual text: \n'
        ) in str(error)
    try:
        s('#hidden-empty').with_(_ignore_case=True).should(have.no.exact_text(''))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden-empty')).has no (exact text "
            "ignoring case: '')\n"
            '\n'
            'Reason: ConditionMismatch: actual text: \n'
        ) in str(error)
    # - hidden and incorrect expected of actual exact text passes
    s('#hidden').should(have.no.exact_text('One !!!').ignore_case)
    # - hidden & empty and incorrect expected of actual exact text passes
    s('#hidden-empty').should(have.no.exact_text('One !!!').ignore_case)
    # - absent and potentially correct expected '' fails with failure
    try:
        s('#absent').should(have.no.exact_text('').ignore_case)
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).has no (exact text ignoring "
            "case: '')\n"
            '\n'
            'Reason: NoSuchElementException: no such element: Unable to locate element: '
            '{"method":"css selector","selector":"#absent"}\n'
        ) in str(error)
    try:
        s('#absent').with_(_ignore_case=True).should(have.no.exact_text(''))
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).has no (exact text ignoring "
            "case: '')\n"
            '\n'
            'Reason: NoSuchElementException: no such element: Unable to locate element: '
            '{"method":"css selector","selector":"#absent"}\n'
        ) in str(error)
    # - absent and potentially correct expected '' + double inversion fails with failure
    '''skip it'''
    # - absent and incorrect expected STILL fails with failure
    '''skip it'''


def test_unicode_text_with_trailing_and_leading_spaces(session_browser):
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>Привет:
           <li>  Саше \n </li>
           <li>Яше</li>
           <li>и еще ...</li>
           <li>100</li>
           <li>приветов всем остальним</li>
        </ul>
        '''
    )

    element = session_browser.element('li')

    element.should(have.exact_text('Саше')).should(have.text('Са'))
    session_browser.all('li')[-2].should(have.exact_text(100)).should(have.text(100))
