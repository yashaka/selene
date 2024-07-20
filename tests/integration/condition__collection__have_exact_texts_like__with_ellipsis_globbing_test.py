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
from selene.core.exceptions import TimeoutException
from tests.integration.helpers.givenpage import GivenPage

# TODO: review tests: clean up, add more cases if needed, break down into smaller tests


def test_should_have_exact_texts_like__does_not_match_merged_with_comma_items(
    session_browser,
):
    browser = session_browser.with_(timeout=0.25)
    li = browser.all('li')
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>1</li>
           <li>2, 3</li>
           <li>4</li>
           <li>5</li>
           <li>6</li>
           <li>7</li>
           <li>8</li>
           <li>9</li>
           <li>X</li>
        </ul>
        '''
    )
    X = 'X'

    # WHEN
    have_exact_texts = lambda *values: have._exact_texts_like(*values).where(
        one_or_more=...
    )
    have_no_exact_texts = have.no._exact_texts_like

    # THEN
    li.should(have_no_exact_texts(1, 2, 3, 4, 5, 6, 7, 8, 9, X))
    li.should(have_no_exact_texts(1, 2, 3, 4, 5, 6, 7, 8, 9, X))
    li.should(have_no_exact_texts(1, '2, 3', '4, 5', 6, 7, 8, 9, X))


def test_should_have_exact_texts_and_no_exact_texts__with_custom_one_or_more_extensive(
    session_browser,
):
    browser = session_browser.with_(timeout=0.25)
    li = browser.all('li')
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>1</li>
           <li>2</li>
           <li>3</li>
           <li>4</li>
           <li>5</li>
           <li>6</li>
           <li>7</li>
           <li>8</li>
           <li>9</li>
           <li>X</li>
        </ul>
        '''
    )
    X = 'X'
    # AND just a simple check to ensure normal have.exact_texts works
    li.should(have.exact_texts('1', '2', '3', '4', '5', '6', '7', '8', '9', X))
    li.should(have.exact_texts(1, 2, 3, 4, 5, 6, 7, 8, 9, X))

    # WHEN
    have_exact_texts = lambda *values: have._exact_texts_like(*values).where(
        one_or_more=...
    )
    have_no_exact_texts = have.no._exact_texts_like

    # THEN
    li.should(have_exact_texts('1', '2', '3', '4', '5', '6', '7', '8', '9', X))
    li.should(have_exact_texts(1, 2, 3, 4, 5, 6, 7, 8, 9, X))
    li.should(have_no_exact_texts(1, ..., '3, 4', 5, 6, 7, 8, 9, X))

    li.should(have_no_exact_texts(..., 1, 2, 3, 4, 5, 6, 7, 8, 9, X))
    li.should(have_no_exact_texts(1, 2, 3, 4, 5, 6, 7, 8, 9, X, ...))
    li.should(have_no_exact_texts(..., 1, 2, 3, 4, 5, 6, 7, 8, 9, X, ...))
    li.should(have_exact_texts(..., 2, 3, 4, 5, 6, 7, 8, 9, X))
    li.should(have_no_exact_texts(..., 2, 3, 4, 5, 6, 7, 8, 9, X, ...))
    li.should(have_exact_texts(1, 2, 3, 4, 5, 6, 7, 8, 9, ...))
    li.should(have_no_exact_texts(..., 1, 2, 3, 4, 5, 6, 7, 8, 9, ...))
    li.should(have_exact_texts(1, 2, 3, 4, 5, ..., 7, 8, 9, X))
    li.should(have_no_exact_texts(1, 2, 3, 4, 5, 7, 8, 9, X))
    li.should(have_exact_texts(1, 2, 3, 4, ..., ..., 7, 8, 9, X))  # valid but redundant
    li.should(have_exact_texts(1, 2, 3, 4, ..., 7, 8, 9, X))  # same as previous
    li.should(have_no_exact_texts(2, 3, 4, ..., 7, 8, 9, X))
    li.should(have_no_exact_texts(1, 2, 3, 4, ..., 7, 8, 9))
    li.should(have_exact_texts(..., 2, 3, 4, ..., 7, 8, 9, ...))
    li.should(have_exact_texts(..., 2, ..., 4, ..., 7, ..., 9, ...))
    li.should(have_no_exact_texts(..., 2, ..., 4, ..., 7, 9, ...))
    li.should(have_no_exact_texts(..., 2, 4, ..., 7, ..., 9, ...))
    li.should(have_no_exact_texts(..., 2, 4, ..., 7, 9, ...))

    li.should(have_no_exact_texts(1, 2))
    li.should(have_exact_texts(1, 2, ...))
    li.should(have_no_exact_texts(2, 3, ...))
    li.should(have_exact_texts(..., 2, 3, ...))
    li.should(have_no_exact_texts(1, 3, ...))
    li.should(have_exact_texts(1, ..., 3, ...))
    li.should(have_exact_texts(1, ..., 4, ...))

    li.should(have_no_exact_texts(9, X))
    li.should(have_exact_texts(..., 9, X))
    li.should(have_no_exact_texts(..., 8, 9))
    li.should(have_exact_texts(..., 8, 9, ...))
    li.should(have_no_exact_texts(..., 8, X))  # TODO: test how fails
    li.should(have_exact_texts(..., 8, ..., X))
    li.should(have_exact_texts(..., 7, ..., X))

    li.should(have_no_exact_texts(5, 6))
    li.should(have_no_exact_texts(5, 6, ...))
    li.should(have_no_exact_texts(..., 5, 6))
    li.should(have_exact_texts(..., 5, 6, ...))
    li.should(have_no_exact_texts(..., 5, ..., 6, ...))


