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


def test_should_have_exact_values(session_browser):
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <table>
          <tr class="row">
            <td class="cell"><input value="A1"/></td><td class="cell"><input value="A2"/></td>
          </tr>
          <tr class="row">
            <td class="cell"><input value="B1"/></td><td class="cell"><input value="B2"/></td>
          </tr>
        </table>
        '''
    )

    session_browser.all('.cell input').should(have.values('A1', 'A2', 'B1', 'B2'))

    session_browser.all('.cell input').should(have.values(['A1', 'A2', 'B1', 'B2']))

    session_browser.all('.cell input').should(have.values(('A1', 'A2', 'B1', 'B2')))

    session_browser.all('.cell input').should(
        have.values(
            ('A1', 'A2'),
            ('B1', 'B2'),
        )
    )
