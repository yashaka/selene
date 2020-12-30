# MIT License
#
# Copyright (c) 2015-2020 Iakiv Kramarenko
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
from selene import by
from tests.integration.helpers.givenpage import GivenPage


def test_complex_locator_based_on_by_locators(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_with_body(
            '''
            <div id="container">
                <div>
                    <div>
                        <label>First</label>
                    </div>
                    <div>
                        <a href="#first">go to Heading 1</a>
                    </div>
                </div>
                <div>
                    <div>
                        <label>Second</label>
                    </div>
                    <div>
                        <a href="#second">go to Heading 2</a>
                    </div>
                </div>
            </div>
            <h1 id="first">Heading 1</h2>
            <h2 id="second">Heading 2</h2>
            ''')

    session_browser.element('#container')\
        .element(by.text('Second'))\
        .element(by.be_parent())\
        .element(by.be_following_sibling())\
        .element(by.be_first_child())\
        .click()

    assert ('second' in session_browser.driver.current_url) is True


def test_complex_locator_based_on_selene_element_relative_elements(session_browser):
    page = GivenPage(session_browser.driver)
    page.opened_with_body(
            '''
            <div id="container">
                <div>
                    <div>
                        <label>First</label>
                    </div>
                    <div>
                        <a href="#first">go to Heading 1</a>
                    </div>
                </div>
                <div>
                    <div>
                        <label>Second</label>
                    </div>
                    <div>
                        <a href="#second">go to Heading 2</a>
                    </div>
                </div>
            </div>
            <h1 id="first">Heading 1</h2>
            <h2 id="second">Heading 2</h2>
            ''')

    session_browser.element('#container')\
        .element(by.partial_text('Sec'))\
        .parent_element\
        .following_sibling\
        .first_child\
        .click()
    assert ('second' in session_browser.driver.current_url) is True