def test_exact_texts_like__on__mixed_numbers_and_quoted_text__with_custom_one_or_more(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>1</li>
           <li>Two</li>
           <li>3</li>
           <li>4</li>
           <li>'Five'</li>
           <li>6</li>
           <li>'7'</li>
        </ul>
        '''
    )

    browser.all('li').should(
        have._exact_texts_like(..., 'Two', ..., 4, "'Five'", ...).where(one_or_more=...)
    )


def test_exact_texts_like__with_default_exactly_one_and_zero_or_more(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>Zero</li>
           <li>1</li>
           <li>Two</li>
           <li>3</li>
           <li>4</li>
           <li>'Five'</li>
           <li>6</li>
           <li>7</li>
        </ul>
        '''
    )

    browser.all('li').should(
        have._exact_texts_like(
            'Zero',
            1,
            'Two',
            [...],  # means zero or MORE and so does match 2 texts
            "'Five'",
            6,
            7,  # here list ends
        )
    )

    browser.all('li').should(
        have._exact_texts_like(
            {...},
            1,
            'Two',
            [...],  # means zero or MORE and so does match 2 texts
            "'Five'",
            6,
            '7',  # here list ends
        )
    )

    browser.all('li').should(
        have._exact_texts_like(
            {...},
            {...},
            'Two',
            [...],  # means zero or MORE and so does match 2 texts
            "'Five'",
            6,
            '7',
        )
    )

    browser.all('li').should(
        have._exact_texts_like(
            {...},
            {...},
            'Two',
            [...],  # means zero or MORE and so does match 2 texts
            "'Five'",
            {...},
            {...},
        )
    )

    browser.all('li').should(
        have._exact_texts_like(
            {...},
            {...},
            'Two',
            {...},
            4,
            "'Five'",
            6,
            {...},  # means exactly one and so does match 1 text
        )
    )

    browser.all('li').should(
        have._exact_texts_like(
            {...},
            {...},
            'Two',
            {...},
            4,
            "'Five'",
            6,
            ...,  # means one or more and so does match 1 text
        )
    )

    browser.all('li').should(
        have.no._exact_texts_like(
            {...},  # means exactly one and does NOT match because of 2 texts (Zero, 1)
            'Two',
            [...],  # means zero or MORE and so does match 2 texts
            "'Five'",
            6,
            '7',
        )
    )

    browser.all('li').should(
        have._exact_texts_like(
            [...],  # means zero or more and so does match 2 texts at start
            'Two',
            {...},
            4,
            "'Five'",
            6,
            '7',
        )
    )

    browser.all('li').should(
        have._exact_texts_like(
            {...},
            {...},
            'Two',
            {...},
            4,
            "'Five'",
            6,
            '7',  # here list ends
            [...],  # means ZERO or more and so does match 0 texts
        )
    )

    browser.all('li').should(
        have._exact_texts_like(
            [...],  # means ZERO or more and so does match 0 texts
            'Zero',  # here list STARTs
            1,
            'Two',
            {...},
            4,
            "'Five'",
            6,
            '7',
        )
    )

    browser.all('li').should(
        have._exact_texts_like(
            {...},
            {...},
            'Two',
            {...},
            4,
            "'Five'",
            [...],  # means ZERO or more and so does match 0 texts
            6,
            '7',
        )
    )

    browser.all('li').should(
        have.no._exact_texts_like(
            {...},  # means exactly one and so does NOT match
            4,
            "'Five'",
            6,
            '7',
            [...],
        )
    )


