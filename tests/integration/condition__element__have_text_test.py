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
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import pytest

from selene import have
from selene.core import match
from tests.integration.helpers.givenpage import GivenPage


def test_should_have_text__passed_and_failed__with_text_to_trim(session_browser):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    GivenPage(session_browser.driver).opened_with_body('''
        <ul>
        <!--<li id="absent"></li>-->
        <li id="hidden-empty" checked style="display: none"></li>
        <li id="hidden" style="display: none"> One  !!!
        </li>
        <li id="visible-empty" checked style="display: block"></li>
        <li id="visible" style="display: block"> One  !!!
        </li>
        </ul>
        ''')

    s('#visible').should(match.text_containing('One'))
    s('#visible').should(have.text('One'))
    s('#visible').should(have.text('One !!!'))
    s('#visible').should(have.text('One').not_.not_)
    s('#visible').should(have.no.text('One').not_)

    try:
        s('#visible').should(have.text('Two'))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible')).has text 'Two'\n"
            '\n'
            'Reason: ConditionMismatch: actual text: One !!!\n'
        ) in str(error)

    s('#visible-empty').should(have.text(''))
    s('#visible-empty').should(have.text('').not_.not_)
    s('#hidden').should(have.text(''))
    s('#hidden-empty').should(have.text(''))

    try:
        s('#hidden').should(have.text('One'))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).has text 'One'\n"
            '\n'
            'Reason: ConditionMismatch: actual text: \n'
        ) in str(error)

    try:
        s('#absent').should(have.text(''))
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).has text ''\n"
            '\n'
            'Reason: NoSuchElementException: no such element: Unable to locate element: '
            '{"method":"css selector","selector":"#absent"}\n'
        ) in str(error)


def test_should_have_text__passed_and_failed__with_text_to_trim__ignore_case(
    session_browser,
):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    GivenPage(session_browser.driver).opened_with_body('''
        <ul>
        <!--<li id="absent"></li>-->
        <li id="hidden-empty" checked style="display: none"></li>
        <li id="hidden" style="display: none"> One  !!!
        </li>
        <li id="visible-empty" checked style="display: block"></li>
        <li id="visible" style="display: block"> One  !!!
        </li>
        </ul>
        ''')

    s('#visible').should(match.text_containing('ONE').ignore_case)
    s('#visible').should(have.text('ONE').ignore_case)
    s('#visible').should(have.text('ONE !!!').ignore_case)
    s('#visible').should(have.text('ONE').ignore_case.not_.not_)
    s('#visible').should(have.no.text('ONE').ignore_case.not_)
    s('#visible').with_(_match_ignoring_case=True).should(have.text('ONE'))

    try:
        s('#visible').should(have.text('TWO').ignore_case)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible')).has text ignoring case: "
            "'TWO'\n"
            '\n'
            'Reason: ConditionMismatch: actual text: One !!!\n'
        ) in str(error)

    try:
        s('#visible').with_(_match_ignoring_case=True).should(have.text('TWO'))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible')).has text ignoring case: "
            "'TWO'\n"
            '\n'
            'Reason: ConditionMismatch: actual text: One !!!\n'
        ) in str(error)

    s('#visible-empty').should(have.text('').ignore_case)
    s('#hidden').should(have.text('').ignore_case)
    s('#hidden-empty').with_(_match_ignoring_case=True).should(have.text(''))

    try:
        s('#absent').should(have.text('').ignore_case)
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).has text ignoring case: "
            "''\n"
            '\n'
            'Reason: NoSuchElementException: no such element: Unable to locate element: '
            '{"method":"css selector","selector":"#absent"}\n'
        ) in str(error)


def test_should_have_no_text__passed_and_failed__with_text_to_trim(
    session_browser,
):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    GivenPage(session_browser.driver).opened_with_body('''
        <ul>
        <!--<li id="absent"></li>-->
        <li id="hidden-empty" checked style="display: none"></li>
        <li id="hidden" style="display: none"> One  !!!
        </li>
        <li id="visible-empty" checked style="display: block"></li>
        <li id="visible" style="display: block"> One  !!!
        </li>
        </ul>
        ''')

    s('#visible').should(match.text_containing('Two').not_)
    s('#visible').should(have.no.text('Two'))
    s('#visible').should(have.no.text('Two').not_.not_)

    try:
        s('#visible').should(have.no.text('One'))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible')).has no (text 'One')\n"
            '\n'
            'Reason: ConditionMismatch: actual text: One !!!\n'
        ) in str(error)

    try:
        s('#visible-empty').should(have.no.text(''))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible-empty')).has no (text '')\n"
            '\n'
            'Reason: ConditionMismatch: actual text: \n'
        ) in str(error)

    try:
        s('#hidden').should(have.no.text(''))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#hidden')).has no (text '')\n"
            '\n'
            'Reason: ConditionMismatch: actual text: \n'
        ) in str(error)

    s('#hidden').should(have.no.text('One'))
    s('#hidden-empty').should(have.no.text('One'))

    try:
        s('#absent').should(have.no.text(''))
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).has no (text '')\n"
            '\n'
            'Reason: NoSuchElementException: no such element: Unable to locate element: '
            '{"method":"css selector","selector":"#absent"}\n'
        ) in str(error)


def test_should_have_no_text__passed_and_failed__with_text_to_trim__ignore_case(
    session_browser,
):
    s = lambda selector: session_browser.with_(timeout=0.1).element(selector)
    GivenPage(session_browser.driver).opened_with_body('''
        <ul>
        <!--<li id="absent"></li>-->
        <li id="hidden-empty" checked style="display: none"></li>
        <li id="hidden" style="display: none"> One  !!!
        </li>
        <li id="visible-empty" checked style="display: block"></li>
        <li id="visible" style="display: block"> One  !!!
        </li>
        </ul>
        ''')

    s('#visible').should(match.text_containing('TWO').ignore_case.not_)
    s('#visible').should(have.no.text('TWO').ignore_case)
    s('#visible').with_(_match_ignoring_case=True).should(have.no.text('TWO'))

    try:
        s('#visible').should(have.no.text('ONE').ignore_case)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible')).has no "
            "(text ignoring case: 'ONE')\n"
            '\n'
            'Reason: ConditionMismatch: actual text: One !!!\n'
        ) in str(error)

    try:
        s('#visible').with_(_match_ignoring_case=True).should(have.no.text('ONE'))
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible')).has no "
            "(text ignoring case: 'ONE')\n"
            '\n'
            'Reason: ConditionMismatch: actual text: One !!!\n'
        ) in str(error)

    try:
        s('#visible-empty').should(have.no.text('').ignore_case)
        pytest.fail('expect mismatch')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#visible-empty')).has no "
            "(text ignoring case: '')\n"
            '\n'
            'Reason: ConditionMismatch: actual text: \n'
        ) in str(error)

    try:
        s('#absent').should(have.no.text('').ignore_case)
        pytest.fail('expect failure')
    except AssertionError as error:
        assert (
            "browser.element(('css selector', '#absent')).has no "
            "(text ignoring case: '')\n"
            '\n'
            'Reason: NoSuchElementException: no such element: Unable to locate element: '
            '{"method":"css selector","selector":"#absent"}\n'
        ) in str(error)


def test_should_have_text_with_numeric_expected_value(session_browser):
    GivenPage(session_browser.driver).opened_with_body('''
        <ul>
          <li>100 points</li>
        </ul>
        ''')

    session_browser.element('li').should(have.text(100))
