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
from selene import have
from tests.integration.helpers.givenpage import GivenPage


# TODO: consider breaking it down into separate tests


def test_unicode_text_with_trailing_and_leading_spaces(session_browser):
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <ul>Привет:
           <li>  Саше \n </li>
           <li>Яше</li>
           <li>и еще ...</li>
           <li>100</li>
           <li>приветов всем остальним</li>
        </ul>
        '''
    )

    element = session_browser.element('li')

    element.should(have.exact_text('Саше')).should(have.text('Са'))
    session_browser.all('li')[-2].should(have.exact_text(100)).should(have.text(100))