def test_exact_texts_like__with_default_exactly_one_one_or_more_and_zero_or_more(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>Zero</li>
           <li>1</li>
           <li>Two</li>
           <li>3</li>
           <li>4</li>
           <li>'Five'</li>
           <li>6</li>
           <li>7</li>
        </ul>
        '''
    )

    browser.all('li').should(
        have._exact_texts_like(
            ...,  # means zero or MORE and so does match 2 texts
            'Two',
            [...],
            "'Five'",
            {...},
            '7',
        )
    )

    browser.all('li').should(
        have.no._exact_texts_like(
            ...,
            'Two',
            [...],
            "'Five'",
            {...},
            {...},  # means zero or MORE and so does NOT match this absent text
            '7',
        )
    )

    browser.all('li').should(
        have._exact_texts_like(
            {...},
            {...},
            'Two',
            [...],
            "'Five'",
            '6',
            ...,
        )
    )

    browser.all('li').should(
        have._exact_texts_like(
            [...],
            'Two',
            {...},
            {...},
            "'Five'",
            '6',
            ...,
        )
    )

    browser.all('li').should(
        have._exact_texts_like(
            [...],
            'Two',
            {...},
            {...},
            "'Five'",
            [...],
            '6',
            ...,
        )
    )

    browser.all('li').should(
        have._exact_texts_like(
            [...],
            'Two',
            {...},
            {...},
            "'Five'",
            [...],
            '6',
            7,
            [...],
        )
    )


def test_exact_texts_like__with_default_exactly_one_one_or_more_zero_or_more_zero_or_1(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>Zero</li>
           <li>1</li>
           <li>Two</li>
           <li>3</li>
           <li>4</li>
           <li>'Five'</li>
           <li>6</li>
           <li>7</li>
           <li>8</li>
        </ul>
        '''
    )

    browser.all('li').should(
        have._exact_texts_like(
            [...],
            'Two',
            {...},
            4,
            [{...}],
            "'Five'",
            ...,
            8,
            [...],
        )
    )

    browser.all('li').should(
        have._exact_texts_like(
            [...],
            'Two',
            {...},
            4,
            [{...}],
            6,
            ...,
            8,
            [...],
        )
    )

    browser.all('li').should(
        have.no._exact_texts_like(
            [...],
            'Two',
            {...},
            4,
            [{...}],
            7,
            ...,
            8,
            [...],
        )
    )

    browser.all('li').should(
        have._exact_texts_like(
            [...],
            'Zero',
            1,
            'Two',
            {...},
            4,
            [{...}],
            "'Five'",
            ...,
            8,
            [...],
        )
    )

    browser.all('li').should(
        have._exact_texts_like(
            [{...}],
            'Zero',
            1,
            'Two',
            {...},
            4,
            [...],
            "'Five'",
            ...,
            8,
            [{...}],
        )
    )

    browser.all('li').should(
        have._exact_texts_like(
            [{...}],
            1,
            'Two',
            {...},
            4,
            [...],
            "'Five'",
            ...,
            8,
            [{...}],
        )
    )

    browser.all('li').should(
        have.no._exact_texts_like(
            [{...}],
            'Two',
            {...},
            4,
            [...],
            "'Five'",
            ...,
            8,
            [...],
        )
    )

    browser.all('li').should(
        have._exact_texts_like(
            [{...}],
            1,
            'Two',
            {...},
            4,
            [...],
            "'Five'",
            6,
            7,
            [{...}],
        )
    )

    browser.all('li').should(
        have.no._exact_texts_like(
            [{...}],
            1,
            'Two',
            {...},
            4,
            [...],
            "'Five'",
            6,
            [{...}],
        )
    )


