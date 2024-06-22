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
import re

import pytest
from selene import have
from selene.core import match
from tests.integration.helpers.givenpage import GivenPage

# TODO: review tests: clean up, add more cases if needed, break down into smaller tests,
#       find better names for tests
#       add more tests for re.DOTALL flag


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
    browser.all('li').should(have.texts_matching(r'\d\) One!+', r'.*', r'.*').not_.not_)
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
            'Reason: ConditionMismatch: actual text: 1) One!!!\n'
            'Screenshot: '
        ) in str(error)

    try:
        browser.all('li').first.should(have.no.text_matching(r'\d\) One(.)\1\1'))
        pytest.fail('expected text match')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li'))[0].has no (text matching \\d\\) "
            'One(.)\\1\\1)\n'
            '\n'
            'Reason: ConditionMismatch: actual text: 1) One!!!\n'
        ) in str(error)


def test_text_matching__regex_pattern__ignore_case__compared(session_browser):
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

    browser.all('li').first.should(have.no.text_matching(r'.*one.*'))
    browser.all('li').first.should(match.exact_text('1) one!!!').not_)  # TODO: o_O
    browser.all('li').first.should(have.no.exact_text('1) one!!!'))
    # browser.all('li').first.should(have.no.exact_text('1) one!!!').ignore_case)  # TODO: check this fail with error
    browser.all('li').first.should(match.exact_text('1) one!!!', _ignore_case=True))
    browser.all('li').first.should(have.exact_text('1) one!!!').ignore_case)
    browser.all('li').first.should(match.text('one', _ignore_case=True))
    browser.all('li').first.should(have.text('one').ignore_case)
    browser.all('li').first.should(match.text_pattern(r'.*one.*', _flags=re.IGNORECASE))
    browser.all('li').first.should(match.text_pattern(r'.*one.*').not_)
    browser.all('li').first.should(
        match.text_pattern(r'.*one.*', _flags=re.IGNORECASE).not_.not_
    )
    browser.all('li').first.should(have.text_matching(r'.*one.*').ignore_case)
    browser.all('li').first.should(
        have.text_matching(r'.*one.*').where_flags(re.IGNORECASE)
    )
    browser.all('li').first.should(
        have.text_matching(r'.*one.*').where_flags(re.IGNORECASE | re.DOTALL)
    )
    browser.all('li').should(
        match._text_patterns(r'.*one.*', r'.*two.*', '.*three.*', _flags=re.IGNORECASE)
    )
    browser.all('li').should(
        have.texts_matching(r'.*one.*', r'.*two.*', '.*three.*').ignore_case
    )
    # # TODO: implement
    # browser.all('li').should(have.texts('one', 'two', 'three').ignore_case)
    # browser.all('li').should(
    #     have.exact_texts('1) One!!!', '2) Two...', '3) Three???').ignore_case
    # )
    browser.all('li').should(
        match._text_patterns_like(r'.*one.*', r'.*two.*', ..., _flags=re.IGNORECASE)
    )
    # do we even neet a prefix here? like where_? why not just .flage(...) ?
    browser.all('li').should(
        have._text_patterns_like(r'.*one.*', r'.*two.*', ...).where_flags(re.IGNORECASE)
    )
    browser.all('li').should(  # TODO: ensure error messages
        have._text_patterns_like(r'.*one.*', r'.*two.*', ...).ignore_case
    )
    # # we used already where_wildcards, so with_ prefix would be less consistent
    # # we used with_ only in .with_regex that is a property, without params
    # # i.e. with_ was used in "define" context not in "redefine/override" context
    # browser.all('li').should(
    #     have._text_patterns_like(r'.*one.*', r'.*two.*', ...).with_flags(re.IGNORECASE)
    # )
    browser.all('li').should(
        have._texts_like(r'.*one.*', r'.*two.*', ...).with_regex.where_flags(
            re.IGNORECASE
        )
    )
    browser.all('li').should(
        have._texts_like(r'.*one.*', r'.*two.*', ...).with_regex.ignore_case
    )
    # possible but without Autocomplete:
    browser.all('li').should(
        have._texts_like(r'.*one.*', r'.*two.*', ...).ignore_case.with_regex
    )
    browser.all('li').should(
        have.no._texts_like(r'*one*', r'*two*', ...).where_wildcards(
            zero_or_more_chars='*'
        )
    )
    browser.all('li').should(
        have._exact_texts_like('1) one!!!', '2) two...', ...).ignore_case
    )
    # wildcards but without ignorecase (just to compare and double check)
    browser.all('li').should(
        have._texts_like(r'*One*', r'*Two*', ...).where_wildcards(
            zero_or_more_chars='*'
        )
    )
    # + explicit flags after
    browser.all('li').should(
        have._texts_like(r'*one*', r'*two*', ...)
        .where_wildcards(zero_or_more_chars='*')
        .where_flags(re.IGNORECASE | re.DOTALL)
    )
    # now ignore case before, maybe less readable
    # because "wildcards explanation is postponed now to the end of phrase"
    browser.all('li').should(
        have._texts_like(r'*one*', r'*two*', ...).ignore_case.where_wildcards(
            zero_or_more_chars='*'
        )
    )
    # now ignore case after (seems like more readable)
    browser.all('li').should(
        have._texts_like(r'*one*', r'*two*', ...)
        .where_wildcards(zero_or_more_chars='*')
        .ignore_case
    )
    # Now with negated versions...
    # Most readable and recommended way to negate:
    # (ignore case before)
    browser.all('li').should(
        have.no._texts_like(r'*two*', r'*one*', ...).ignore_case.where_wildcards(
            zero_or_more_chars='*'
        )
    )
    # or with ignore case after
    browser.all('li').should(
        have.no._texts_like(r'*two*', r'*one*', ...)
        .where_wildcards(zero_or_more_chars='*')
        .ignore_case
    )
    # possible but without Autocomplete and not recommended:
    browser.all('li').should(
        have._texts_like(r'*two*', r'*one*', ...).not_.ignore_case.where_wildcards(
            zero_or_more_chars='*'
        )
    )
    # possible but without Autocomplete and not recommended:
    browser.all('li').should(
        have._texts_like(r'*two*', r'*one*', ...).ignore_case.not_.where_wildcards(
            zero_or_more_chars='*'
        )
    )
    # below all correct usdages with .not_ in the end
    browser.all('li').should(
        have._texts_like(r'*two*', r'*one*', ...).with_wildcards.not_
    )
    browser.all('li').should(
        have._texts_like(r'*two*', r'*one*', ...)
        .where_wildcards(zero_or_more_chars='*')
        .not_
    )
    browser.all('li').should(
        have._texts_like(r'*two*', r'*one*', ...)
        .where_wildcards(zero_or_more_chars='*')
        .ignore_case.not_
    )
    browser.all('li').should(
        have._texts_like(r'*two*', r'*one*', ...)
        .ignore_case.where_wildcards(zero_or_more_chars='*')
        .not_
    )
    # or with wrapped not (also correct)
    from selene.core.condition import not_

    browser.all('li').should(
        not_(
            have._texts_like(r'*two*', r'*one*', ...).ignore_case.where_wildcards(
                zero_or_more_chars='*'
            )
        )
    )

    try:
        browser.all('li').should(
            have._texts_like(r'*One*', r'*Two*', ...)
            .where_wildcards(zero_or_more_chars='*')
            .not_
        )
        pytest.fail('expected texts match')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li')).have no texts with wildcards like:\n"
            '    *One*, *Two*, ...\n'
            '\n'
            'Reason: AssertionError: actual visible texts:\n'
            '    1) One!!!, 2) Two..., 3) Three???\n'
            '\n'
            'Pattern used for matching:\n'
            '    ^.*?One.*?‚.*?Two.*?‚[^‚]+‚$\n'
            'Actual text used to match:\n'
            '    1) One!!!‚2) Two...‚3) Three???‚\n'
        ) in str(error)


