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

# TODO: review tests: clean up, add more cases if needed, break down into smaller tests,
#       find better names for tests


def test_text_matching__regex_pattern__compared(
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

    # in addition to:
    browser.all('li').first.should(have.text('One'))
    # this would be an alternative to previous match, but via regex:
    browser.all('li').first.should(have.text_matching(r'.*One.*'))
    # or
    browser.all('li').first.should(match.text_pattern(r'.*One.*'))
    # with matching whole text not just part (kind of implicit ^ and $):
    browser.all('li').first.should(have.no.text_matching(r'One'))
    # or
    browser.all('li').first.should(match.text_pattern(r'One').not_)
    # With regular regex powerful features:
    browser.all('li').first.should(have.text_matching(r'\d\) One(.)\1\1'))
    # ^ and $ can be used but don't add much value, cause work same as previous
    browser.all('li').first.should(have.text_matching(r'^\d\) One(.)\1\1$'))

    # there is also a similar collection condition that
    # matches each pattern to each element text in the collection
    # in the corresponding order:
    browser.all('li').should(have.texts_matching(r'\d\) One!+', r'.*', r'.*'))
    # that is also equivalent to:
    browser.all('li').should(have._texts_like(r'\d\) One(.)\1\1', ..., ...).with_regex)
    # or even:
    browser.all('li').should(
        have._texts_like(r'\d\) One(.)\1\1', (...,)).with_regex  # = one or more
    )
    # And with smart approach you can mix to achieve more with less:
    browser.all('li')[:3].should(have.text_matching(r'\d\) \w+(.)\1\1').each)


def test_text_matching__regex_pattern__error_message(
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

    try:
        browser.all('li').first.should(have.text_matching(r'\d\) ONE(.)\1\1'))
        pytest.fail('expected text mismatch')
    except AssertionError as error:
        assert (
            'Timed out after 0.1s, while waiting for:\n'
            "browser.all(('css selector', 'li'))[0].has text matching \\d\\) "
            'ONE(.)\\1\\1\n'
            '\n'
            'Reason: AssertionError: actual text: 1) One!!!\n'
            'Screenshot: '
        ) in str(error)

    try:
        browser.all('li').first.should(have.no.text_matching(r'\d\) One(.)\1\1'))
        pytest.fail('expected text match')
    except AssertionError as error:
        assert (
            'Timed out after 0.1s, while waiting for:\n'
            "browser.all(('css selector', 'li'))[0].has no (text matching \\d\\) "
            'One(.)\\1\\1)\n'
            '\n'
            'Reason: ConditionNotMatchedError: condition not matched\n'
            'Screenshot: '
        ) in str(error)