def test_exact_texts_like__with_default_doubled_globs(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>Zero</li>
           <li>1</li>
           <li>Two</li>
           <li>3</li>
           <li>4</li>
           <li>'Five'</li>
           <li>6</li>
           <li>7</li>
           <li>8</li>
        </ul>
        '''
    )

    browser.all('li').should(
        have._exact_texts_like(
            [...],
            'Two',
            {...},
            4,
            [{...}],  # zero
            [{...}],  # or two
            7,
            8,
            [...],
        )
    )

    browser.all('li').should(
        have.no._exact_texts_like(
            [...],
            'Two',
            {...},
            4,
            [{...}],  # zero
            [{...}],  # or two
            8,
            [...],
        )
    )

    browser.all('li').should(
        have._exact_texts_like(
            [...],
            'Two',
            {...},
            4,
            [{...}],  # zero or one
            [{...}],  # or two
            6,
            7,
            8,
            [...],
        )
    )

    browser.all('li').should(
        have._exact_texts_like(
            [...],
            'Two',
            {...},
            4,
            [{...}],  # zero or one
            [{...}],  # or two
            "'Five'",
            6,
            7,
            8,
            [...],
        )
    )

    browser.all('li').should(
        have._exact_texts_like(
            [...],
            'Two',
            {...},
            4,
            {...},  # one
            [{...}],  # or two
            6,
            7,
            8,
            [...],
        )
    )

    browser.all('li').should(
        have.no._exact_texts_like(
            [...],
            'Two',
            {...},
            4,
            {...},  # one
            [{...}],  # or two
            "'Five'",
            6,
            7,
            8,
            [...],
        )
    )

    browser.all('li').should(
        have._exact_texts_like(
            [...],
            'Two',
            {...},
            4,
            {...},  # one
            [{...}],  # or two
            7,
            8,
            [...],
        )
    )

    browser.all('li').should(
        have.no._exact_texts_like(
            [...],
            'Two',
            {...},
            4,
            {...},  # one
            [{...}],  # or two
            8,
            [...],
        )
    )

    browser.all('li').should(
        have._exact_texts_like(
            [...],
            'Two',
            {...},
            4,
            [{...}],  # one
            {...},  # or two
            6,
            7,
            8,
            [...],
        )
    )

    browser.all('li').should(
        have.no._exact_texts_like(
            [...],
            'Two',
            {...},
            4,
            [{...}],  # one
            {...},  # or two
            "'Five'",
            6,
            7,
            8,
            [...],
        )
    )

    browser.all('li').should(
        have._exact_texts_like(
            [...],
            'Two',
            {...},
            4,
            [{...}],  # one
            {...},  # or two
            7,
            8,
            [...],
        )
    )

    browser.all('li').should(
        have.no._exact_texts_like(
            [...],
            'Two',
            {...},
            4,
            [{...}],  # one
            {...},  # or two
            8,
            [...],
        )
    )

    # TODO: cover other "doubled" cases?


def test_exact_texts_like__overrides_original_globs__compared(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>1</li>
           <li>Two</li>
           <li>3</li>
           <li>4</li>
           <li>'Five'</li>
           <li>6</li>
           <li>'7'</li>
        </ul>
        '''
    )

    # no override
    # - pass on have
    browser.all('li').should(
        have._exact_texts_like(..., 'Two', ..., "'Five'", 6, "'7'")
    )
    # - pass on have no (mismatch on wrong placeholder)
    browser.all('li').should(
        have.no._exact_texts_like(..., 'Two', ..., "'Five'", 6, "'7'", (...,))
    )
    # - pass on have no (mismatch on wrong element)
    browser.all('li').should(
        have.no._exact_texts_like(..., 'Two', ..., "'Five'", 6, '7')
    )

    # override via config
    # - pass on have
    browser.with_(_placeholders_to_match_elements=dict(one_or_more=(...,))).all(
        'li'
    ).should(have._exact_texts_like((...,), 'Two', (...,), "'Five'", 6, "'7'"))
    # - pass on have no (mismatch on wrong placeholder)
    browser.with_(_placeholders_to_match_elements=dict(one_or_more=(...,))).all(
        'li'
    ).should(
        have.no._exact_texts_like((...,), 'Two', (...,), "'Five'", 6, "'7'", [...])
    )
    # - pass on have no (mismatch on wrong element)
    browser.with_(_placeholders_to_match_elements=dict(one_or_more=(...,))).all(
        'li'
    ).should(have.no._exact_texts_like((...,), 'Two', (...,), "'Five'", 6, '7'))

    # override via config to empty dict (keeps original defaults)
    # - pass on have
    browser.with_(_placeholders_to_match_elements=dict()).all('li').should(
        have._exact_texts_like(..., 'Two', ..., "'Five'", 6, "'7'")
    )
    # - pass on have no (mismatch on wrong placeholder)
    browser.with_(_placeholders_to_match_elements=dict()).all('li').should(
        have.no._exact_texts_like(..., 'Two', ..., "'Five'", 6, "'7'", (...,))
    )
    # - pass on have no (mismatch on wrong element)
    browser.with_(_placeholders_to_match_elements=dict()).all('li').should(
        have.no._exact_texts_like(..., 'Two', ..., "'Five'", 6, '7')
    )

    # override via where
    # - pass on have
    browser.all('li').should(
        have._exact_texts_like((...,), 'Two', (...,), "'Five'", 6, "'7'").where(
            one_or_more=(...,)
        )
    )
    # - pass on have no (mismatch on wrong placeholder)
    browser.all('li').should(
        have.no._exact_texts_like(
            (...,), 'Two', (...,), "'Five'", 6, "'7'", [...]
        ).where(one_or_more=(...,))
    )
    # - pass on have no (mismatch on wrong element)
    browser.all('li').should(
        have.no._exact_texts_like((...,), 'Two', (...,), "'Five'", 6, '7').where(
            one_or_more=(...,)
        )
    )

    # override via where overrides overridden config
    # - pass on have
    browser.with_(_placeholders_to_match_elements=dict(one_or_more=[...])).all(
        'li'
    ).should(
        have._exact_texts_like((...,), 'Two', (...,), "'Five'", 6, "'7'").where(
            one_or_more=(...,)
        )
    )
    # - pass on have no (mismatch on wrong placeholder)
    browser.with_(_placeholders_to_match_elements=dict(one_or_more=[...])).all(
        'li'
    ).should(
        have.no._exact_texts_like(
            (...,), 'Two', (...,), "'Five'", 6, "'7'", [...]
        ).where(one_or_more=(...,))
    )
    # - pass on have no (mismatch on wrong element)
    browser.with_(_placeholders_to_match_elements=dict(one_or_more=[...])).all(
        'li'
    ).should(
        have.no._exact_texts_like((...,), 'Two', (...,), "'Five'", 6, '7').where(
            one_or_more=(...,)
        )
    )


