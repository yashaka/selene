# MIT License
#
# Copyright (c) 2024 Iakiv Kramarenko
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


# TODO: consider breaking it down into separate tests,
#       and remove duplicates with other test suites


def test_have_text__condition_variations(session_browser):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>Hey:
           <li><label>First Name:</label> <span class="name" id="firstname">John 20th</span></li>
           <li><label>Last Name:</label> <span class="name" id="lastname">Doe 2nd</span></li>
        </ul>
        <ul>Your training today:
           <li><label>Pull up:</label><span class='exercise' id="pullup">20</span></li>
           <li><label>Push up:</label><span class='exercise' id="pushup">30</span></li>
        </ul>
        '''
    )

    names = browser.all('.name')
    exercises = browser.all('.exercise')

    exercises.should(have.exact_texts(20, 30))
    exercises.should(have.exact_texts('20', '30'))
    exercises.should(have.texts(2, 3))
    exercises.should(have.texts('2', '3'))
    exercises.should(have.text('0').each)
    exercises.should(have.text(0).each)
    exercises.second.should(have.no.exact_text(20))
    exercises.should(have.exact_text(20).each.not_)
    # exercises.should(have.no.exact_text(20).each)  # TODO: fix it

    try:
        names.should(have.texts(20, 2).not_)
        pytest.fail('should fail on texts mismatch')
    except AssertionError as error:
        assert (
            'Timed out after 0.1s, while waiting for:\n'
            "browser.all(('css selector', '.name')).have no (texts (20, 2))\n"
            '\n'
            "Reason: ConditionMismatch: actual visible texts: ['John 20th', 'Doe 2nd']\n"
        ) in str(error)


def test_text__including_ignorecase__passed_compared_to_failed(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
          <li>1) One!!!</li>
          <li>2) Two...</li>
          <li>3) Three???</li>
        </ul>
        '''
    )

    # have.text
    browser.all('li').first.should(have.text('one').ignore_case)
    try:
        browser.all('li').first.should(have.text('one.').ignore_case)
        pytest.fail('expected text mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li'))[0].has text ignoring case: one.\n"
            '\n'
            'Reason: ConditionMismatch: actual text: 1) One!!!\n'
        ) in str(error)
    # - inverted
    # - - with no before
    browser.all('li').first.should(have.no.text('one.').ignore_case)
    try:
        browser.all('li').first.should(have.no.text('one').ignore_case)
        pytest.fail('expected text mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li'))[0].has no (text ignoring case: one)\n"
            '\n'
            'Reason: ConditionMismatch: actual text: 1) One!!!\n'
        ) in str(error)
    # - - with not after, in the end
    #     (in the middle works but without Autocomplete & not recommended)
    browser.all('li').first.should(have.text('one.').ignore_case.not_)
    try:
        browser.all('li').first.should(have.text('one').ignore_case.not_)
        pytest.fail('expected text mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li'))[0].has no (text ignoring case: one)\n"
            '\n'
            'Reason: ConditionMismatch: actual text: 1) One!!!\n'
        ) in str(error)


