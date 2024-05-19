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

from selene import query
from tests.integration.helpers.givenpage import GivenPage


def test_query_values(session_browser):
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li><input type="text" value="Alex!"></li>
           <li><input type="text" value="  Yakov! \n "</li>
        </ul>
        '''
    )

    assert session_browser.all('input').get(query.values) == [
        'Alex!',
        '  Yakov!   ',
    ]


def test_query_values_after_retyped(session_browser):
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>Hello:
           <li><input type="text" value="Alex!"></li>
           <li><input type="text" value="  Yakov! \n "</li>
        </ul>
        '''
    )

    session_browser.all('input').first.clear().type('  1 \n ')
    session_browser.all('input').second.clear().type('2')

    assert session_browser.all('input').get(query.values) == [
        '  1  ',
        '2',
    ]


# TODO: check query is logged properly