def test_exact_texts_like__on__mixed_numbers_and_quoted_text__with_default_one_or_more(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>0</li>
           <li>1</li>
           <li>Two</li>
           <li>3</li>
           <li>4</li>
           <li>'Five'</li>
           <li>6</li>
           <li>'7'</li>
        </ul>
        '''
    )

    browser.all('li').should(have._exact_texts_like(..., 'Two', ..., 4, "'Five'", ...))


def test_exact_texts_like__on__mixed_numbers_emtpy_and_quoted_text(session_browser):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>Zero</li>
           <li>1</li>
           <li>Two</li>
           <li></li>
           <li>4</li>
           <li>'Five'</li>
           <li>6</li>
        </ul>
        '''
    )

    browser.all('li').should(have._exact_texts_like(..., 'Two', ..., 4, "'Five'", ...))


def test_exact_texts_like__on__mixed__with_expected_empty_text(session_browser):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>0</li>
           <li>1</li>
           <li>Two</li>
           <li></li>
           <li>4</li>
           <li>'Five'</li>
           <li>6</li>
        </ul>
        '''
    )

    browser.all('li').should(have._exact_texts_like(0, ..., '', ..., "'Five'", ...))


def test_correct_exact_texts_like_exception_message_with_custom_globs(session_browser):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>Zero</li>
           <li></li>
           <li>Two</li>
           <li></li>
           <li>4</li>
           <li>'Five'</li>
           <li>6</li>
        </ul>
        '''
    )

    try:
        browser.all('li').should(have._exact_texts_like(..., 'Two', '', ..., "'Five'"))
        pytest.fail('expected texts mismatch')
    except AssertionError as error:
        assert (
            'Message: \n'
            '\n'
            'Timed out after 0.1s, while waiting for:\n'
            "browser.all(('css selector', 'li')).have exact texts like:\n"
            "    ..., Two, , ..., 'Five'\n"
            '\n'
            'Reason: AssertionError: actual visible texts:\n'
            "    Zero, , Two, , 4, 'Five', 6\n"
            '\n'
            'Pattern used for matching:\n'
            "    ^.+?‚Two‚‹EMTPY_STRING›‚.+?‚'Five'‚$\n"
            'Actual text used to match:\n'
            "    Zero‚‹EMTPY_STRING›‚Two‚‹EMTPY_STRING›‚4‚'Five'‚6‚\n"
            'Screenshot: '
        ) in str(error)


