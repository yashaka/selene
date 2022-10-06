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


def test_should_have_exact_texts(session_browser):
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>Alex!</li>
           <li>  Yakov! \n </li>
        </ul>
        '''
    )

    session_browser.all('li').should(have.exact_texts('Alex!', 'Yakov!'))


def test_should_have_exact_texts_does_normalize_inner_spaces(
    session_browser,
):
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>Alex!</li>
           <li>  Yakov    ! \n </li>
        </ul>
        '''
    )

    session_browser.all('li').should(have.exact_texts('Alex!', 'Yakov !'))


def test_should_have_exact_texts_passed_as_collections(session_browser):
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <table>
          <tr class="row">
            <td class="cell">A1</td><td class="cell">A2</td>
          </tr>
          <tr class="row">
            <td class="cell">B1</td><td class="cell">B2</td>
          </tr>
        </table>
        '''
    )

    session_browser.all('.cell').should(
        have.exact_texts('A1', 'A2', 'B1', 'B2')
    )

    session_browser.all('.cell').should(
        have.exact_texts(['A1', 'A2', 'B1', 'B2'])
    )

    session_browser.all('.cell').should(
        have.exact_texts(('A1', 'A2', 'B1', 'B2'))
    )

    session_browser.all('.cell').should(
        have.exact_texts(
            ('A1', 'A2'),
            ('B1', 'B2'),
        )
    )


def test_should_have_exact_texts_exception(session_browser):
    browser = session_browser.with_(timeout=0.1)
    GivenPage(browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li>Alex</li>
           <li> Yakov \n</li>
        </ul>
        '''
    )

    with pytest.raises(TimeoutException) as error:
        browser.all('li').should(have.exact_texts('Alex'))
    assert "has exact texts ('Alex',)" in error.value.msg
    assert (
        "AssertionError: actual visible_texts: ['Alex', 'Yakov']"
        in error.value.msg
    )
