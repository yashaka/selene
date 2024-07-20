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
#       maybe some duplicates are ok, cause serves for comparison purposes


def test_text_patterns_like__mixed__with_regex_patterns_support(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
            <li>1) One...</li>
            <li>2) Two...</li>
            <li>3) Three...</li>
            <li>4) Four...</li>
            <li>5) Five...</li>
            <li>6) Six...</li>
            <li>7) Seven...</li>
            <li>8) Eight...</li>
            <li>9) Nine...</li>
            <li>X) Ten...</li>
        </ul>
        '''
    )

    # full regex support (^ and $ for each item text is kind of implicit)
    # – for item texts in addition to support of ellipsis globs as items placeholders
    browser.all('li').should(
        match._text_patterns_like(
            [{...}],
            r'.*?O.e.*?',
            {...},
            r'.*?Thr.+.*?',
            ...,
            r'.*?Six.*?',
            [...],
            r'.*?Ten.*?',
            [...],
        )
    )
    # with alias
    browser.all('li').should(
        have._text_patterns_like(
            [{...}],
            r'.*?O.e.*?',
            {...},
            r'.*?Thr.+.*?',
            ...,
            r'.*?Six.*?',
            [...],
            r'.*?Ten.*?',
            [...],
        )
    )
    # with one more alias
    browser.all('li').should(
        have._texts_like(
            [{...}],
            r'.*?O.e.*?',
            {...},
            r'.*?Thr.+.*?',
            ...,
            r'.*?Six.*?',
            [...],
            r'.*?Ten.*?',
            [...],
        ).with_regex
    )
    # without "_like" version will lack support of ellipsis globs as items placeholders
    browser.all('li').should(
        match._text_patterns(
            r'.*?O.e.*?',
            r'2\) Two\.\.\.',
            r'.*?Thr.+.*?',
            r'4\) Four\.\.\.',
            r'5\) Five\.\.\.?',
            r'.*?Six.*?',
            r'7\) Seven\.\.\.',
            r'8\) Eight\.\.\.',
            r'9\) Nine\.\.\.',
            r'.*?Ten.*?',
        )
    )
    browser.all('li').should(
        match._text_patterns(
            [{...}],
            r'.*?O.e.*?',
            {...},
            r'.*?Thr.+.*?',
            ...,
            r'.*?Six.*?',
            [...],
            r'.*?Ten.*?',
            [...],
        ).not_
    )
    # with alias
    browser.all('li').should(
        have.texts_matching(
            r'.*?O.e.*?',
            r'2\) Two\.\.\.',
            r'.*?Thr.+.*?',
            r'4\) Four\.\.\.',
            r'5\) Five\.\.\.?',
            r'.*?Six.*?',
            r'7\) Seven\.\.\.',
            r'8\) Eight\.\.\.',
            r'9\) Nine\.\.\.',
            r'.*?Ten.*?',
        )
    )


def test_text_patternss_like__mixed__with_regex_patterns_support__error_messages(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
            <li>1) One...</li>
            <li>2) Two...</li>
            <li>3) Three...</li>
            <li>4) Four...</li>
            <li>5) Five...</li>
            <li>6) Six...</li>
            <li>7) Seven...</li>
            <li>8) Eight...</li>
            <li>9) Nine...</li>
            <li>X) Ten...</li>
        </ul>
        '''
    )

    try:
        # full regex support (^ and $ for each item text is kind of implicit)
        # – for item texts in addition to support of ellipsis globs as items placeholders
        browser.all('li').should(
            have._text_patterns_like(
                [{...}],
                r'.*?O.e.*?',
                {...},
                r'.*?Three',  # fails on ending: 'Three' != 'Three...'
                ...,
                r'.*?Six.*?',
                [...],
                r'.*?Ten.*?',
                [...],
            )
        )
        pytest.fail('expected texts mismatch')
    except AssertionError as error:
        assert (
            'Message: \n'
            '\n'
            'Timed out after 0.1s, while waiting for:\n'
            "browser.all(('css selector', 'li')).have text patterns like:\n"
            '    [{...}], .*?O.e.*?, {...}, .*?Three, ..., .*?Six.*?, [...]), '
            '.*?Ten.*?, [...])\n'
            '\n'
            'Reason: AssertionError: actual visible texts:\n'
            '    1) One..., 2) Two..., 3) Three..., 4) Four..., 5) Five..., 6) Six..., 7) '
            'Seven..., 8) Eight..., 9) Nine..., X) Ten...\n'
            '\n'
            'Pattern used for matching:\n'
            '    ^[^‚]*‚?.*?O.e.*?‚[^‚]+‚.*?Three‚.+?‚.*?Six.*?‚.*?‚?.*?Ten.*?‚.*?‚?$\n'
            'Actual text used to match:\n'
            '    1) One...‚2) Two...‚3) Three...‚4) Four...‚5) Five...‚6) Six...‚7) '
            'Seven...‚8) Eight...‚9) Nine...‚X) Ten...‚\n'
            'Screenshot: '
        ) in str(error)

    # with an alias
    try:
        browser.all('li').should(
            have._texts_like(
                [{...}],
                r'.*?O.e.*?',
                {...},
                r'.*?Three',  # fails on ending: 'Three' != 'Three...'
                ...,
                r'.*?Six.*?',
                [...],
                r'.*?Ten.*?',
                [...],
            ).with_regex
        )
        pytest.fail('expected texts mismatch')
    except AssertionError as error:
        assert ".have text patterns like:\n" in str(error)

    # without "_like" version will lack support of ellipsis globs as items placeholders
    try:
        browser.all('li').should(
            have.texts_matching(
                r'^.*?O.e.*?$',  # fails on syntax: '^' and '$' should be implicit
                r'2\) Two\.\.\.',
                r'.*?Thr.+.*?',
                r'4\) Four\.\.\.',
                r'5\) Five\.\.\.?',
                r'.*?Six.*?',
                r'7\) Seven\.\.\.',
                r'8\) Eight\.\.\.',
                r'9\) Nine\.\.\.',
                r'.*?Ten.*?',
            )
        )
        pytest.fail('expected texts mismatch')
    except AssertionError as error:
        assert ".have text patterns:\n" in str(error)

    try:
        browser.all('li').should(
            have.texts_matching(
                r'.*?O.e.*?',
                r'2\) Two\.\.\.',
                r'.*?Thr.+.*?',
                r'4\) Four\.\.\.',
                r'5\) Five\.\.\.?',
                r'.*?Six.*?',
                r'7\) Seven\.\.\.',
                r'8\) Eight\.\.\.',
                r'9\) Nine\.\.\.',
                r'.*?Ten.*?',
            ).not_  # fails here because without not_ it matches
        )
        pytest.fail('expected texts mismatch')
    except AssertionError as error:
        assert ".have no text patterns:\n" in str(error)