def test_correct_no_exact_texts_like_exception_message__with_custom_globs(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>Zero</li>
           <li></li>
           <li>Two</li>
           <li></li>
           <li>4</li>
           <li>'Five'</li>
           <li>6</li>
        </ul>
        '''
    )

    try:
        browser.all('li').should(
            have.no._exact_texts_like(..., 'Two', '', ..., "'Five'", 6).where(
                one_or_more=...
            )
        )
        pytest.fail('expected texts mismatch')
    except AssertionError as error:
        assert (
            'Message: \n'
            '\n'
            'Timed out after 0.1s, while waiting for:\n'
            "browser.all(('css selector', 'li')).have no exact texts like:\n"
            "    ..., Two, , ..., 'Five', 6\n"
            '\n'
            'Reason: AssertionError: actual visible texts:\n'
            "    Zero, , Two, , 4, 'Five', 6\n"
            '\n'
            'Pattern used for matching:\n'
            "    ^.+?‚Two‚‹EMTPY_STRING›‚.+?‚'Five'‚6‚$\n"
            'Actual text used to match:\n'
            "    Zero‚‹EMTPY_STRING›‚Two‚‹EMTPY_STRING›‚4‚'Five'‚6‚\n"
            'Screenshot: '
        ) in str(error)


def test_correct_no_exact_texts_like_exception_message__with_custom_globs_mixed(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>Zero</li>
           <li></li>
           <li>Two</li>
           <li></li>
           <li>4</li>
           <li>'Five'</li>
           <li>6</li>
           <li>7</li>
           <li>8</li>
        </ul>
        '''
    )

    try:
        browser.all('li').should(
            have._exact_texts_like(
                [{...}],
                1,  # fails here: 1 != empty string
                'Two',
                {...},
                4,
                [...],
                "'Five'",
                ...,
                8,
                [{...}],
            )
        )
        pytest.fail('expected texts mismatch')
    except AssertionError as error:
        assert (
            'Message: \n'
            '\n'
            'Timed out after 0.1s, while waiting for:\n'
            "browser.all(('css selector', 'li')).have exact texts like:\n"
            "    [{...}], 1, Two, {...}, 4, [...]), 'Five', ..., 8, [{...}]\n"
            '\n'
            'Reason: AssertionError: actual visible texts:\n'
            "    Zero, , Two, , 4, 'Five', 6, 7, 8\n"
            '\n'
            'Pattern used for matching:\n'
            "    ^[^‚]*‚?1‚Two‚[^‚]+‚4‚.*?‚?'Five'‚.+?‚8‚[^‚]*‚?$\n"
            'Actual text used to match:\n'
            "    Zero‚‹EMTPY_STRING›‚Two‚‹EMTPY_STRING›‚4‚'Five'‚6‚7‚8‚\n"
            'Screenshot: '
        ) in str(error)


def test_correct_no_exact_texts_like_exception_message__with_default_globs(
    session_browser,
):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>Zero</li>
           <li></li>
           <li>Two</li>
           <li></li>
           <li>4</li>
           <li>'Five'</li>
           <li>6</li>
        </ul>
        '''
    )

    try:
        browser.all('li').should(
            have.no._exact_texts_like(..., 'Two', '', ..., "'Five'", 6)
        )
        pytest.fail('expected texts mismatch')
    except AssertionError as error:
        assert (
            'Message: \n'
            '\n'
            'Timed out after 0.1s, while waiting for:\n'
            "browser.all(('css selector', 'li')).have no exact texts like:\n"
            "    ..., Two, , ..., 'Five', 6\n"
            '\n'
            'Reason: AssertionError: actual visible texts:\n'
            "    Zero, , Two, , 4, 'Five', 6\n"
            '\n'
            'Pattern used for matching:\n'
            "    ^.+?‚Two‚‹EMTPY_STRING›‚.+?‚'Five'‚6‚$\n"
            'Actual text used to match:\n'
            "    Zero‚‹EMTPY_STRING›‚Two‚‹EMTPY_STRING›‚4‚'Five'‚6‚\n"
            'Screenshot: '
        ) in str(error)
