# MIT License
#
# Copyright (c) 2015-2021 Iakiv Kramarenko
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

from selene import be, have
from tests.integration.helpers.givenpage import GivenPage


def test_should(session_browser):
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <button id="hidden" style="display: none">Press me</button>
        '''
    )

    hidden_element = session_browser.element("#hidden")

    hidden_element.should(be.in_dom).should(be.hidden)


def test_action_on_element_found_from_hidden_element(session_browser):
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <button id="hidden" style="display: none">Press me</button>
        <div>
            <a href="#first">go to Heading 1</a>
            <a href="#second">go to Heading 2</a>
        </div>
        <h1 id="first">Heading 1</h2>
        <h2 id="second">Heading 2</h2>
        '''
    )
    hidden_element = session_browser.element("#hidden")

    hidden_element.element('./following-sibling::*/a[2]').click()

    assert 'second' in session_browser.driver.current_url