def test_text_patterns_like__mixed__with_implicit_wildcards_patterns_support(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
            <li>1) One...</li>
            <li>2) Two...</li>
            <li>3) Three...</li>
            <li>4) Four...</li>
            <li>5) Five...</li>
            <li>6) Six...</li>
            <li>7) Seven...</li>
            <li>8) Eight...</li>
            <li>9) Nine...</li>
            <li>X) Ten...</li>
        </ul>
        '''
    )

    # for the most common case (similar to classic have.texts)...
    browser.all('li').should(
        match._text_patterns_like(
            [{...}],
            r'.*?One.*?',
            {...},
            r'.*?Three.*?',
            ...,
            r'.*?Six.*?',
            [...],
            r'.*?Ten.*?',
            [...],
        )
    )
    # – there is a shortcut:
    browser.all('li').should(
        have._texts_like(
            [{...}],
            'One',
            {...},
            'Three',
            ...,
            'Six',
            [...],
            'Ten',
            [...],
        )
    )
    browser.all('li').should(
        have.no._texts_like(
            [{...}],
            'Two',  # does NOT match: 'Two' != 'One'
            {...},
            'Three',
            ...,
            'Six',
            [...],
            'Ten',
            [...],
        )
    )


def test_texts_like__mixed__with_implicit_wildcards_patterns_support__with_errors(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
            <li>1) One...</li>
            <li>2) Two...</li>
            <li>3) Three...</li>
            <li>4) Four...</li>
            <li>5) Five...</li>
            <li>6) Six...</li>
            <li>7) Seven...</li>
            <li>8) Eight...</li>
            <li>9) Nine...</li>
            <li>X) Ten...</li>
        </ul>
        '''
    )

    try:
        browser.all('li').should(
            have._texts_like(
                [{...}],
                'ONE',  # fails here: 'ONE' != 'One'
                {...},
                'Three',
                ...,
                'Six',
                [...],
                'Ten',
                [...],
            )
        )
        pytest.fail('expected texts mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li')).have texts like:\n"
            '    [{...}], ONE, {...}, Three, ..., Six, [...]), Ten, [...])\n'
            '\n'
            'Reason: AssertionError: actual visible texts:\n'
            '    1) One..., 2) Two..., 3) Three..., 4) Four..., 5) Five..., 6) Six..., 7) '
            'Seven..., 8) Eight..., 9) Nine..., X) Ten...\n'
            '\n'
            'Pattern used for matching:\n'
            '    ^[^‚]*‚?.*?ONE.*?‚[^‚]+‚.*?Three.*?‚.+?‚.*?Six.*?‚.*?‚?.*?Ten.*?‚.*?‚?$\n'
            'Actual text used to match:\n'
            '    1) One...‚2) Two...‚3) Three...‚4) Four...‚5) Five...‚6) Six...‚7) '
            'Seven...‚8) Eight...‚9) Nine...‚X) Ten...‚\n'
        ) in str(error)


