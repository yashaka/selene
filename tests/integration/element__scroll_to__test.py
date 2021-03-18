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
from selene import be, command
from tests.integration.helpers.givenpage import GivenPage


def test_can_scroll_to_element_manually(session_browser):
    session_browser.driver.set_window_size(1000, 100)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <div id="paragraph" style="margin: 400px">
        </div>
        <a id="not-viewable-link" href="#header"/>
        <h1 id="header">Heading 1</h2>
        '''
    )
    element = session_browser.element("#not-viewable-link")

    element.perform(command.js.scroll_into_view)

    element.click()  # we can click even if we did not make the scrolling
    # TODO: find the way to assert that scroll worked!
    assert "header" in session_browser.driver.current_url


def test_can_scroll_to_element_automatically(session_browser):
    session_browser.driver.set_window_size(1000, 100)
    GivenPage(session_browser.driver).opened_with_body(
        '''
        <div id="paragraph" style="margin: 400px">
        </div>
        <a id="not-viewable-link" href="#header"/>
        <h1 id="header">Heading 1</h2>
        '''
    )

    session_browser.element("#not-viewable-link").click()

    assert "header" in session_browser.driver.current_url