def test_text_matching__regex_pattern__error__on_invalid_regex__with_ignorecase(
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
        browser.all('li').first.should(have.text_matching(r'*one*').ignore_case)
        pytest.fail('expected invalid regex error')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li'))[0].has text matching (with flags "
            're.IGNORECASE): *one*\n'
            '\n'
            'Reason: error: nothing to repeat at position '
            '0:\n'
            'actual text: 1) One!!!\n'
            'Screenshot: '
        ) in str(error)

    # TODO: decide on expected behavior
    try:
        browser.all('li').first.should(have.text_matching(r'*one*').ignore_case.not_)
        pytest.fail('expected invalid regex error')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li'))[0].has no (text matching (with flags "
            're.IGNORECASE): *one*)\n'
            '\n'
            'Reason: error: nothing to repeat at position '
            '0:\n'
            'actual text: 1) One!!!\n'
            'Screenshot: '
        ) in str(error)

    try:
        browser.all('li').first.should(have.no.text_matching(r'*one*').ignore_case)
        pytest.fail('expected invalid regex error')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li'))[0].has no (text matching (with flags "
            're.IGNORECASE): *one*)\n'
            '\n'
            'Reason: error: nothing to repeat at position '
            '0:\n'
            'actual text: 1) One!!!\n'
            'Screenshot: '
        ) in str(error)