def test_texts_like__mixed__with_explicit_wildcards_patterns_support(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
            <li>1) One...</li>
            <li>2) Two...</li>
            <li>3) Three...</li>
            <li>4) Four...</li>
            <li>5) Five...</li>
            <li>6) Six...</li>
            <li>7) Seven...</li>
            <li>8) Eight...</li>
            <li>9) Nine...</li>
            <li>X) Ten...</li>
        </ul>
        '''
    )

    # .with_wildcards overrides default behavior
    browser.all('li').should(
        have.no._texts_like(
            [{...}],
            'One',  # does not match cause correct pattern '*One*' != 'One'
            {...},
            'Three',
            ...,
            'Six',
            [...],
            'Ten',
            [...],
        ).with_wildcards
    )
    browser.all('li').should(
        have._texts_like(
            [{...}],
            '*O?e*',
            {...},
            '*T??ee*',
            ...,
            '*Six*',
            [...],
            '*Ten*',
            [...],
        ).with_wildcards
    )
    browser.all('li').should(
        have.no._texts_like(
            [{...}],
            '*O?e*',
            {...},
            '*T???ee*',  # does not match: 'Three' != 'Th?ree'
            ...,
            '*Six*',
            [...],
            '*Ten*',
            [...],
        ).with_wildcards
    )


def test_texts_like__mixed__with_explicit_wildcards_patterns_support__with_errors(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
            <li>1) One...</li>
            <li>2) Two...</li>
            <li>3) Three...</li>
            <li>4) Four...</li>
            <li>5) Five...</li>
            <li>6) Six...</li>
            <li>7) Seven...</li>
            <li>8) Eight...</li>
            <li>9) Nine...</li>
            <li>X) Ten...</li>
        </ul>
        '''
    )

    try:
        browser.all('li').should(
            have._texts_like(
                [{...}],
                'One',  # does not match cause correct pattern '*One*' != 'One'
                {...},
                '*T??ee*',
                ...,
                '*Six*',
                [...],
                '*Ten*',
                [...],
            ).with_wildcards
        )
        pytest.fail('expected texts mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li')).have texts with wildcards like:\n"
            '    [{...}], One, {...}, *T??ee*, ..., *Six*, [...]), *Ten*, [...])\n'
            '\n'
            'Reason: AssertionError: actual visible texts:\n'
            '    1) One..., 2) Two..., 3) Three..., 4) Four..., 5) Five..., 6) Six..., 7) '
            'Seven..., 8) Eight..., 9) Nine..., X) Ten...\n'
            '\n'
            'Pattern used for matching:\n'
            '    ^[^‚]*‚?One‚[^‚]+‚.*?T..ee.*?‚.+?‚.*?Six.*?‚.*?‚?.*?Ten.*?‚.*?‚?$\n'
            'Actual text used to match:\n'
            '    1) One...‚2) Two...‚3) Three...‚4) Four...‚5) Five...‚6) Six...‚7) '
            'Seven...‚8) Eight...‚9) Nine...‚X) Ten...‚\n'
        ) in str(error)