def test_exact_text__including_ignorecase__passed_compared_to_failed(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
          <li>1) One!!!</li>
          <li>2) Two...</li>
          <li>3) Three???</li>
        </ul>
        '''
    )

    # have.exact_text
    browser.all('li').first.should(have.exact_text('1) One!!!'))
    browser.all('li').first.should(have.exact_text('1) one!!!').ignore_case)
    try:
        browser.all('li').first.should(have.exact_text('One'))
        pytest.fail('expected text mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li'))[0].has exact text One\n"
            '\n'
            'Reason: ConditionMismatch: actual text: 1) One!!!\n'
        ) in str(error)
    try:
        browser.all('li').first.should(have.exact_text('one').ignore_case)
        pytest.fail('expected text mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li'))[0].has exact text ignoring case: one\n"
            '\n'
            'Reason: ConditionMismatch: actual text: 1) One!!!\n'
        ) in str(error)
    # - inverted
    # - - with no before
    browser.all('li').first.should(have.no.exact_text('One'))
    try:
        browser.all('li').first.should(have.no.exact_text('1) One!!!'))
        pytest.fail('expected text mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li'))[0].has no (exact text 1) One!!!)\n"
            '\n'
            'Reason: ConditionMismatch: actual text: 1) One!!!\n'
        ) in str(error)
    browser.all('li').first.should(have.no.exact_text('one').ignore_case)
    try:
        browser.all('li').first.should(have.no.exact_text('1) one!!!').ignore_case)
        pytest.fail('expected text mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li'))[0].has no (exact text ignoring case: 1) one!!!)\n"
            '\n'
            'Reason: ConditionMismatch: actual text: 1) One!!!\n'
        ) in str(error)
    # - - with not after
    browser.all('li').first.should(have.exact_text('One').not_)
    try:
        browser.all('li').first.should(have.exact_text('1) One!!!').not_)
        pytest.fail('expected text mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li'))[0].has no (exact text 1) One!!!)\n"
            '\n'
            'Reason: ConditionMismatch: actual text: 1) One!!!\n'
        ) in str(error)
    browser.all('li').first.should(have.exact_text('one').ignore_case.not_)
    try:
        browser.all('li').first.should(have.exact_text('1) One!!!').ignore_case.not_)
        pytest.fail('expected text mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li'))[0].has no (exact text ignoring case: 1) One!!!)\n"
            '\n'
            'Reason: ConditionMismatch: actual text: 1) One!!!\n'
        ) in str(error)


def test_texts__including_ignorecase__passed_compared_to_failed(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
          <li>1) One!!!</li>
          <li>2) Two...</li>
          <li>3) Three???</li>
        </ul>
        '''
    )

    # have.texts
    browser.all('li').should(have.texts('One', 'Two', 'Three'))
    try:
        browser.all('li').should(have.texts('one', 'two', 'three'))
        pytest.fail('expected text mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li')).have texts ('one', "
            "'two', 'three')\n"
            '\n'
            "Reason: ConditionMismatch: actual visible texts: ['1) One!!!', '2) Two...', '3) "
            "Three???']\n"
        ) in str(error)
    # - inverted
    browser.all('li').should(have.no.texts('one', 'two', 'three'))
    browser.all('li').should(have.texts('one', 'two', 'three').not_)
    try:
        browser.all('li').should(have.no.texts('One', 'Two', 'Three'))
        pytest.fail('expected mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li')).have no (texts ('One', "
            "'Two', 'Three'))\n"
            '\n'
            "Reason: ConditionMismatch: actual visible texts: ['1) One!!!', '2) Two...', '3) "
            "Three???']\n"
        ) in str(error)
    # have.texts (ignore_case)
    browser.all('li').should(match.texts('one', 'two', 'three', _ignore_case=True))
    browser.all('li').should(have.texts('one', 'two', 'three').ignore_case)
    try:
        browser.all('li').should(have.texts('one.', 'two.', 'three.').ignore_case)
        pytest.fail('expected text mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li')).have texts ignoring case: ('one.', "
            "'two.', 'three.')\n"
            '\n'
            "Reason: ConditionMismatch: actual visible texts: ['1) One!!!', '2) Two...', '3) "
            "Three???']\n"
        ) in str(error)
    # - inverted
    # - - with no before
    browser.all('li').should(have.no.texts('one.', 'two.', 'three.').ignore_case)
    try:
        browser.all('li').should(have.no.texts('one', 'two', 'three').ignore_case)
        pytest.fail('expected mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li')).have no (texts ignoring case: ('one', "
            "'two', 'three'))\n"
            '\n'
            "Reason: ConditionMismatch: actual visible texts: ['1) One!!!', '2) Two...', '3) "
            "Three???']\n"
        ) in str(error)
    # - - with not after, in the end
    #     (in the middle works but without Autocomplete & not recommended)
    browser.all('li').should(have.texts('one.', 'two.', 'three.').ignore_case.not_)
    try:
        browser.all('li').should(have.texts('one', 'two', 'three').ignore_case.not_)
        pytest.fail('expected mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li')).have no (texts ignoring case: ('one', "
            "'two', 'three'))\n"
            '\n'
            "Reason: ConditionMismatch: actual visible texts: ['1) One!!!', '2) Two...', '3) "
            "Three???']\n"
        ) in str(error)


def test_exact_texts__including_ignorecase__passed_compared_to_failed(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
          <li>1) One!!!</li>
          <li>2) Two...</li>
          <li>3) Three???</li>
        </ul>
        '''
    )

    # have.exact_texts
    browser.all('li').should(have.exact_texts('1) One!!!', '2) Two...', '3) Three???'))
    try:
        browser.all('li').should(have.exact_texts('One', 'Two', 'Three'))
        pytest.fail('expected text mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li')).have exact texts ('One', 'Two', "
            "'Three')\n"
            '\n'
            "Reason: ConditionMismatch: actual visible texts: ['1) One!!!', '2) Two...', '3) "
            "Three???']\n"
        ) in str(error)
    # - inverted
    browser.all('li').should(have.no.exact_texts('one', 'Two', 'Three'))
    browser.all('li').should(have.exact_texts('One', 'Two', 'Three').not_)
    try:
        browser.all('li').should(
            have.no.exact_texts('1) One!!!', '2) Two...', '3) Three???')
        )
        pytest.fail('expected mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li')).have no (exact texts ('1) One!!!', '2) "
            "Two...', '3) Three???'))\n"
            '\n'
            "Reason: ConditionMismatch: actual visible texts: ['1) One!!!', '2) Two...', '3) "
            "Three???']\n"
        ) in str(error)
    # have.texts (ignore_case)
    browser.all('li').should(
        match.exact_texts('1) one!!!', '2) two...', '3) three???', _ignore_case=True)
    )
    browser.all('li').should(
        have.exact_texts('1) one!!!', '2) two...', '3) three???').ignore_case
    )
    try:
        browser.all('li').should(have.exact_texts('one.', 'two.', 'three.').ignore_case)
        pytest.fail('expected mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li')).have exact texts ignoring case: ('one.', "
            "'two.', 'three.')\n"
            '\n'
            "Reason: ConditionMismatch: actual visible texts: ['1) One!!!', '2) Two...', '3) "
            "Three???']\n"
        ) in str(error)
    # - inverted
    # - - with no before
    browser.all('li').should(have.no.exact_texts('one.', 'two.', 'three.').ignore_case)
    try:
        browser.all('li').should(
            have.no.exact_texts('1) one!!!', '2) two...', '3) three???').ignore_case
        )
        pytest.fail('expected mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li')).have no (exact texts ignoring case: ('1) "
            "one!!!', '2) two...', '3) three???'))\n"
            '\n'
            "Reason: ConditionMismatch: actual visible texts: ['1) One!!!', '2) Two...', '3) "
            "Three???']\n"
        ) in str(error)
    # - - with not after, in the end
    #     (in the middle works but without Autocomplete & not recommended)
    browser.all('li').should(
        have.exact_texts('one.', 'two.', 'three.').ignore_case.not_
    )
    try:
        browser.all('li').should(
            have.exact_texts('1) one!!!', '2) two...', '3) three???').ignore_case.not_
        )
        pytest.fail('expected mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li')).have no (exact texts ignoring case: ('1) "
            "one!!!', '2) two...', '3) three???'))\n"
            '\n'
            "Reason: ConditionMismatch: actual visible texts: ['1) One!!!', '2) Two...', '3) "
            "Three???']\n"
        ) in str(error)
