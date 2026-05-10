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
from tests.integration.helpers.givenpage import GivenPage


def test_collection_by_their_filters_by_inner_element(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_with_body(
        """
        <ul>
          <li class='result'><span class='title'>Selene docs</span><a class='url'>/docs</a></li>
          <li class='result'><span class='title'>Other</span><a class='url'>/other</a></li>
          <li class='result'><span class='title'>Selene examples</span><a class='url'>/examples</a></li>
        </ul>
        """
    )

    session_browser.all('.result').by_their('.title', have.text('Selene')).all(
        '.url'
    ).should(have.exact_texts('/docs', '/examples'))


def test_collection_element_by_its_finds_single_matching_parent(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_with_body(
        """
        <ul>
          <li class='result'><span class='title'>One</span><a class='url'>/one</a></li>
          <li class='result'><span class='title'>Two</span><a class='url'>/two</a></li>
        </ul>
        """
    )

    session_browser.all('.result').element_by_its('.title', have.exact_text('Two')).element(
        '.url'
    ).should(have.exact_text('/two'))


def test_collection_collected_and_all_first_extract_nested_cells(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_with_body(
        """
        <table>
          <tr class='row'><td class='cell'>A1</td><td class='cell'>A2</td></tr>
          <tr class='row'><td class='cell'>B1</td><td class='cell'>B2</td></tr>
        </table>
        """
    )

    rows = session_browser.all('.row')

    rows.collected(lambda row: row.all('.cell')).should(
        have.exact_texts('A1', 'A2', 'B1', 'B2')
    )
    rows.all_first('.cell').should(have.exact_texts('A1', 'B1'))


def test_collection_filtered_by_warns_and_still_works(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_with_body(
        """
        <ul>
          <li class='item active'>a</li>
          <li class='item'>b</li>
          <li class='item active'>c</li>
        </ul>
        """
    )

    with pytest.warns(DeprecationWarning):
        filtered = session_browser.all('.item').filtered_by(have.css_class('active'))

    filtered.should(have.exact_texts('a', 'c'))


def test_collection_slicing_aliases_even_odd_from_to(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_with_body(
        """
        <ul>
          <li class='i'>1</li>
          <li class='i'>2</li>
          <li class='i'>3</li>
          <li class='i'>4</li>
        </ul>
        """
    )

    items = session_browser.all('.i')

    items.even.should(have.exact_texts('2', '4'))
    items.odd.should(have.exact_texts('1', '3'))
    items.from_(1).should(have.exact_texts('2', '3', '4'))
    items.to(2).should(have.exact_texts('1', '2'))
    items.sliced(1, 4, 2).should(have.exact_texts('2', '4'))