def test_texts_like__mixed__where_custom_wildcards_patterns_support(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
            <li>1) One...</li>
            <li>2) Two...</li>
            <li>3) Three...</li>
            <li>4) Four...</li>
            <li>5) Five...</li>
            <li>6) Six...</li>
            <li>7) Seven...</li>
            <li>8) Eight...</li>
            <li>9) Nine...</li>
            <li>X) Ten...</li>
        </ul>
        '''
    )

    # .with_wildcards customized overrides default (no-wildcards) behavior
    browser.all('li').should(
        have.no._texts_like(
            [{...}],
            'One',
            {...},
            'Three',
            ...,
            'Six',
            [...],
            'Ten',
            [...],
        ).where_wildcards(zero_or_more_chars='**', exactly_one_char='_')
    )
    # .with_wildcards customized overrides default explicit-wildcards behavior
    browser.all('li').should(
        have.no._texts_like(
            [{...}],
            '*O?e*',
            {...},
            '*T??ee*',
            ...,
            '*Six*',
            [...],
            '*Ten*',
            [...],
        ).where_wildcards(zero_or_more_chars='**', exactly_one_char='_')
    )
    # TODO: isn't it not obvious? the context is a bit different from .where...
    #       it's also different from entity.with(**options),
    #       where not all options are overriden but just passed ones...
    #       but maybe here we say with_WILDCARDS and then we specify all wildcards...
    #       hm... maybe then ok...
    # even one overrides everything
    browser.all('li').should(
        have.no._texts_like(
            [{...}],
            '**One**',
            {...},
            '**T??ee**',  # now are not considered as wildcards = does not match
            ...,
            '**Six**',
            [...],
            '**Ten**',
            [...],
        ).where_wildcards(zero_or_more_chars='**')
    )
    # even one overrides everything
    browser.all('li').should(
        have._texts_like(
            [{...}],
            '**One**',
            {...},
            '**Three**',  # now are not considered as wildcards = does not match
            ...,
            '**Six**',
            [...],
            '**Ten**',
            [...],
        ).where_wildcards(zero_or_more_chars='**')
    )
    browser.all('li').should(
        have._texts_like(
            [{...}],
            '**O_e**',
            {...},
            '**T__ee**',
            ...,
            '**Six**',
            [...],
            '**Ten**',
            [...],
        ).where_wildcards(zero_or_more_chars='**', exactly_one_char='_')
    )


def test_texts_like__mixed__where_custom_wildcards_patterns_support__with_errors(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
            <li>1) One...</li>
            <li>2) Two...</li>
            <li>3) Three...</li>
            <li>4) Four...</li>
            <li>5) Five...</li>
            <li>6) Six...</li>
            <li>7) Seven...</li>
            <li>8) Eight...</li>
            <li>9) Nine...</li>
            <li>X) Ten...</li>
        </ul>
        '''
    )

    try:
        browser.all('li').should(
            have.no._texts_like(  # fails here because actually matches without no
                [{...}],
                '**O_e**',
                {...},
                '**T__ee**',
                ...,
                '**Six**',
                [...],
                '**Ten**',
                [...],
            ).where_wildcards(zero_or_more_chars='**', exactly_one_char='_')
        )
        pytest.fail('expected condition mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li')).have no texts with wildcards like:\n"
        ) in str(error)


def test_texts_matching__regex_pattern__error__on_invalid_regex(session_browser):
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
        browser.all('li').should(have._texts_like(r'*One.*', {...}, {...}).with_regex)
        pytest.fail('expected invalid regex error')
    except AssertionError as error:
        assert (
            'Timed out after 0.1s, while waiting for:\n'
            "browser.all(('css selector', 'li')).have text patterns like:\n"
            '    *One.*, {...}, {...}\n'
            '\n'
            'Reason: AssertionError:  RegexError: nothing to repeat at position 1\n'
            'actual visible texts:\n'
            '    1) One!!!, 2) Two..., 3) Three???\n'
            '\n'
            'Pattern used for matching:\n'
            '    ^*One.*‚[^‚]+‚[^‚]+‚$\n'
            'Actual text used to match:\n'
            '    1) One!!!‚2) Two...‚3) Three???‚\n'
        ) in str(error)


def test_texts_matching__regex_pattern__ignore_case_error__on_invalid_regex(
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
        browser.all('li').should(
            have._texts_like(r'*one.*', {...}, {...}).with_regex.ignore_case.not_
        )
        pytest.fail('expected invalid regex error')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li')).have no text patterns like (flags: "
            're.IGNORECASE):\n'
            '    *one.*, {...}, {...}\n'
            '\n'
            'Reason: AssertionError:  RegexError: nothing to repeat at position 1\n'
            'actual visible texts:\n'
            '    1) One!!!, 2) Two..., 3) Three???\n'
            '\n'
            'Pattern used for matching:\n'
            '    ^*one.*‚[^‚]+‚[^‚]+‚$\n'
            'Actual text used to match:\n'
            '    1) One!!!‚2) Two...‚3) Three???‚\n'
        ) in str(error)


def test_texts_like__including_ignorecase__passed_compared_to_failed(
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

    # have.texts_like
    browser.all('li').should(have._texts_like('One', {...}, {...}))
    try:
        browser.all('li').should(have._texts_like('one', {...}, {...}))
        pytest.fail('expected text mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li')).have texts like:\n"
            '    one, {...}, {...}\n'
            '\n'
            'Reason: AssertionError: actual visible texts:\n'
            '    1) One!!!, 2) Two..., 3) Three???\n'
            '\n'
            'Pattern used for matching:\n'
            '    ^.*?one.*?‚[^‚]+‚[^‚]+‚$\n'
            'Actual text used to match:\n'
            '    1) One!!!‚2) Two...‚3) Three???‚\n'
        ) in str(error)
    # - inverted
    browser.all('li').should(have.no._texts_like('one', {...}, {...}))
    browser.all('li').should(have._texts_like('one', {...}, {...}).not_)
    try:
        browser.all('li').should(have.no._texts_like('One', {...}, {...}))
        pytest.fail('expected mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li')).have no texts like:\n"
            '    One, {...}, {...}\n'
            '\n'
            'Reason: AssertionError: actual visible texts:\n'
            '    1) One!!!, 2) Two..., 3) Three???\n'
            '\n'
            'Pattern used for matching:\n'
            '    ^.*?One.*?‚[^‚]+‚[^‚]+‚$\n'
            'Actual text used to match:\n'
            '    1) One!!!‚2) Two...‚3) Three???‚\n'
        ) in str(error)
    # have._texts_like (ignore_case)
    browser.all('li').should(
        match._texts_like('one', {...}, {...}, _flags=re.IGNORECASE)
    )
    browser.all('li').should(have._texts_like('one', {...}, {...}).ignore_case)
    try:
        browser.all('li').should(have._texts_like('one.', {...}, {...}).ignore_case)
        pytest.fail('expected text mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li')).have texts like (flags: "
            're.IGNORECASE):\n'
            '    one., {...}, {...}\n'
            '\n'
            'Reason: AssertionError: actual visible texts:\n'
            '    1) One!!!, 2) Two..., 3) Three???\n'
            '\n'
            'Pattern used for matching:\n'
            '    ^.*?one\\..*?‚[^‚]+‚[^‚]+‚$\n'
            'Actual text used to match:\n'
            '    1) One!!!‚2) Two...‚3) Three???‚\n'
        ) in str(error)
    # - double inversion == no inversion
    browser.all('li').should(
        match._texts_like('one', {...}, {...}, _flags=re.IGNORECASE).not_.not_
    )
    browser.all('li').should(have.no._texts_like('one', {...}, {...}).ignore_case.not_)
    try:
        browser.all('li').should(
            have.no._texts_like('one.', {...}, {...}).ignore_case.not_
        )
        pytest.fail('expected text mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li')).have texts like (flags: "
            're.IGNORECASE):\n'
            '    one., {...}, {...}\n'
            '\n'
            'Reason: AssertionError: actual visible texts:\n'
            '    1) One!!!, 2) Two..., 3) Three???\n'
            '\n'
            'Pattern used for matching:\n'
            '    ^.*?one\\..*?‚[^‚]+‚[^‚]+‚$\n'
            'Actual text used to match:\n'
            '    1) One!!!‚2) Two...‚3) Three???‚\n'
        ) in str(error)
    # - inverted
    # - - with no before
    browser.all('li').should(have.no._texts_like('one.', {...}, {...}).ignore_case)
    try:
        browser.all('li').should(have.no._texts_like('one', {...}, {...}).ignore_case)
        pytest.fail('expected mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li')).have no texts like (flags: "
            're.IGNORECASE):\n'
            '    one, {...}, {...}\n'
            '\n'
            'Reason: AssertionError: actual visible texts:\n'
            '    1) One!!!, 2) Two..., 3) Three???\n'
            '\n'
            'Pattern used for matching:\n'
            '    ^.*?one.*?‚[^‚]+‚[^‚]+‚$\n'
            'Actual text used to match:\n'
            '    1) One!!!‚2) Two...‚3) Three???‚\n'
        ) in str(error)
    # - - with not after, in the end
    #     (in the middle works but without Autocomplete & not recommended)
    browser.all('li').should(have._texts_like('one.', {...}, {...}).ignore_case.not_)
    try:
        browser.all('li').should(have._texts_like('one', {...}, {...}).ignore_case.not_)
        pytest.fail('expected mismatch')
    except AssertionError as error:
        assert (
            "browser.all(('css selector', 'li')).have no texts like (flags: "
            're.IGNORECASE):\n'
            '    one, {...}, {...}\n'
            '\n'
            'Reason: AssertionError: actual visible texts:\n'
            '    1) One!!!, 2) Two..., 3) Three???\n'
            '\n'
            'Pattern used for matching:\n'
            '    ^.*?one.*?‚[^‚]+‚[^‚]+‚$\n'
            'Actual text used to match:\n'
            '    1) One!!!‚2) Two...‚3) Three???‚\n'
        ) in str(error)
